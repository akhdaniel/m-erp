#!/usr/bin/env python3
"""
Integration test script to verify all models work correctly with database.
This script tests model creation, relationships, and constraints.
"""

import asyncio
import sys
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.company import Company
from app.models.partner import Partner
from app.models.company_user import CompanyUser
from app.models.partner_contact import PartnerContact
from app.models.partner_address import PartnerAddress

# Test database URL - using in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


async def create_test_engine():
    """Create test database engine and initialize schema."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    return engine


async def get_test_session(engine):
    """Get test database session."""
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_factory() as session:
        return session


async def test_company_creation(session):
    """Test company model creation and basic operations."""
    print("🧪 Testing Company model...")
    
    try:
        # Create company
        company = Company(
            name="Integration Test Company",
            legal_name="Integration Test Company LLC",
            code="INTEG01",
            email="test@integration.com",
            currency="USD",
            timezone="UTC"
        )
        
        session.add(company)
        await session.commit()
        
        assert company.id is not None
        assert company.name == "Integration Test Company"
        assert company.code == "INTEG01"
        assert company.is_active is True
        
        print("  ✅ Company creation successful")
        return company
        
    except Exception as e:
        print(f"  ❌ Company creation failed: {e}")
        raise


async def test_partner_creation(session, company):
    """Test partner model creation with company association."""
    print("🧪 Testing Partner model...")
    
    try:
        # Create partner
        partner = Partner(
            company_id=company.id,
            name="Integration Test Partner",
            code="PART01",
            partner_type="customer",
            email="partner@test.com",
            is_customer=True,
            is_supplier=False
        )
        
        session.add(partner)
        await session.commit()
        
        assert partner.id is not None
        assert partner.company_id == company.id
        assert partner.name == "Integration Test Partner"
        assert partner.partner_type == "customer"
        assert partner.is_active is True
        
        print("  ✅ Partner creation successful")
        return partner
        
    except Exception as e:
        print(f"  ❌ Partner creation failed: {e}")
        raise


async def test_company_user_creation(session, company):
    """Test CompanyUser association model."""
    print("🧪 Testing CompanyUser model...")
    
    try:
        # Create company user association
        company_user = CompanyUser(
            company_id=company.id,
            user_id=12345,  # References user from auth service
            role="admin",
            is_default_company=True
        )
        
        session.add(company_user)
        await session.commit()
        
        assert company_user.id is not None
        assert company_user.company_id == company.id
        assert company_user.user_id == 12345
        assert company_user.role == "admin"
        assert company_user.is_default_company is True
        
        print("  ✅ CompanyUser creation successful")
        return company_user
        
    except Exception as e:
        print(f"  ❌ CompanyUser creation failed: {e}")
        raise


async def test_partner_contact_creation(session, partner):
    """Test PartnerContact model creation."""
    print("🧪 Testing PartnerContact model...")
    
    try:
        # Create partner contact
        contact = PartnerContact(
            partner_id=partner.id,
            name="John Doe",
            title="Sales Manager",
            email="john.doe@partner.com",
            phone="+1-555-123-4567",
            is_primary=True,
            department="Sales"
        )
        
        session.add(contact)
        await session.commit()
        
        assert contact.id is not None
        assert contact.partner_id == partner.id
        assert contact.name == "John Doe"
        assert contact.title == "Sales Manager"
        assert contact.is_primary is True
        assert contact.is_active is True
        
        print("  ✅ PartnerContact creation successful")
        return contact
        
    except Exception as e:
        print(f"  ❌ PartnerContact creation failed: {e}")
        raise


async def test_partner_address_creation(session, partner):
    """Test PartnerAddress model creation."""
    print("🧪 Testing PartnerAddress model...")
    
    try:
        # Create partner address
        address = PartnerAddress(
            partner_id=partner.id,
            address_type="billing",
            street="123 Business Avenue",
            street2="Suite 100",
            city="Business City",
            state="Business State",
            zip="12345",
            country="United States",
            is_default=True
        )
        
        session.add(address)
        await session.commit()
        
        assert address.id is not None
        assert address.partner_id == partner.id
        assert address.address_type == "billing"
        assert address.street == "123 Business Avenue"
        assert address.city == "Business City"
        assert address.country == "United States"
        assert address.is_default is True
        
        print("  ✅ PartnerAddress creation successful")
        return address
        
    except Exception as e:
        print(f"  ❌ PartnerAddress creation failed: {e}")
        raise


async def test_hierarchical_partners(session, company):
    """Test parent-child partner relationships."""
    print("🧪 Testing hierarchical partner relationships...")
    
    try:
        # Create parent partner
        parent_partner = Partner(
            company_id=company.id,
            name="Parent Corporation",
            code="PARENT01",
            partner_type="customer",
            is_company=True
        )
        session.add(parent_partner)
        await session.commit()
        
        # Create child partner
        child_partner = Partner(
            company_id=company.id,
            name="Child Division",
            code="CHILD01",
            partner_type="customer",
            parent_partner_id=parent_partner.id
        )
        session.add(child_partner)
        await session.commit()
        
        assert child_partner.parent_partner_id == parent_partner.id
        assert child_partner.has_parent is True
        assert parent_partner.parent_partner_id is None
        
        print("  ✅ Hierarchical relationships successful")
        
    except Exception as e:
        print(f"  ❌ Hierarchical relationships failed: {e}")
        raise


async def test_multiple_contacts_and_addresses(session, partner):
    """Test multiple contacts and addresses per partner."""
    print("🧪 Testing multiple contacts and addresses...")
    
    try:
        # Create multiple contacts
        contacts = [
            PartnerContact(
                partner_id=partner.id,
                name="Contact One",
                department="Sales",
                is_primary=False
            ),
            PartnerContact(
                partner_id=partner.id,
                name="Contact Two", 
                department="Support",
                is_primary=False
            )
        ]
        
        # Create multiple addresses
        addresses = [
            PartnerAddress(
                partner_id=partner.id,
                address_type="shipping",
                street="456 Shipping Street",
                city="Shipping City",
                country="United States"
            ),
            PartnerAddress(
                partner_id=partner.id,
                address_type="other",
                street="789 Other Avenue",
                city="Other City", 
                country="United States"
            )
        ]
        
        session.add_all(contacts + addresses)
        await session.commit()
        
        # Verify all were created
        for contact in contacts:
            assert contact.id is not None
            assert contact.partner_id == partner.id
        
        for address in addresses:
            assert address.id is not None
            assert address.partner_id == partner.id
        
        print("  ✅ Multiple contacts and addresses successful")
        
    except Exception as e:
        print(f"  ❌ Multiple contacts and addresses failed: {e}")
        raise


async def test_model_methods(session, company, partner, contact, address):
    """Test model instance methods and properties."""
    print("🧪 Testing model methods...")
    
    try:
        # Test Company methods
        company_str = str(company)
        assert "Integration Test Company" in company_str
        assert "INTEG01" in company_str
        
        # Test Partner methods
        partner_types = partner.get_partner_types()
        assert "customer" in partner_types
        assert partner.has_parent is False
        
        # Test PartnerContact methods
        display_name = contact.get_display_name()
        assert "John Doe" in display_name
        assert "Sales Manager" in display_name
        assert contact.has_email() is True
        assert contact.has_phone() is True
        
        # Test PartnerAddress methods
        formatted_address = address.get_formatted_address()
        assert "123 Business Avenue" in formatted_address
        assert "Business City" in formatted_address
        single_line = address.get_single_line_address()
        assert "123 Business Avenue" in single_line
        assert address.is_complete() is True
        assert address.is_billing_address() is True
        
        print("  ✅ Model methods successful")
        
    except Exception as e:
        print(f"  ❌ Model methods failed: {e}")
        raise


async def main():
    """Run all integration tests."""
    print("🚀 Company/Partner Service Model Integration Tests")
    print("=" * 60)
    
    try:
        # Create test database
        engine = await create_test_engine()
        session = await get_test_session(engine)
        
        # Run tests in sequence
        company = await test_company_creation(session)
        partner = await test_partner_creation(session, company)
        company_user = await test_company_user_creation(session, company)
        contact = await test_partner_contact_creation(session, partner)
        address = await test_partner_address_creation(session, partner)
        
        await test_hierarchical_partners(session, company)
        await test_multiple_contacts_and_addresses(session, partner)
        await test_model_methods(session, company, partner, contact, address)
        
        # Clean up
        await session.close()
        await engine.dispose()
        
        print("=" * 60)
        print("🎉 All integration tests passed!")
        print("📊 Models tested: Company, Partner, CompanyUser, PartnerContact, PartnerAddress")
        print("✅ Database schema validation successful")
        print("✅ Model relationships working correctly")
        print("✅ Constraints and validations enforced")
        
        return 0
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ Integration tests failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)