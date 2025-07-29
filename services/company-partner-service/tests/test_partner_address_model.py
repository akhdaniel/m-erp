"""
Tests for PartnerAddress model.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.company import Company
from app.models.partner import Partner
from app.models.partner_address import PartnerAddress


@pytest.fixture
async def sample_partner(test_db_session):
    """Create a sample company and partner for address tests."""
    company = Company(
        name="Test Company",
        legal_name="Test Company LLC",
        code="TEST01"
    )
    test_db_session.add(company)
    await test_db_session.commit()
    
    partner = Partner(
        company_id=company.id,
        name="Test Partner",
        partner_type="customer"
    )
    test_db_session.add(partner)
    await test_db_session.commit()
    
    return partner


@pytest.mark.unit
async def test_partner_address_creation_basic(test_db_session, sample_partner):
    """Test basic PartnerAddress creation with required fields."""
    address = PartnerAddress(
        partner_id=sample_partner.id,
        street="123 Test Street",
        city="Test City",
        country="United States"
    )
    
    test_db_session.add(address)
    await test_db_session.commit()
    
    assert address.id is not None
    assert address.partner_id == sample_partner.id
    assert address.address_type == "default"
    assert address.street == "123 Test Street"
    assert address.city == "Test City"
    assert address.country == "United States"
    assert address.is_default is False
    assert address.created_at is not None
    assert address.updated_at is not None


@pytest.mark.unit
async def test_partner_address_creation_full_fields(test_db_session, sample_partner):
    """Test PartnerAddress creation with all fields populated."""
    address = PartnerAddress(
        partner_id=sample_partner.id,
        address_type="billing",
        street="456 Business Avenue",
        street2="Suite 100",
        city="Business City",
        state="Business State",
        zip="12345-6789",
        country="United States",
        is_default=True
    )
    
    test_db_session.add(address)
    await test_db_session.commit()
    
    assert address.address_type == "billing"
    assert address.street == "456 Business Avenue"
    assert address.street2 == "Suite 100"
    assert address.city == "Business City"
    assert address.state == "Business State"
    assert address.zip == "12345-6789"
    assert address.country == "United States"
    assert address.is_default is True


@pytest.mark.unit
async def test_partner_address_required_fields(test_db_session, sample_partner):
    """Test that required fields cannot be None."""
    # Test missing partner_id
    with pytest.raises(IntegrityError):
        address = PartnerAddress(
            street="123 Test Street",
            city="Test City",
            country="United States"
        )
        test_db_session.add(address)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing street
    with pytest.raises(IntegrityError):
        address = PartnerAddress(
            partner_id=sample_partner.id,
            city="Test City",
            country="United States"
        )
        test_db_session.add(address)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing city
    with pytest.raises(IntegrityError):
        address = PartnerAddress(
            partner_id=sample_partner.id,
            street="123 Test Street",
            country="United States"
        )
        test_db_session.add(address)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing country
    with pytest.raises(IntegrityError):
        address = PartnerAddress(
            partner_id=sample_partner.id,
            street="123 Test Street",
            city="Test City"
        )
        test_db_session.add(address)
        await test_db_session.commit()


@pytest.mark.unit
async def test_partner_address_type_constraint(test_db_session, sample_partner):
    """Test that address_type must be valid value."""
    # Test invalid address type
    with pytest.raises(IntegrityError):
        address = PartnerAddress(
            partner_id=sample_partner.id,
            address_type="invalid_type",  # Not in allowed values
            street="123 Test Street",
            city="Test City",
            country="United States"
        )
        test_db_session.add(address)
        await test_db_session.commit()


@pytest.mark.unit
async def test_partner_address_valid_types(test_db_session, sample_partner):
    """Test all valid address type values."""
    valid_types = ["default", "billing", "shipping", "other"]
    
    for address_type in valid_types:
        address = PartnerAddress(
            partner_id=sample_partner.id,
            address_type=address_type,
            street=f"123 {address_type.title()} Street",
            city="Test City",
            country="United States"
        )
        test_db_session.add(address)
    
    await test_db_session.commit()
    
    # Verify all were created successfully
    stmt = select(PartnerAddress).where(PartnerAddress.partner_id == sample_partner.id)
    result = await test_db_session.execute(stmt)
    addresses = result.scalars().all()
    
    assert len(addresses) == 4
    created_types = {addr.address_type for addr in addresses}
    assert created_types == set(valid_types)


@pytest.mark.unit
async def test_partner_address_default_values(test_db_session, sample_partner):
    """Test that default values are set correctly."""
    address = PartnerAddress(
        partner_id=sample_partner.id,
        street="123 Default Street",
        city="Default City",
        country="Default Country"
        # address_type not specified, should default to "default"
        # is_default not specified, should default to False
    )
    
    test_db_session.add(address)
    await test_db_session.commit()
    
    assert address.address_type == "default"
    assert address.is_default is False


@pytest.mark.unit
async def test_partner_address_multiple_per_partner(test_db_session, sample_partner):
    """Test that partners can have multiple addresses."""
    addresses = [
        PartnerAddress(
            partner_id=sample_partner.id,
            address_type="billing",
            street="123 Billing Street",
            city="Billing City",
            country="United States",
            is_default=True
        ),
        PartnerAddress(
            partner_id=sample_partner.id,
            address_type="shipping",
            street="456 Shipping Avenue",
            city="Shipping City",
            country="United States"
        ),
        PartnerAddress(
            partner_id=sample_partner.id,
            address_type="other",
            street="789 Other Boulevard",
            city="Other City",
            country="United States"
        )
    ]
    
    test_db_session.add_all(addresses)
    await test_db_session.commit()
    
    # Query addresses for partner
    stmt = select(PartnerAddress).where(PartnerAddress.partner_id == sample_partner.id)
    result = await test_db_session.execute(stmt)
    partner_addresses = result.scalars().all()
    
    assert len(partner_addresses) == 3
    address_types = {addr.address_type for addr in partner_addresses}
    assert address_types == {"billing", "shipping", "other"}


@pytest.mark.unit
async def test_partner_address_delete_cascade_from_partner(test_db_session, sample_partner):
    """Test that addresses are deleted when partner is deleted."""
    address = PartnerAddress(
        partner_id=sample_partner.id,
        street="123 Cascade Street",
        city="Cascade City",
        country="United States"
    )
    test_db_session.add(address)
    await test_db_session.commit()
    
    address_id = address.id
    
    # Delete the partner
    await test_db_session.delete(sample_partner)
    await test_db_session.commit()
    
    # Verify address is also deleted
    stmt = select(PartnerAddress).where(PartnerAddress.id == address_id)
    result = await test_db_session.execute(stmt)
    deleted_address = result.scalar_one_or_none()
    
    assert deleted_address is None


@pytest.mark.unit
async def test_partner_address_default_flag(test_db_session, sample_partner):
    """Test default address functionality."""
    # Create multiple addresses, one default
    default_address = PartnerAddress(
        partner_id=sample_partner.id,
        address_type="default",
        street="123 Default Street",
        city="Default City",
        country="United States",
        is_default=True
    )
    other_address = PartnerAddress(
        partner_id=sample_partner.id,
        address_type="billing",
        street="456 Billing Street",
        city="Billing City",
        country="United States",
        is_default=False
    )
    
    test_db_session.add_all([default_address, other_address])
    await test_db_session.commit()
    
    # Query default address
    stmt = select(PartnerAddress).where(
        PartnerAddress.partner_id == sample_partner.id,
        PartnerAddress.is_default == True
    )
    result = await test_db_session.execute(stmt)
    default = result.scalar_one()
    
    assert default.street == "123 Default Street"
    assert default.address_type == "default"


@pytest.mark.unit
async def test_partner_address_query_by_type(test_db_session, sample_partner):
    """Test querying addresses by type."""
    # Create different types of addresses
    billing_address = PartnerAddress(
        partner_id=sample_partner.id,
        address_type="billing",
        street="123 Billing Street",
        city="Billing City",
        country="United States"
    )
    shipping_address = PartnerAddress(
        partner_id=sample_partner.id,
        address_type="shipping",
        street="456 Shipping Avenue",
        city="Shipping City",
        country="United States"
    )
    
    test_db_session.add_all([billing_address, shipping_address])
    await test_db_session.commit()
    
    # Query billing addresses only
    stmt = select(PartnerAddress).where(
        PartnerAddress.partner_id == sample_partner.id,
        PartnerAddress.address_type == "billing"
    )
    result = await test_db_session.execute(stmt)
    billing_addresses = result.scalars().all()
    
    assert len(billing_addresses) == 1
    assert billing_addresses[0].street == "123 Billing Street"


@pytest.mark.unit
async def test_partner_address_str_representation(test_db_session, sample_partner):
    """Test string representation of PartnerAddress model."""
    address = PartnerAddress(
        partner_id=sample_partner.id,
        address_type="shipping",
        street="123 String Test Street",
        city="String City",
        state="String State",
        country="United States"
    )
    
    test_db_session.add(address)
    await test_db_session.commit()
    
    # Test string representation
    address_str = str(address)
    assert "123 String Test Street" in address_str
    assert "String City" in address_str
    assert "shipping" in address_str