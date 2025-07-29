"""
Tests for Company service operations.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.company_service import CompanyService
from app.schemas.company import CompanyCreate, CompanyUpdate


@pytest.mark.asyncio
async def test_create_company(db_session: AsyncSession):
    """Test creating a new company."""
    company_data = CompanyCreate(
        name="Test Company",
        legal_name="Test Company LLC",
        code="TEST01",
        email="test@company.com",
        currency="USD"
    )
    
    company = await CompanyService.create_company(db_session, company_data)
    
    assert company.id is not None
    assert company.name == "Test Company"
    assert company.legal_name == "Test Company LLC"
    assert company.code == "TEST01"
    assert company.email == "test@company.com"
    assert company.currency == "USD"
    assert company.is_active is True


@pytest.mark.asyncio
async def test_create_company_duplicate_code(db_session: AsyncSession):
    """Test creating a company with duplicate code raises error."""
    company_data = CompanyCreate(
        name="Test Company 1",
        legal_name="Test Company 1 LLC",
        code="DUPLICATE",
        email="test1@company.com"
    )
    
    # Create first company
    await CompanyService.create_company(db_session, company_data)
    
    # Try to create second company with same code
    company_data2 = CompanyCreate(
        name="Test Company 2",
        legal_name="Test Company 2 LLC",
        code="DUPLICATE",
        email="test2@company.com"
    )
    
    with pytest.raises(ValueError) as exc_info:
        await CompanyService.create_company(db_session, company_data2)
    
    assert "already exists" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_company(db_session: AsyncSession):
    """Test retrieving a company by ID."""
    # Create a company first
    company_data = CompanyCreate(
        name="Retrieve Test Company",
        legal_name="Retrieve Test Company LLC",
        code="RETRIEVE01"
    )
    created_company = await CompanyService.create_company(db_session, company_data)
    
    # Retrieve the company
    retrieved_company = await CompanyService.get_company(db_session, created_company.id)
    
    assert retrieved_company is not None
    assert retrieved_company.id == created_company.id
    assert retrieved_company.name == "Retrieve Test Company"
    assert retrieved_company.code == "RETRIEVE01"


@pytest.mark.asyncio
async def test_get_company_by_code(db_session: AsyncSession):
    """Test retrieving a company by code."""
    # Create a company first
    company_data = CompanyCreate(
        name="Code Test Company",
        legal_name="Code Test Company LLC",
        code="CODETEST"
    )
    created_company = await CompanyService.create_company(db_session, company_data)
    
    # Retrieve the company by code
    retrieved_company = await CompanyService.get_company_by_code(db_session, "CODETEST")
    
    assert retrieved_company is not None
    assert retrieved_company.id == created_company.id
    assert retrieved_company.name == "Code Test Company"
    assert retrieved_company.code == "CODETEST"


@pytest.mark.asyncio
async def test_get_company_by_code_case_insensitive(db_session: AsyncSession):
    """Test retrieving a company by code is case insensitive."""
    # Create a company first
    company_data = CompanyCreate(
        name="Case Test Company",
        legal_name="Case Test Company LLC",
        code="CASETEST"
    )
    await CompanyService.create_company(db_session, company_data)
    
    # Retrieve the company by lowercase code
    retrieved_company = await CompanyService.get_company_by_code(db_session, "casetest")
    
    assert retrieved_company is not None
    assert retrieved_company.code == "CASETEST"


@pytest.mark.asyncio
async def test_get_companies_with_search(db_session: AsyncSession):
    """Test retrieving companies with search filtering."""
    # Create test companies
    company1_data = CompanyCreate(
        name="Alpha Corporation",
        legal_name="Alpha Corporation LLC",
        code="ALPHA01"
    )
    company2_data = CompanyCreate(
        name="Beta Industries",
        legal_name="Beta Industries LLC",
        code="BETA01"
    )
    company3_data = CompanyCreate(
        name="Alpha Technologies",
        legal_name="Alpha Technologies LLC",
        code="ALPHATECH"
    )
    
    await CompanyService.create_company(db_session, company1_data)
    await CompanyService.create_company(db_session, company2_data)
    await CompanyService.create_company(db_session, company3_data)
    
    # Search for companies with "Alpha" in name
    companies, total = await CompanyService.get_companies(
        db_session, search="Alpha"
    )
    
    assert total == 2
    assert len(companies) == 2
    company_names = [c.name for c in companies]
    assert "Alpha Corporation" in company_names
    assert "Alpha Technologies" in company_names


@pytest.mark.asyncio
async def test_update_company(db_session: AsyncSession):
    """Test updating a company."""
    # Create a company first
    company_data = CompanyCreate(
        name="Update Test Company",
        legal_name="Update Test Company LLC",
        code="UPDATE01"
    )
    created_company = await CompanyService.create_company(db_session, company_data)
    
    # Update the company
    update_data = CompanyUpdate(
        name="Updated Company Name",
        email="updated@company.com",
        phone="555-1234"
    )
    
    updated_company = await CompanyService.update_company(
        db_session, created_company.id, update_data
    )
    
    assert updated_company is not None
    assert updated_company.name == "Updated Company Name"
    assert updated_company.email == "updated@company.com"
    assert updated_company.phone == "555-1234"
    assert updated_company.legal_name == "Update Test Company LLC"  # Unchanged
    assert updated_company.code == "UPDATE01"  # Unchanged


@pytest.mark.asyncio
async def test_delete_company(db_session: AsyncSession):
    """Test soft deleting a company."""
    # Create a company first
    company_data = CompanyCreate(
        name="Delete Test Company",
        legal_name="Delete Test Company LLC",
        code="DELETE01"
    )
    created_company = await CompanyService.create_company(db_session, company_data)
    
    # Delete the company
    success = await CompanyService.delete_company(db_session, created_company.id)
    assert success is True
    
    # Verify the company is soft deleted
    company = await CompanyService.get_company(db_session, created_company.id)
    assert company is not None
    assert company.is_active is False


@pytest.mark.asyncio
async def test_activate_company(db_session: AsyncSession):
    """Test activating a deactivated company."""
    # Create a company first
    company_data = CompanyCreate(
        name="Activate Test Company",
        legal_name="Activate Test Company LLC",
        code="ACTIVATE01"
    )
    created_company = await CompanyService.create_company(db_session, company_data)
    
    # Delete (deactivate) the company
    await CompanyService.delete_company(db_session, created_company.id)
    
    # Activate the company
    activated_company = await CompanyService.activate_company(db_session, created_company.id)
    
    assert activated_company is not None
    assert activated_company.is_active is True


@pytest.mark.asyncio
async def test_get_companies_pagination(db_session: AsyncSession):
    """Test company pagination."""
    # Create multiple companies
    for i in range(15):
        company_data = CompanyCreate(
            name=f"Pagination Company {i:02d}",
            legal_name=f"Pagination Company {i:02d} LLC",
            code=f"PAGE{i:02d}"
        )
        await CompanyService.create_company(db_session, company_data)
    
    # Test first page
    companies, total = await CompanyService.get_companies(
        db_session, skip=0, limit=10
    )
    
    assert total >= 15  # At least 15 companies
    assert len(companies) == 10
    
    # Test second page
    companies, total = await CompanyService.get_companies(
        db_session, skip=10, limit=10
    )
    
    assert total >= 15
    assert len(companies) >= 5  # At least 5 more companies


@pytest.mark.asyncio
async def test_get_companies_active_only(db_session: AsyncSession):
    """Test filtering companies by active status."""
    # Create two companies
    company1_data = CompanyCreate(
        name="Active Company",
        legal_name="Active Company LLC",
        code="ACTIVE01"
    )
    company2_data = CompanyCreate(
        name="Inactive Company",
        legal_name="Inactive Company LLC",
        code="INACTIVE01"
    )
    
    company1 = await CompanyService.create_company(db_session, company1_data)
    company2 = await CompanyService.create_company(db_session, company2_data)
    
    # Deactivate one company
    await CompanyService.delete_company(db_session, company2.id)
    
    # Get only active companies
    companies, total = await CompanyService.get_companies(
        db_session, active_only=True
    )
    
    company_names = [c.name for c in companies]
    assert "Active Company" in company_names
    assert "Inactive Company" not in company_names