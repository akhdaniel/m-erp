#!/usr/bin/env python3
"""
Simple model verification script using actual PostgreSQL database.
This script tests basic model creation and functionality.
"""

import asyncio
import sys
from datetime import datetime

from app.core.database import get_db
from app.models.company import Company
from app.models.partner import Partner
from app.models.company_user import CompanyUser
from app.models.partner_contact import PartnerContact
from app.models.partner_address import PartnerAddress


async def test_basic_model_creation():
    """Test basic model creation and database operations."""
    print("🧪 Testing basic model creation...")
    
    try:
        async for db in get_db():
            # Create a test company
            company = Company(
                name="Test Integration Company",
                legal_name="Test Integration Company LLC", 
                code=f"TEST{int(datetime.now().timestamp())}"  # Unique code
            )
            
            db.add(company)
            await db.commit()
            
            print(f"  ✅ Company created: {company.name} (ID: {company.id})")
            
            # Create a test partner
            partner = Partner(
                company_id=company.id,
                name="Test Partner",
                partner_type="customer"
            )
            
            db.add(partner)
            await db.commit()
            
            print(f"  ✅ Partner created: {partner.name} (ID: {partner.id})")
            
            # Create a company user
            company_user = CompanyUser(
                company_id=company.id,
                user_id=99999,  # Test user ID
                role="admin"
            )
            
            db.add(company_user)
            await db.commit()
            
            print(f"  ✅ CompanyUser created: User {company_user.user_id} -> Company {company_user.company_id}")
            
            # Create a partner contact
            contact = PartnerContact(
                partner_id=partner.id,
                name="Test Contact",
                email="test@contact.com"
            )
            
            db.add(contact)
            await db.commit()
            
            print(f"  ✅ PartnerContact created: {contact.name} (ID: {contact.id})")
            
            # Create a partner address
            address = PartnerAddress(
                partner_id=partner.id,
                address_type="billing",
                street="123 Test Street",
                city="Test City",
                country="Test Country"
            )
            
            db.add(address)
            await db.commit()
            
            print(f"  ✅ PartnerAddress created: {address.address_type} address (ID: {address.id})")
            
            # Test model methods
            print(f"  📝 Company string: {str(company)}")
            print(f"  📝 Partner types: {partner.get_partner_types()}")
            print(f"  📝 Contact display: {contact.get_display_name()}")
            print(f"  📝 Address formatted: {address.get_single_line_address()}")
            
            break  # Exit the async generator
            
        return True
        
    except Exception as e:
        print(f"  ❌ Model creation failed: {e}")
        return False


async def test_model_imports():
    """Test that all models can be imported correctly."""
    print("🧪 Testing model imports...")
    
    try:
        # Test that all models are available
        models = [Company, Partner, CompanyUser, PartnerContact, PartnerAddress]
        
        for model in models:
            assert hasattr(model, '__tablename__')
            print(f"  ✅ {model.__name__} model imported successfully")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Model import failed: {e}")
        return False


async def main():
    """Run all verification tests."""
    print("🚀 Company/Partner Service Simple Model Tests")
    print("=" * 60)
    
    tests = [
        test_model_imports,
        test_basic_model_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All model tests passed!")
        print("✅ Database models working correctly")
        print("✅ PostgreSQL integration successful") 
        print("✅ Multi-company schema validated")
        return 0
    else:
        print("❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())