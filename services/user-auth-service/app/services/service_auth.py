"""
Service authentication and token management.
Handles service-to-service authentication and authorization.
"""

import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.service import Service, ServiceToken
from app.services.password_service import PasswordService
from app.services.jwt_service import JWTService


class ServiceAuthService:
    """Service for handling inter-service authentication."""
    
    # Service token expiration time (24 hours)
    SERVICE_TOKEN_EXPIRE_HOURS = 24
    
    # Available service scopes
    AVAILABLE_SCOPES = [
        "read:users",           # Read user information
        "write:users",          # Create/update users
        "read:roles",           # Read role information
        "write:roles",          # Create/update roles
        "read:permissions",     # Read permission information
        "validate:tokens",      # Validate user tokens
        "admin:users",          # Full admin access to users
        "admin:services",       # Manage other services
    ]

    @staticmethod
    def generate_service_secret() -> str:
        """Generate a secure service secret."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_service_secret(secret: str) -> str:
        """Hash a service secret for secure storage."""
        return PasswordService.hash_password(secret)

    @staticmethod
    def verify_service_secret(secret: str, secret_hash: str) -> bool:
        """Verify a service secret against its hash."""
        return PasswordService.verify_password(secret, secret_hash)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a service token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    async def register_service(
        db: AsyncSession,
        service_name: str,
        service_description: str,
        allowed_scopes: List[str]
    ) -> Tuple[Service, str]:
        """
        Register a new service for inter-service authentication.
        
        Returns:
            Tuple of (Service instance, plain text secret)
        """
        # Validate scopes
        invalid_scopes = [scope for scope in allowed_scopes 
                         if scope not in ServiceAuthService.AVAILABLE_SCOPES]
        if invalid_scopes:
            raise ValueError(f"Invalid scopes: {invalid_scopes}")

        # Check if service name already exists
        stmt = select(Service).where(Service.service_name == service_name)
        result = await db.execute(stmt)
        existing_service = result.scalar_one_or_none()
        
        if existing_service:
            raise ValueError(f"Service '{service_name}' already exists")

        # Generate service secret
        service_secret = ServiceAuthService.generate_service_secret()
        secret_hash = ServiceAuthService.hash_service_secret(service_secret)

        # Create service
        service = Service(
            service_name=service_name,
            service_description=service_description,
            service_secret_hash=secret_hash,
            allowed_scopes=allowed_scopes
        )

        db.add(service)
        await db.commit()
        await db.refresh(service)

        return service, service_secret

    @staticmethod
    async def authenticate_service(
        db: AsyncSession,
        service_name: str,
        service_secret: str,
        requested_scopes: Optional[List[str]] = None
    ) -> Tuple[Service, str, List[str]]:
        """
        Authenticate a service and generate access token.
        
        Returns:
            Tuple of (Service instance, access token, granted scopes)
        """
        # Find service
        stmt = select(Service).where(
            and_(
                Service.service_name == service_name,
                Service.is_active == True
            )
        )
        result = await db.execute(stmt)
        service = result.scalar_one_or_none()

        if not service:
            raise ValueError("Service not found or inactive")

        # Verify secret
        if not ServiceAuthService.verify_service_secret(service_secret, service.service_secret_hash):
            raise ValueError("Invalid service secret")

        # Determine granted scopes
        if requested_scopes is None:
            granted_scopes = service.allowed_scopes.copy()
        else:
            # Only grant scopes that are both requested and allowed
            granted_scopes = [scope for scope in requested_scopes 
                            if scope in service.allowed_scopes]

        # Generate service token
        expires_at = datetime.now(timezone.utc) + timedelta(hours=ServiceAuthService.SERVICE_TOKEN_EXPIRE_HOURS)
        
        # Create JWT payload for service
        payload = {
            "service_id": service.id,
            "service_name": service.service_name,
            "scopes": granted_scopes,
            "type": "service_token"
        }
        
        access_token = JWTService.create_service_token(payload, expires_at)

        # Store token hash for tracking/revocation
        token_hash = ServiceAuthService.hash_token(access_token)
        service_token = ServiceToken(
            service_id=service.id,
            token_hash=token_hash,
            scopes=granted_scopes,
            expires_at=expires_at
        )

        db.add(service_token)
        
        # Update service last_used timestamp
        service.update_last_used()
        
        await db.commit()

        return service, access_token, granted_scopes

    @staticmethod
    async def validate_service_token(
        db: AsyncSession,
        token: str,
        required_scopes: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[dict]]:
        """
        Validate a service token and check required scopes.
        
        Returns:
            Tuple of (is_valid, token_payload)
        """
        # Verify JWT token
        payload = JWTService.verify_service_token(token)
        if not payload:
            return False, None

        # Check if it's a service token
        if payload.get("type") != "service_token":
            return False, None

        service_id = payload.get("service_id")
        if not service_id:
            return False, None

        # Check if token is in database and not revoked
        token_hash = ServiceAuthService.hash_token(token)
        stmt = select(ServiceToken).where(
            and_(
                ServiceToken.service_id == service_id,
                ServiceToken.token_hash == token_hash,
                ServiceToken.is_revoked == False
            )
        )
        result = await db.execute(stmt)
        service_token = result.scalar_one_or_none()

        if not service_token or not service_token.is_valid():
            return False, None

        # Check required scopes
        token_scopes = payload.get("scopes", [])
        if required_scopes:
            if not all(scope in token_scopes for scope in required_scopes):
                return False, None

        return True, payload

    @staticmethod
    async def revoke_service_token(
        db: AsyncSession,
        token: str
    ) -> bool:
        """
        Revoke a service token.
        
        Returns:
            True if token was revoked, False if not found
        """
        token_hash = ServiceAuthService.hash_token(token)
        stmt = select(ServiceToken).where(ServiceToken.token_hash == token_hash)
        result = await db.execute(stmt)
        service_token = result.scalar_one_or_none()

        if not service_token:
            return False

        service_token.revoke()
        await db.commit()
        return True

    @staticmethod
    async def revoke_all_service_tokens(
        db: AsyncSession,
        service_id: int
    ) -> int:
        """
        Revoke all tokens for a service.
        
        Returns:
            Number of tokens revoked
        """
        stmt = select(ServiceToken).where(
            and_(
                ServiceToken.service_id == service_id,
                ServiceToken.is_revoked == False
            )
        )
        result = await db.execute(stmt)
        tokens = result.scalars().all()

        revoked_count = 0
        for token in tokens:
            token.revoke()
            revoked_count += 1

        await db.commit()
        return revoked_count

    @staticmethod
    async def get_service_by_id(
        db: AsyncSession,
        service_id: int
    ) -> Optional[Service]:
        """Get service by ID."""
        stmt = select(Service).where(Service.id == service_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_service_by_name(
        db: AsyncSession,
        service_name: str
    ) -> Optional[Service]:
        """Get service by name."""
        stmt = select(Service).where(Service.service_name == service_name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_services(
        db: AsyncSession,
        active_only: bool = True
    ) -> List[Service]:
        """List all registered services."""
        stmt = select(Service)
        if active_only:
            stmt = stmt.where(Service.is_active == True)
        
        stmt = stmt.order_by(Service.created_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_service_status(
        db: AsyncSession,
        service_id: int,
        is_active: bool
    ) -> Optional[Service]:
        """Update service active status."""
        service = await ServiceAuthService.get_service_by_id(db, service_id)
        if not service:
            return None

        service.is_active = is_active
        
        # If deactivating, revoke all tokens
        if not is_active:
            await ServiceAuthService.revoke_all_service_tokens(db, service_id)

        await db.commit()
        await db.refresh(service)
        return service