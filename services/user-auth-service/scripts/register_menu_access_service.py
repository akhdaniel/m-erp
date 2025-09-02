#!/usr/bin/env python3
"""
Script to register the menu-access service with the user-auth-service.
"""

import asyncio
import sys
import os

# Add the user-auth-service to the Python path
sys.path.append('/app')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.service_auth import ServiceAuthService
from app.models.service import Service

async def register_menu_access_service():
    """Register the menu-access service with appropriate scopes."""
    
    # Database setup
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Service details
    service_name = "menu-access-service"
    service_description = "Menu & Access Rights Management Service"
    service_secret = "menu-access-service-secret-key-that-is-long-enough"  # This should match the one in docker-compose
    
    # Define the scopes needed by this service
    allowed_scopes = [
        "validate:tokens",
        "read:users",
        "read:permissions"
    ]
    
    async with async_session() as db:
        try:
            # Check if service already exists
            existing_service = await ServiceAuthService.get_service_by_name(db, service_name)
            
            if existing_service:
                print(f"Service '{service_name}' already exists.")
                print("Updating service secret...")
                
                # Update the service secret
                from app.services.password_service import PasswordService
                secret_hash = PasswordService.hash_password(service_secret)
                existing_service.service_secret_hash = secret_hash
                await db.commit()
                print("Service secret updated successfully.")
            else:
                # Register new service
                print(f"Registering service '{service_name}'...")
                
                # Generate service secret (we'll use our predefined one for consistency)
                from app.services.password_service import PasswordService
                secret_hash = PasswordService.hash_password(service_secret)
                
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
                print(f"Service '{service_name}' registered successfully.")
            
        except Exception as e:
            print(f"Error registering service: {e}")
            await db.rollback()
            return False
    
    print("Service registration completed.")
    return True

if __name__ == "__main__":
    asyncio.run(register_menu_access_service())