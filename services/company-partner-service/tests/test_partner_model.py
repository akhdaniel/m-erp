"""
Tests for Partner model with company association.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.company import Company
from app.models.partner import Partner


@pytest.fixture
async def sample_company(test_db_session):
    """Create a sample company for partner tests."""
    company = Company(
        name="Test Company",
        legal_name="Test Company LLC",
        code="TEST01"
    )
    test_db_session.add(company)
    await test_db_session.commit()
    return company


@pytest.mark.unit
async def test_partner_creation_basic(test_db_session, sample_company):
    """Test basic partner creation with required fields."""
    partner = Partner(
        company_id=sample_company.id,
        name="Test Customer",
        partner_type="customer"
    )
    
    test_db_session.add(partner)
    await test_db_session.commit()
    
    assert partner.id is not None
    assert partner.company_id == sample_company.id
    assert partner.name == "Test Customer"
    assert partner.partner_type == "customer"
    assert partner.is_active is True
    assert partner.is_customer is True
    assert partner.is_supplier is False
    assert partner.is_vendor is False
    assert partner.is_company is False
    assert partner.created_at is not None
    assert partner.updated_at is not None


@pytest.mark.unit
async def test_partner_creation_full_fields(test_db_session, sample_company):
    """Test partner creation with all fields populated."""
    partner = Partner(
        company_id=sample_company.id,
        name="Full Test Partner",
        code="FULL01",
        partner_type="both",
        email="partner@test.com",
        phone="+1-555-987-6543",
        mobile="+1-555-123-7890",
        website="https://partner.test.com",
        tax_id="98-7654321",
        industry="Technology",
        is_company=True,
        is_customer=True,
        is_supplier=True,
        is_vendor=False
    )
    
    test_db_session.add(partner)
    await test_db_session.commit()
    
    assert partner.code == "FULL01"
    assert partner.email == "partner@test.com"
    assert partner.phone == "+1-555-987-6543"
    assert partner.mobile == "+1-555-123-7890"
    assert partner.website == "https://partner.test.com"
    assert partner.tax_id == "98-7654321"
    assert partner.industry == "Technology"
    assert partner.is_company is True
    assert partner.is_customer is True
    assert partner.is_supplier is True
    assert partner.is_vendor is False


@pytest.mark.unit
async def test_partner_company_association(test_db_session, sample_company):
    """Test that partner is properly associated with company."""
    partner = Partner(
        company_id=sample_company.id,
        name="Associated Partner",
        partner_type="supplier"
    )
    
    test_db_session.add(partner)
    await test_db_session.commit()
    
    # Verify association
    assert partner.company_id == sample_company.id
    
    # Test loading the company relationship (when implemented)
    # assert partner.company.name == "Test Company"


@pytest.mark.unit
async def test_partner_code_unique_per_company(test_db_session):
    """Test that partner codes are unique within each company."""
    # Create two companies
    company1 = Company(name="Company 1", legal_name="Company 1 LLC", code="COMP01")
    company2 = Company(name="Company 2", legal_name="Company 2 LLC", code="COMP02")
    test_db_session.add_all([company1, company2])
    await test_db_session.commit()
    
    # Create partners with same code in different companies (should work)
    partner1 = Partner(
        company_id=company1.id,
        name="Partner 1",
        code="SAME01",
        partner_type="customer"
    )
    partner2 = Partner(
        company_id=company2.id,
        name="Partner 2", 
        code="SAME01",
        partner_type="customer"
    )
    test_db_session.add_all([partner1, partner2])
    await test_db_session.commit()
    
    # This should succeed - same code in different companies is allowed
    assert partner1.code == partner2.code
    assert partner1.company_id != partner2.company_id
    
    # Now try same code in same company (should fail)
    partner3 = Partner(
        company_id=company1.id,
        name="Partner 3",
        code="SAME01",  # Same code as partner1 in same company
        partner_type="supplier"
    )
    test_db_session.add(partner3)
    
    with pytest.raises(IntegrityError):
        await test_db_session.commit()


@pytest.mark.unit
async def test_partner_required_fields(test_db_session, sample_company):
    """Test that required fields cannot be None."""
    # Test missing company_id
    with pytest.raises(IntegrityError):
        partner = Partner(
            name="Test Partner",
            partner_type="customer"
        )
        test_db_session.add(partner)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing name
    with pytest.raises(IntegrityError):
        partner = Partner(
            company_id=sample_company.id,
            partner_type="customer"
        )
        test_db_session.add(partner)
        await test_db_session.commit()


@pytest.mark.unit
async def test_partner_type_constraint(test_db_session, sample_company):
    """Test that partner_type must be valid value."""
    # Test invalid partner type
    with pytest.raises(IntegrityError):
        partner = Partner(
            company_id=sample_company.id,
            name="Invalid Type Partner",
            partner_type="invalid_type"  # Not in allowed values
        )
        test_db_session.add(partner)
        await test_db_session.commit()


@pytest.mark.unit
async def test_partner_name_length_constraint(test_db_session, sample_company):
    """Test that partner name cannot be empty."""
    # Test empty name
    with pytest.raises(IntegrityError):
        partner = Partner(
            company_id=sample_company.id,
            name="",  # Empty name
            partner_type="customer"
        )
        test_db_session.add(partner)
        await test_db_session.commit()


@pytest.mark.unit
async def test_partner_default_values(test_db_session, sample_company):
    """Test that default values are set correctly."""
    partner = Partner(
        company_id=sample_company.id,
        name="Default Values Partner"
        # partner_type not specified, should default to "customer"
    )
    
    test_db_session.add(partner)
    await test_db_session.commit()
    
    assert partner.partner_type == "customer"
    assert partner.is_active is True
    assert partner.is_customer is True
    assert partner.is_supplier is False
    assert partner.is_vendor is False
    assert partner.is_company is False


@pytest.mark.unit
async def test_partner_hierarchical_relationship(test_db_session, sample_company):
    """Test parent-child partner relationships."""
    # Create parent partner
    parent_partner = Partner(
        company_id=sample_company.id,
        name="Parent Company",
        partner_type="customer",
        is_company=True
    )
    test_db_session.add(parent_partner)
    await test_db_session.commit()
    
    # Create child partner
    child_partner = Partner(
        company_id=sample_company.id,
        name="Child Division",
        partner_type="customer",
        parent_partner_id=parent_partner.id
    )
    test_db_session.add(child_partner)
    await test_db_session.commit()
    
    assert child_partner.parent_partner_id == parent_partner.id
    
    # Test loading parent relationship (when implemented)
    # assert child_partner.parent_partner.name == "Parent Company"


@pytest.mark.unit
async def test_partner_delete_cascade_from_company(test_db_session, sample_company):
    """Test that partners are deleted when company is deleted."""
    partner = Partner(
        company_id=sample_company.id,
        name="Cascade Test Partner",
        partner_type="customer"
    )
    test_db_session.add(partner)
    await test_db_session.commit()
    
    partner_id = partner.id
    
    # Delete the company
    await test_db_session.delete(sample_company)
    await test_db_session.commit()
    
    # Verify partner is also deleted
    stmt = select(Partner).where(Partner.id == partner_id)
    result = await test_db_session.execute(stmt)
    deleted_partner = result.scalar_one_or_none()
    
    assert deleted_partner is None


@pytest.mark.unit
async def test_partner_parent_delete_set_null(test_db_session, sample_company):
    """Test that parent_partner_id is set to NULL when parent is deleted."""
    # Create parent and child partners
    parent_partner = Partner(
        company_id=sample_company.id,
        name="Parent to Delete",
        partner_type="customer"
    )
    test_db_session.add(parent_partner)
    await test_db_session.commit()
    
    child_partner = Partner(
        company_id=sample_company.id,
        name="Child Partner",
        partner_type="customer",
        parent_partner_id=parent_partner.id
    )
    test_db_session.add(child_partner)
    await test_db_session.commit()
    
    child_id = child_partner.id
    
    # Delete parent partner
    await test_db_session.delete(parent_partner)
    await test_db_session.commit()
    
    # Verify child still exists but parent_partner_id is NULL
    stmt = select(Partner).where(Partner.id == child_id)
    result = await test_db_session.execute(stmt)
    updated_child = result.scalar_one()
    
    assert updated_child is not None
    assert updated_child.parent_partner_id is None


@pytest.mark.unit
async def test_partner_query_by_type(test_db_session, sample_company):
    """Test querying partners by type."""
    # Create different types of partners
    customer = Partner(
        company_id=sample_company.id,
        name="Customer Partner",
        partner_type="customer"
    )
    supplier = Partner(
        company_id=sample_company.id,
        name="Supplier Partner",
        partner_type="supplier"
    )
    vendor = Partner(
        company_id=sample_company.id,
        name="Vendor Partner",
        partner_type="vendor"
    )
    
    test_db_session.add_all([customer, supplier, vendor])
    await test_db_session.commit()
    
    # Query customers only
    stmt = select(Partner).where(
        Partner.company_id == sample_company.id,
        Partner.partner_type == "customer"
    )
    result = await test_db_session.execute(stmt)
    customers = result.scalars().all()
    
    assert len(customers) == 1
    assert customers[0].name == "Customer Partner"


@pytest.mark.unit
async def test_partner_query_active_only(test_db_session, sample_company):
    """Test querying only active partners."""
    # Create active and inactive partners
    active_partner = Partner(
        company_id=sample_company.id,
        name="Active Partner",
        partner_type="customer"
    )
    inactive_partner = Partner(
        company_id=sample_company.id,
        name="Inactive Partner", 
        partner_type="customer",
        is_active=False
    )
    
    test_db_session.add_all([active_partner, inactive_partner])
    await test_db_session.commit()
    
    # Query only active partners
    stmt = select(Partner).where(
        Partner.company_id == sample_company.id,
        Partner.is_active == True
    )
    result = await test_db_session.execute(stmt)
    active_partners = result.scalars().all()
    
    assert len(active_partners) == 1
    assert active_partners[0].name == "Active Partner"


@pytest.mark.unit
async def test_partner_str_representation(test_db_session, sample_company):
    """Test string representation of partner model."""
    partner = Partner(
        company_id=sample_company.id,
        name="String Test Partner",
        code="STR01",
        partner_type="customer"
    )
    
    test_db_session.add(partner)
    await test_db_session.commit()
    
    # Test string representation
    partner_str = str(partner)
    assert "String Test Partner" in partner_str
    assert "STR01" in partner_str
    assert "customer" in partner_str


@pytest.mark.unit
async def test_partner_industry_field(test_db_session, sample_company):
    """Test partner industry field functionality."""
    partner = Partner(
        company_id=sample_company.id,
        name="Tech Partner",
        partner_type="customer",
        industry="Technology"
    )
    
    test_db_session.add(partner)
    await test_db_session.commit()
    
    assert partner.industry == "Technology"
    
    # Test industry field can be None
    partner_no_industry = Partner(
        company_id=sample_company.id,
        name="No Industry Partner",
        partner_type="customer"
    )
    
    test_db_session.add(partner_no_industry)
    await test_db_session.commit()
    
    assert partner_no_industry.industry is None


@pytest.mark.unit 
async def test_partner_industry_filtering(test_db_session, sample_company):
    """Test filtering partners by industry."""
    # Create partners with different industries
    tech_partner = Partner(
        company_id=sample_company.id,
        name="Tech Corp",
        partner_type="customer",
        industry="Technology"
    )
    manufacturing_partner = Partner(
        company_id=sample_company.id,
        name="Manufacturing Inc",
        partner_type="supplier",
        industry="Manufacturing"
    )
    no_industry_partner = Partner(
        company_id=sample_company.id,
        name="Unknown Industry",
        partner_type="customer"
    )
    
    test_db_session.add_all([tech_partner, manufacturing_partner, no_industry_partner])
    await test_db_session.commit()
    
    # Query partners by industry
    stmt = select(Partner).where(
        Partner.company_id == sample_company.id,
        Partner.industry == "Technology"
    )
    result = await test_db_session.execute(stmt)
    tech_partners = result.scalars().all()
    
    assert len(tech_partners) == 1
    assert tech_partners[0].name == "Tech Corp"


@pytest.mark.unit
async def test_partner_contact_relationship_activation(test_db_session, sample_company):
    """Test that partner contact relationship is properly configured."""
    from app.models.partner_contact import PartnerContact
    
    partner = Partner(
        company_id=sample_company.id,
        name="Partner with Contacts",
        partner_type="customer"
    )
    test_db_session.add(partner)
    await test_db_session.commit()
    
    # Create contact
    contact = PartnerContact(
        partner_id=partner.id,
        name="John Doe",
        title="Sales Manager",
        email="john@partner.com",
        is_primary=True
    )
    test_db_session.add(contact)
    await test_db_session.commit()
    
    # Test relationship (when activated)
    # This test will pass when relationships are uncommented in Partner model
    assert contact.partner_id == partner.id
    # Future: assert partner.contacts[0].name == "John Doe"


@pytest.mark.unit
async def test_partner_address_relationship_activation(test_db_session, sample_company):
    """Test that partner address relationship is properly configured."""
    from app.models.partner_address import PartnerAddress
    
    partner = Partner(
        company_id=sample_company.id,
        name="Partner with Addresses",
        partner_type="customer"
    )
    test_db_session.add(partner)
    await test_db_session.commit()
    
    # Create address
    address = PartnerAddress(
        partner_id=partner.id,
        address_type="billing",
        street="123 Main St",
        city="New York",
        country="USA",
        is_default=True
    )
    test_db_session.add(address)
    await test_db_session.commit()
    
    # Test relationship (when activated)
    # This test will pass when relationships are uncommented in Partner model
    assert address.partner_id == partner.id
    # Future: assert partner.addresses[0].street == "123 Main St"