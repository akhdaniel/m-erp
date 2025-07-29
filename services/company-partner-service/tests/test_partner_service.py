"""
Tests for Partner service operations.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.partner_service import PartnerService
from app.services.company_service import CompanyService
from app.schemas.partner import PartnerCreate, PartnerUpdate
from app.schemas.company import CompanyCreate


@pytest.fixture
async def test_company(db_session: AsyncSession):
    """Create a test company for partner tests."""
    company_data = CompanyCreate(
        name="Test Company",
        legal_name="Test Company LLC",
        code="TESTCO"
    )
    return await CompanyService.create_company(db_session, company_data)


@pytest.mark.asyncio
async def test_create_partner(db_session: AsyncSession, test_company):
    """Test creating a new partner."""
    partner_data = PartnerCreate(
        company_id=test_company.id,
        name="Test Partner",
        code="TESTPART01",
        email="partner@test.com",
        partner_type="customer",
        is_customer=True
    )
    
    partner = await PartnerService.create_partner(db_session, partner_data)
    
    assert partner.id is not None
    assert partner.company_id == test_company.id
    assert partner.name == "Test Partner"
    assert partner.code == "TESTPART01"
    assert partner.email == "partner@test.com"
    assert partner.partner_type == "customer"
    assert partner.is_customer is True
    assert partner.is_active is True


@pytest.mark.asyncio
async def test_create_partner_duplicate_code_same_company(db_session: AsyncSession, test_company):
    """Test creating a partner with duplicate code in same company raises error."""
    partner_data = PartnerCreate(
        company_id=test_company.id,
        name="Test Partner 1",
        code="DUPLICATE",
        partner_type="customer"
    )
    
    # Create first partner
    await PartnerService.create_partner(db_session, partner_data)
    
    # Try to create second partner with same code in same company
    partner_data2 = PartnerCreate(
        company_id=test_company.id,
        name="Test Partner 2",
        code="DUPLICATE",
        partner_type="supplier"
    )
    
    with pytest.raises(ValueError) as exc_info:
        await PartnerService.create_partner(db_session, partner_data2)
    
    assert "already exists for this company" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_partner_same_code_different_company(db_session: AsyncSession):
    """Test creating partners with same code in different companies is allowed."""
    # Create two companies
    company1_data = CompanyCreate(name="Company 1", legal_name="Company 1 LLC", code="COMP1")
    company2_data = CompanyCreate(name="Company 2", legal_name="Company 2 LLC", code="COMP2")
    
    company1 = await CompanyService.create_company(db_session, company1_data)
    company2 = await CompanyService.create_company(db_session, company2_data)
    
    # Create partners with same code in different companies
    partner1_data = PartnerCreate(
        company_id=company1.id,
        name="Partner in Company 1",
        code="SAMECODE",
        partner_type="customer"
    )
    
    partner2_data = PartnerCreate(
        company_id=company2.id,
        name="Partner in Company 2",
        code="SAMECODE",
        partner_type="customer"
    )
    
    partner1 = await PartnerService.create_partner(db_session, partner1_data)
    partner2 = await PartnerService.create_partner(db_session, partner2_data)
    
    assert partner1.code == "SAMECODE"
    assert partner2.code == "SAMECODE"
    assert partner1.company_id != partner2.company_id


@pytest.mark.asyncio
async def test_get_partner(db_session: AsyncSession, test_company):
    """Test retrieving a partner by ID."""
    # Create a partner first
    partner_data = PartnerCreate(
        company_id=test_company.id,
        name="Retrieve Test Partner",
        code="RETRIEVE01",
        partner_type="customer"
    )
    created_partner = await PartnerService.create_partner(db_session, partner_data)
    
    # Retrieve the partner
    retrieved_partner = await PartnerService.get_partner(db_session, created_partner.id)
    
    assert retrieved_partner is not None
    assert retrieved_partner.id == created_partner.id
    assert retrieved_partner.name == "Retrieve Test Partner"
    assert retrieved_partner.code == "RETRIEVE01"


@pytest.mark.asyncio
async def test_get_partner_by_code(db_session: AsyncSession, test_company):
    """Test retrieving a partner by code within a company."""
    # Create a partner first
    partner_data = PartnerCreate(
        company_id=test_company.id,
        name="Code Test Partner",
        code="CODETEST",
        partner_type="supplier"
    )
    created_partner = await PartnerService.create_partner(db_session, partner_data)
    
    # Retrieve the partner by code
    retrieved_partner = await PartnerService.get_partner_by_code(
        db_session, test_company.id, "CODETEST"
    )
    
    assert retrieved_partner is not None
    assert retrieved_partner.id == created_partner.id
    assert retrieved_partner.name == "Code Test Partner"
    assert retrieved_partner.code == "CODETEST"


@pytest.mark.asyncio
async def test_get_partners_by_company(db_session: AsyncSession):
    """Test retrieving all partners for a specific company."""
    # Create two companies
    company1_data = CompanyCreate(name="Company 1", legal_name="Company 1 LLC", code="COMP1")
    company2_data = CompanyCreate(name="Company 2", legal_name="Company 2 LLC", code="COMP2")
    
    company1 = await CompanyService.create_company(db_session, company1_data)
    company2 = await CompanyService.create_company(db_session, company2_data)
    
    # Create partners in both companies
    partner1_data = PartnerCreate(
        company_id=company1.id, name="Partner 1-1", code="P11", partner_type="customer"
    )
    partner2_data = PartnerCreate(
        company_id=company1.id, name="Partner 1-2", code="P12", partner_type="supplier"
    )
    partner3_data = PartnerCreate(
        company_id=company2.id, name="Partner 2-1", code="P21", partner_type="customer"
    )
    
    await PartnerService.create_partner(db_session, partner1_data)
    await PartnerService.create_partner(db_session, partner2_data)
    await PartnerService.create_partner(db_session, partner3_data)
    
    # Get partners for company 1
    company1_partners = await PartnerService.get_partners_by_company(
        db_session, company1.id
    )
    
    assert len(company1_partners) == 2
    partner_names = [p.name for p in company1_partners]
    assert "Partner 1-1" in partner_names
    assert "Partner 1-2" in partner_names


@pytest.mark.asyncio
async def test_get_partners_with_search(db_session: AsyncSession, test_company):
    """Test retrieving partners with search filtering."""
    # Create test partners
    partner1_data = PartnerCreate(
        company_id=test_company.id,
        name="Alpha Corporation",
        code="ALPHA01",
        email="alpha@test.com",
        partner_type="customer"
    )
    partner2_data = PartnerCreate(
        company_id=test_company.id,
        name="Beta Industries",
        code="BETA01",
        email="beta@test.com",
        partner_type="supplier"
    )
    partner3_data = PartnerCreate(
        company_id=test_company.id,
        name="Alpha Technologies",
        code="ALPHATECH",
        email="tech@alpha.com",
        partner_type="customer"
    )
    
    await PartnerService.create_partner(db_session, partner1_data)
    await PartnerService.create_partner(db_session, partner2_data)
    await PartnerService.create_partner(db_session, partner3_data)
    
    # Search for partners with "Alpha" in name
    partners, total = await PartnerService.get_partners(
        db_session, company_id=test_company.id, search="Alpha"
    )
    
    assert total == 2
    assert len(partners) == 2
    partner_names = [p.name for p in partners]
    assert "Alpha Corporation" in partner_names
    assert "Alpha Technologies" in partner_names


@pytest.mark.asyncio
async def test_get_partners_by_type(db_session: AsyncSession, test_company):
    """Test filtering partners by type."""
    # Create partners of different types
    customer_data = PartnerCreate(
        company_id=test_company.id,
        name="Customer Partner",
        code="CUST01",
        partner_type="customer",
        is_customer=True
    )
    supplier_data = PartnerCreate(
        company_id=test_company.id,
        name="Supplier Partner",
        code="SUPP01",
        partner_type="supplier",
        is_supplier=True,
        is_customer=False
    )
    
    await PartnerService.create_partner(db_session, customer_data)
    await PartnerService.create_partner(db_session, supplier_data)
    
    # Get only customers
    customers, total = await PartnerService.get_partners(
        db_session, company_id=test_company.id, partner_type="customer"
    )
    
    assert total == 1
    assert customers[0].name == "Customer Partner"
    assert customers[0].is_customer is True


@pytest.mark.asyncio
async def test_update_partner(db_session: AsyncSession, test_company):
    """Test updating a partner."""
    # Create a partner first
    partner_data = PartnerCreate(
        company_id=test_company.id,
        name="Update Test Partner",
        code="UPDATE01",
        partner_type="customer"
    )
    created_partner = await PartnerService.create_partner(db_session, partner_data)
    
    # Update the partner
    update_data = PartnerUpdate(
        name="Updated Partner Name",
        email="updated@partner.com",
        phone="555-1234",
        is_supplier=True
    )
    
    updated_partner = await PartnerService.update_partner(
        db_session, created_partner.id, update_data
    )
    
    assert updated_partner is not None
    assert updated_partner.name == "Updated Partner Name"
    assert updated_partner.email == "updated@partner.com"
    assert updated_partner.phone == "555-1234"
    assert updated_partner.is_supplier is True
    assert updated_partner.code == "UPDATE01"  # Unchanged


@pytest.mark.asyncio
async def test_delete_partner(db_session: AsyncSession, test_company):
    """Test soft deleting a partner."""
    # Create a partner first
    partner_data = PartnerCreate(
        company_id=test_company.id,
        name="Delete Test Partner",
        code="DELETE01",
        partner_type="customer"
    )
    created_partner = await PartnerService.create_partner(db_session, partner_data)
    
    # Delete the partner
    success = await PartnerService.delete_partner(db_session, created_partner.id)
    assert success is True
    
    # Verify the partner is soft deleted
    partner = await PartnerService.get_partner(db_session, created_partner.id)
    assert partner is not None
    assert partner.is_active is False


@pytest.mark.asyncio
async def test_activate_partner(db_session: AsyncSession, test_company):
    """Test activating a deactivated partner."""
    # Create a partner first
    partner_data = PartnerCreate(
        company_id=test_company.id,
        name="Activate Test Partner",
        code="ACTIVATE01",
        partner_type="customer"
    )
    created_partner = await PartnerService.create_partner(db_session, partner_data)
    
    # Delete (deactivate) the partner
    await PartnerService.delete_partner(db_session, created_partner.id)
    
    # Activate the partner
    activated_partner = await PartnerService.activate_partner(db_session, created_partner.id)
    
    assert activated_partner is not None
    assert activated_partner.is_active is True


@pytest.mark.asyncio
async def test_get_partners_pagination(db_session: AsyncSession, test_company):
    """Test partner pagination."""
    # Create multiple partners
    for i in range(15):
        partner_data = PartnerCreate(
            company_id=test_company.id,
            name=f"Pagination Partner {i:02d}",
            code=f"PAGE{i:02d}",
            partner_type="customer"
        )
        await PartnerService.create_partner(db_session, partner_data)
    
    # Test first page
    partners, total = await PartnerService.get_partners(
        db_session, company_id=test_company.id, skip=0, limit=10
    )
    
    assert total == 15
    assert len(partners) == 10
    
    # Test second page
    partners, total = await PartnerService.get_partners(
        db_session, company_id=test_company.id, skip=10, limit=10
    )
    
    assert total == 15
    assert len(partners) == 5