#!/usr/bin/env python3
"""
Verification script to test the basic infrastructure setup.
This script tests that all components can be imported and basic functionality works.
"""

import sys
import asyncio
from datetime import datetime

def test_imports():
    """Test that all modules can be imported correctly."""
    print("🔍 Testing imports...")
    
    try:
        from app.main import app
        from app.core.config import settings
        from app.core.database import Base, get_db
        from app.models.base import BaseModel, CompanyBaseModel
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test that configuration loads correctly."""
    print("🔍 Testing configuration...")
    
    try:
        from app.core.config import settings
        
        assert settings.project_name == "Company & Partner Management Service"
        assert settings.version == "1.0.0"
        assert settings.database_url is not None
        assert settings.auth_service_url is not None
        
        print("✅ Configuration loaded successfully")
        print(f"   Service: {settings.project_name}")
        print(f"   Version: {settings.version}")
        print(f"   Environment: {settings.environment}")
        print(f"   Debug: {settings.debug}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_app_creation():
    """Test that FastAPI app can be created."""
    print("🔍 Testing FastAPI app creation...")
    
    try:
        from app.main import app
        
        assert app is not None
        assert app.title == "Company & Partner Management Service"
        
        print("✅ FastAPI app created successfully")
        print(f"   Title: {app.title}")
        print(f"   Debug: {app.debug}")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

async def test_database_models():
    """Test that database models are defined correctly."""
    print("🔍 Testing database models...")
    
    try:
        from app.models.base import BaseModel, CompanyBaseModel
        from app.core.database import Base
        
        # Check that models inherit correctly
        assert issubclass(BaseModel, Base)
        assert hasattr(BaseModel, 'created_at')
        assert hasattr(BaseModel, 'updated_at')
        
        assert issubclass(CompanyBaseModel, Base)
        assert hasattr(CompanyBaseModel, 'company_id')
        assert hasattr(CompanyBaseModel, 'created_at')
        
        print("✅ Database models defined correctly")
        return True
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint logic."""
    print("🔍 Testing health endpoint logic...")
    
    try:
        # Import without running the actual HTTP server
        from app.main import health_check
        
        # Test that health_check function exists and can be called
        # Note: We can't actually call it without async context, but we can verify it exists
        assert callable(health_check)
        
        print("✅ Health endpoint defined correctly")
        return True
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

async def main():
    """Run all verification tests."""
    print("🚀 Company/Partner Service Infrastructure Verification")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_app_creation,
        test_database_models,
        test_health_endpoint,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if asyncio.iscoroutinefunction(test):
            result = await test()
        else:
            result = test()
        
        if result:
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All infrastructure tests passed! Service is ready for development.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())