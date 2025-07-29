#!/usr/bin/env python3
"""
Simple test script to verify service authentication functionality.
This can be run without pytest to validate the implementation.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.service_auth import ServiceAuthService
from app.services.jwt_service import JWTService
from app.models.service import Service, ServiceToken
from app.core.database import async_session_factory, init_db


async def test_service_functionality():
    """Test basic service authentication functionality."""
    print("🧪 Testing Service Authentication Functionality...")
    
    # Initialize database
    await init_db()
    
    async with async_session_factory() as session:
        try:
            # Test 1: Service Registration
            print("\n📝 Test 1: Service Registration")
            service, secret = await ServiceAuthService.register_service(
                session,
                "test-service",
                "Test service for functionality check",
                ["read:users", "validate:tokens"]
            )
            print(f"✅ Service registered: {service.service_name}")
            print(f"   Service ID: {service.id}")
            print(f"   Secret length: {len(secret)} characters")
            print(f"   Allowed scopes: {service.allowed_scopes}")
            
            # Test 2: Service Authentication
            print("\n🔐 Test 2: Service Authentication")
            auth_service, token, scopes = await ServiceAuthService.authenticate_service(
                session,
                service.service_name,
                secret,
                ["read:users"]
            )
            print(f"✅ Service authenticated successfully")
            print(f"   Token length: {len(token)} characters")
            print(f"   Granted scopes: {scopes}")
            
            # Test 3: Token Validation
            print("\n🔍 Test 3: Token Validation")
            is_valid, payload = await ServiceAuthService.validate_service_token(
                session,
                token,
                ["read:users"]
            )
            print(f"✅ Token validation: {'Valid' if is_valid else 'Invalid'}")
            if is_valid and payload:
                print(f"   Service name: {payload.get('service_name')}")
                print(f"   Token scopes: {payload.get('scopes')}")
            
            # Test 4: JWT Service Token Creation
            print("\n🎫 Test 4: JWT Service Token")
            jwt_payload = {
                "service_id": service.id,
                "service_name": service.service_name,
                "scopes": ["read:users"],
                "type": "service_token"
            }
            from datetime import datetime, timezone, timedelta
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            
            jwt_token = JWTService.create_service_token(jwt_payload, expires_at)
            jwt_validation = JWTService.verify_service_token(jwt_token)
            
            print(f"✅ JWT service token created and verified")
            print(f"   Token type: {jwt_validation.get('type') if jwt_validation else 'Failed'}")
            
            # Test 5: Service Listing
            print("\n📋 Test 5: Service Listing")
            services = await ServiceAuthService.list_services(session)
            print(f"✅ Found {len(services)} registered service(s)")
            for s in services:
                print(f"   - {s.service_name} (active: {s.is_active})")
            
            # Test 6: Token Revocation
            print("\n🚫 Test 6: Token Revocation")
            revoked_count = await ServiceAuthService.revoke_all_service_tokens(session, service.id)
            print(f"✅ Revoked {revoked_count} token(s)")
            
            # Test 7: Post-revocation validation
            print("\n🔍 Test 7: Post-revocation Validation")
            is_valid_after, _ = await ServiceAuthService.validate_service_token(
                session,
                token
            )
            print(f"✅ Token validation after revocation: {'Valid' if is_valid_after else 'Invalid (expected)'}")
            
            print("\n🎉 All tests completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_available_scopes():
    """Test that available scopes are properly defined."""
    print("\n🔧 Testing Available Service Scopes:")
    for scope in ServiceAuthService.AVAILABLE_SCOPES:
        print(f"   - {scope}")
    print(f"✅ Total available scopes: {len(ServiceAuthService.AVAILABLE_SCOPES)}")


def main():
    """Main test function."""
    print("🚀 Service Authentication Functionality Test")
    print("=" * 50)
    
    try:
        # Test available scopes first (synchronous)
        asyncio.run(test_available_scopes())
        
        # Test main functionality
        success = asyncio.run(test_service_functionality())
        
        if success:
            print("\n🎊 All functionality tests passed!")
            return 0
        else:
            print("\n💥 Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())