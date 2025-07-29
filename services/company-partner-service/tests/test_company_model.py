"""
Tests for Company model validation and constraints.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.company import Company


@pytest.mark.unit
async def test_company_creation_basic(test_db_session):
    """Test basic company creation with required fields."""
    company = Company(
        name="Test Company",
        legal_name="Test Company LLC",
        code="TEST01"
    )
    
    test_db_session.add(company)
    await test_db_session.commit()
    
    assert company.id is not None
    assert company.name == "Test Company"
    assert company.legal_name == "Test Company LLC"
    assert company.code == "TEST01"
    assert company.is_active is True
    assert company.currency == "USD"
    assert company.timezone == "UTC"
    assert company.created_at is not None
    assert company.updated_at is not None


@pytest.mark.unit
async def test_company_creation_full_fields(test_db_session):
    """Test company creation with all fields populated."""
    company = Company(
        name="Full Test Company",
        legal_name="Full Test Company LLC",
        code="FULL01",
        email="info@fulltest.com",
        phone="+1-555-123-4567",
        website="https://fulltest.com",
        tax_id="12-3456789",
        street="123 Business Ave",
        street2="Suite 100",
        city="Business City",
        state="Business State",
        zip="12345",
        country="United States",
        currency="EUR",
        timezone="America/New_York",
        logo_url="https://fulltest.com/logo.png"
    )
    
    test_db_session.add(company)
    await test_db_session.commit()
    
    assert company.id is not None
    assert company.email == "info@fulltest.com"
    assert company.phone == "+1-555-123-4567"
    assert company.website == "https://fulltest.com"
    assert company.tax_id == "12-3456789"
    assert company.street == "123 Business Ave"
    assert company.street2 == "Suite 100"
    assert company.city == "Business City"
    assert company.state == "Business State"
    assert company.zip == "12345"
    assert company.country == "United States"
    assert company.currency == "EUR"
    assert company.timezone == "America/New_York"
    assert company.logo_url == "https://fulltest.com/logo.png"


@pytest.mark.unit
async def test_company_code_uniqueness(test_db_session):
    """Test that company codes must be unique."""
    # Create first company
    company1 = Company(
        name="Company One",
        legal_name="Company One LLC",
        code="UNIQUE01"
    )
    test_db_session.add(company1)
    await test_db_session.commit()
    
    # Try to create second company with same code
    company2 = Company(
        name="Company Two",
        legal_name="Company Two LLC",
        code="UNIQUE01"  # Same code
    )
    test_db_session.add(company2)
    
    with pytest.raises(IntegrityError):
        await test_db_session.commit()


@pytest.mark.unit
async def test_company_required_fields(test_db_session):
    """Test that required fields cannot be None."""
    # Test missing name
    with pytest.raises(IntegrityError):
        company = Company(
            legal_name="Test Company LLC",
            code="TEST01"
        )
        test_db_session.add(company)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing legal_name
    with pytest.raises(IntegrityError):
        company = Company(
            name="Test Company",
            code="TEST01"
        )
        test_db_session.add(company)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing code
    with pytest.raises(IntegrityError):
        company = Company(
            name="Test Company",
            legal_name="Test Company LLC"
        )
        test_db_session.add(company)
        await test_db_session.commit()


@pytest.mark.unit
async def test_company_code_length_constraint(test_db_session):
    """Test that company code must be at least 2 characters."""
    # Test single character code
    with pytest.raises(IntegrityError):
        company = Company(
            name="Test Company",
            legal_name="Test Company LLC",
            code="T"  # Too short
        )
        test_db_session.add(company)
        await test_db_session.commit()


@pytest.mark.unit
async def test_company_name_length_constraint(test_db_session):
    """Test that company name cannot be empty."""
    # Test empty name
    with pytest.raises(IntegrityError):
        company = Company(
            name="",  # Empty name
            legal_name="Test Company LLC",
            code="TEST01"
        )
        test_db_session.add(company)
        await test_db_session.commit()


@pytest.mark.unit
async def test_company_default_values(test_db_session):
    """Test that default values are set correctly."""
    company = Company(
        name="Default Test Company",
        legal_name="Default Test Company LLC",
        code="DEFAULT01"
    )
    
    test_db_session.add(company)
    await test_db_session.commit()
    
    assert company.is_active is True
    assert company.currency == "USD"
    assert company.timezone == "UTC"


@pytest.mark.unit
async def test_company_active_status_toggle(test_db_session):
    """Test toggling company active status."""
    company = Company(
        name="Status Test Company",
        legal_name="Status Test Company LLC",
        code="STATUS01"
    )
    
    test_db_session.add(company)
    await test_db_session.commit()
    
    # Initially active
    assert company.is_active is True
    
    # Deactivate
    company.is_active = False
    await test_db_session.commit()
    
    # Verify deactivated
    stmt = select(Company).where(Company.id == company.id)
    result = await test_db_session.execute(stmt)
    updated_company = result.scalar_one()
    assert updated_company.is_active is False


@pytest.mark.unit
async def test_company_timestamp_updates(test_db_session):
    """Test that updated_at timestamp changes on updates."""
    company = Company(
        name="Timestamp Test Company",
        legal_name="Timestamp Test Company LLC",
        code="TIME01"
    )
    
    test_db_session.add(company)
    await test_db_session.commit()
    
    original_updated_at = company.updated_at
    
    # Update the company
    company.name = "Updated Timestamp Test Company"
    await test_db_session.commit()
    
    # Check that updated_at changed
    assert company.updated_at > original_updated_at


@pytest.mark.unit
async def test_company_query_by_code(test_db_session):
    """Test querying companies by code."""
    company = Company(
        name="Query Test Company",
        legal_name="Query Test Company LLC",
        code="QUERY01"
    )
    
    test_db_session.add(company)
    await test_db_session.commit()
    
    # Query by code
    stmt = select(Company).where(Company.code == "QUERY01")
    result = await test_db_session.execute(stmt)
    found_company = result.scalar_one()
    
    assert found_company.id == company.id
    assert found_company.name == "Query Test Company"


@pytest.mark.unit
async def test_company_query_active_only(test_db_session):
    """Test querying only active companies."""
    # Create active company
    active_company = Company(
        name="Active Company",
        legal_name="Active Company LLC",
        code="ACTIVE01"
    )
    
    # Create inactive company
    inactive_company = Company(
        name="Inactive Company",
        legal_name="Inactive Company LLC",
        code="INACTIVE01",
        is_active=False
    )
    
    test_db_session.add_all([active_company, inactive_company])
    await test_db_session.commit()
    
    # Query only active companies
    stmt = select(Company).where(Company.is_active == True)
    result = await test_db_session.execute(stmt)
    active_companies = result.scalars().all()
    
    assert len(active_companies) == 1
    assert active_companies[0].code == "ACTIVE01"


@pytest.mark.unit
async def test_company_str_representation(test_db_session):
    """Test string representation of company model."""
    company = Company(
        name="String Test Company",
        legal_name="String Test Company LLC",
        code="STRING01"
    )
    
    test_db_session.add(company)
    await test_db_session.commit()
    
    # Test string representation
    company_str = str(company)
    assert "String Test Company" in company_str
    assert "STRING01" in company_str