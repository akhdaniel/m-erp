"""
Tests for PartnerContact model.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.company import Company
from app.models.partner import Partner
from app.models.partner_contact import PartnerContact


@pytest.fixture
async def sample_partner(test_db_session):
    """Create a sample company and partner for contact tests."""
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
async def test_partner_contact_creation_basic(test_db_session, sample_partner):
    """Test basic PartnerContact creation with required fields."""
    contact = PartnerContact(
        partner_id=sample_partner.id,
        name="John Doe"
    )
    
    test_db_session.add(contact)
    await test_db_session.commit()
    
    assert contact.id is not None
    assert contact.partner_id == sample_partner.id
    assert contact.name == "John Doe"
    assert contact.is_primary is False
    assert contact.is_active is True
    assert contact.created_at is not None
    assert contact.updated_at is not None


@pytest.mark.unit
async def test_partner_contact_creation_full_fields(test_db_session, sample_partner):
    """Test PartnerContact creation with all fields populated."""
    contact = PartnerContact(
        partner_id=sample_partner.id,
        name="Jane Smith",
        title="Senior Manager",
        email="jane.smith@partner.com",
        phone="+1-555-123-4567",
        mobile="+1-555-987-6543",
        is_primary=True,
        department="Sales",
        notes="Primary contact for all sales inquiries"
    )
    
    test_db_session.add(contact)
    await test_db_session.commit()
    
    assert contact.title == "Senior Manager"
    assert contact.email == "jane.smith@partner.com"
    assert contact.phone == "+1-555-123-4567"
    assert contact.mobile == "+1-555-987-6543"
    assert contact.is_primary is True
    assert contact.department == "Sales"
    assert contact.notes == "Primary contact for all sales inquiries"


@pytest.mark.unit
async def test_partner_contact_required_fields(test_db_session, sample_partner):
    """Test that required fields cannot be None."""
    # Test missing partner_id
    with pytest.raises(IntegrityError):
        contact = PartnerContact(
            name="Test Contact"
        )
        test_db_session.add(contact)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing name
    with pytest.raises(IntegrityError):
        contact = PartnerContact(
            partner_id=sample_partner.id
        )
        test_db_session.add(contact)
        await test_db_session.commit()


@pytest.mark.unit
async def test_partner_contact_name_length_constraint(test_db_session, sample_partner):
    """Test that contact name cannot be empty."""
    # Test empty name
    with pytest.raises(IntegrityError):
        contact = PartnerContact(
            partner_id=sample_partner.id,
            name=""  # Empty name
        )
        test_db_session.add(contact)
        await test_db_session.commit()


@pytest.mark.unit
async def test_partner_contact_default_values(test_db_session, sample_partner):
    """Test that default values are set correctly."""
    contact = PartnerContact(
        partner_id=sample_partner.id,
        name="Default Test Contact"
    )
    
    test_db_session.add(contact)
    await test_db_session.commit()
    
    assert contact.is_primary is False
    assert contact.is_active is True


@pytest.mark.unit
async def test_partner_contact_multiple_per_partner(test_db_session, sample_partner):
    """Test that partners can have multiple contacts."""
    contacts = [
        PartnerContact(
            partner_id=sample_partner.id,
            name="Contact One",
            department="Sales",
            is_primary=True
        ),
        PartnerContact(
            partner_id=sample_partner.id,
            name="Contact Two",
            department="Support"
        ),
        PartnerContact(
            partner_id=sample_partner.id,
            name="Contact Three",
            department="Billing"
        )
    ]
    
    test_db_session.add_all(contacts)
    await test_db_session.commit()
    
    # Query contacts for partner
    stmt = select(PartnerContact).where(PartnerContact.partner_id == sample_partner.id)
    result = await test_db_session.execute(stmt)
    partner_contacts = result.scalars().all()
    
    assert len(partner_contacts) == 3
    contact_names = {c.name for c in partner_contacts}
    assert contact_names == {"Contact One", "Contact Two", "Contact Three"}


@pytest.mark.unit
async def test_partner_contact_delete_cascade_from_partner(test_db_session, sample_partner):
    """Test that contacts are deleted when partner is deleted."""
    contact = PartnerContact(
        partner_id=sample_partner.id,
        name="Cascade Test Contact"
    )
    test_db_session.add(contact)
    await test_db_session.commit()
    
    contact_id = contact.id
    
    # Delete the partner
    await test_db_session.delete(sample_partner)
    await test_db_session.commit()
    
    # Verify contact is also deleted
    stmt = select(PartnerContact).where(PartnerContact.id == contact_id)
    result = await test_db_session.execute(stmt)
    deleted_contact = result.scalar_one_or_none()
    
    assert deleted_contact is None


@pytest.mark.unit
async def test_partner_contact_primary_flag(test_db_session, sample_partner):
    """Test primary contact functionality."""
    # Create multiple contacts, one primary
    primary_contact = PartnerContact(
        partner_id=sample_partner.id,
        name="Primary Contact",
        is_primary=True
    )
    secondary_contact = PartnerContact(
        partner_id=sample_partner.id,
        name="Secondary Contact",
        is_primary=False
    )
    
    test_db_session.add_all([primary_contact, secondary_contact])
    await test_db_session.commit()
    
    # Query primary contact
    stmt = select(PartnerContact).where(
        PartnerContact.partner_id == sample_partner.id,
        PartnerContact.is_primary == True
    )
    result = await test_db_session.execute(stmt)
    primary = result.scalar_one()
    
    assert primary.name == "Primary Contact"


@pytest.mark.unit
async def test_partner_contact_active_status(test_db_session, sample_partner):
    """Test active/inactive contact filtering."""
    # Create active and inactive contacts
    active_contact = PartnerContact(
        partner_id=sample_partner.id,
        name="Active Contact",
        is_active=True
    )
    inactive_contact = PartnerContact(
        partner_id=sample_partner.id,
        name="Inactive Contact",
        is_active=False
    )
    
    test_db_session.add_all([active_contact, inactive_contact])
    await test_db_session.commit()
    
    # Query only active contacts
    stmt = select(PartnerContact).where(
        PartnerContact.partner_id == sample_partner.id,
        PartnerContact.is_active == True
    )
    result = await test_db_session.execute(stmt)
    active_contacts = result.scalars().all()
    
    assert len(active_contacts) == 1
    assert active_contacts[0].name == "Active Contact"


@pytest.mark.unit
async def test_partner_contact_str_representation(test_db_session, sample_partner):
    """Test string representation of PartnerContact model."""
    contact = PartnerContact(
        partner_id=sample_partner.id,
        name="String Test Contact",
        title="Test Manager",
        email="test@contact.com"
    )
    
    test_db_session.add(contact)
    await test_db_session.commit()
    
    # Test string representation
    contact_str = str(contact)
    assert "String Test Contact" in contact_str
    assert "Test Manager" in contact_str