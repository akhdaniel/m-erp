"""
Tests for CompanyUser association model.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.models.company import Company
from app.models.company_user import CompanyUser


@pytest.fixture
async def sample_company(test_db_session):
    """Create a sample company for CompanyUser tests."""
    company = Company(
        name="Test Company",
        legal_name="Test Company LLC",
        code="TEST01"
    )
    test_db_session.add(company)
    await test_db_session.commit()
    return company


@pytest.mark.unit
async def test_company_user_creation_basic(test_db_session, sample_company):
    """Test basic CompanyUser creation with required fields."""
    company_user = CompanyUser(
        company_id=sample_company.id,
        user_id=123,  # References user from auth service
        role="user"
    )
    
    test_db_session.add(company_user)
    await test_db_session.commit()
    
    assert company_user.id is not None
    assert company_user.company_id == sample_company.id
    assert company_user.user_id == 123
    assert company_user.role == "user"
    assert company_user.is_default_company is False
    assert company_user.created_at is not None
    assert company_user.updated_at is not None


@pytest.mark.unit
async def test_company_user_creation_with_default(test_db_session, sample_company):
    """Test CompanyUser creation with default company flag."""
    company_user = CompanyUser(
        company_id=sample_company.id,
        user_id=456,
        role="admin",
        is_default_company=True
    )
    
    test_db_session.add(company_user)
    await test_db_session.commit()
    
    assert company_user.role == "admin"
    assert company_user.is_default_company is True


@pytest.mark.unit
async def test_company_user_unique_constraint(test_db_session, sample_company):
    """Test that user can only be associated with company once."""
    # Create first association
    company_user1 = CompanyUser(
        company_id=sample_company.id,
        user_id=789,
        role="user"
    )
    test_db_session.add(company_user1)
    await test_db_session.commit()
    
    # Try to create duplicate association
    company_user2 = CompanyUser(
        company_id=sample_company.id,
        user_id=789,  # Same user_id and company_id
        role="admin"
    )
    test_db_session.add(company_user2)
    
    with pytest.raises(IntegrityError):
        await test_db_session.commit()


@pytest.mark.unit
async def test_company_user_required_fields(test_db_session, sample_company):
    """Test that required fields cannot be None."""
    # Test missing company_id
    with pytest.raises(IntegrityError):
        company_user = CompanyUser(
            user_id=123,
            role="user"
        )
        test_db_session.add(company_user)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing user_id
    with pytest.raises(IntegrityError):
        company_user = CompanyUser(
            company_id=sample_company.id,
            role="user"
        )
        test_db_session.add(company_user)
        await test_db_session.commit()
    
    await test_db_session.rollback()
    
    # Test missing role
    with pytest.raises(IntegrityError):
        company_user = CompanyUser(
            company_id=sample_company.id,
            user_id=123
        )
        test_db_session.add(company_user)
        await test_db_session.commit()


@pytest.mark.unit
async def test_company_user_role_constraint(test_db_session, sample_company):
    """Test that role must be valid value."""
    # Test invalid role
    with pytest.raises(IntegrityError):
        company_user = CompanyUser(
            company_id=sample_company.id,
            user_id=123,
            role="invalid_role"  # Not in allowed values
        )
        test_db_session.add(company_user)
        await test_db_session.commit()


@pytest.mark.unit
async def test_company_user_valid_roles(test_db_session, sample_company):
    """Test all valid role values."""
    valid_roles = ["admin", "manager", "user", "viewer"]
    
    for i, role in enumerate(valid_roles):
        company_user = CompanyUser(
            company_id=sample_company.id,
            user_id=1000 + i,  # Different user_id for each
            role=role
        )
        test_db_session.add(company_user)
    
    await test_db_session.commit()
    
    # Verify all were created successfully
    stmt = select(CompanyUser).where(CompanyUser.company_id == sample_company.id)
    result = await test_db_session.execute(stmt)
    company_users = result.scalars().all()
    
    assert len(company_users) == 4
    created_roles = {cu.role for cu in company_users}
    assert created_roles == set(valid_roles)


@pytest.mark.unit
async def test_company_user_default_values(test_db_session, sample_company):
    """Test that default values are set correctly."""
    company_user = CompanyUser(
        company_id=sample_company.id,
        user_id=999
        # role not specified, should default to "user"
        # is_default_company not specified, should default to False
    )
    
    test_db_session.add(company_user)
    await test_db_session.commit()
    
    assert company_user.role == "user"
    assert company_user.is_default_company is False


@pytest.mark.unit
async def test_company_user_multiple_companies(test_db_session):
    """Test that user can be associated with multiple companies."""
    # Create two companies
    company1 = Company(name="Company 1", legal_name="Company 1 LLC", code="COMP01")
    company2 = Company(name="Company 2", legal_name="Company 2 LLC", code="COMP02")
    test_db_session.add_all([company1, company2])
    await test_db_session.commit()
    
    # Associate same user with both companies
    user_id = 555
    company_user1 = CompanyUser(
        company_id=company1.id,
        user_id=user_id,
        role="admin",
        is_default_company=True
    )
    company_user2 = CompanyUser(
        company_id=company2.id,
        user_id=user_id,
        role="user",
        is_default_company=False
    )
    
    test_db_session.add_all([company_user1, company_user2])
    await test_db_session.commit()
    
    # Verify both associations exist
    stmt = select(CompanyUser).where(CompanyUser.user_id == user_id)
    result = await test_db_session.execute(stmt)
    user_companies = result.scalars().all()
    
    assert len(user_companies) == 2
    company_ids = {cu.company_id for cu in user_companies}
    assert company_ids == {company1.id, company2.id}


@pytest.mark.unit
async def test_company_user_delete_cascade_from_company(test_db_session, sample_company):
    """Test that CompanyUser records are deleted when company is deleted."""
    company_user = CompanyUser(
        company_id=sample_company.id,
        user_id=777,
        role="user"
    )
    test_db_session.add(company_user)
    await test_db_session.commit()
    
    company_user_id = company_user.id
    
    # Delete the company
    await test_db_session.delete(sample_company)
    await test_db_session.commit()
    
    # Verify CompanyUser is also deleted
    stmt = select(CompanyUser).where(CompanyUser.id == company_user_id)
    result = await test_db_session.execute(stmt)
    deleted_company_user = result.scalar_one_or_none()
    
    assert deleted_company_user is None


@pytest.mark.unit
async def test_company_user_query_by_user(test_db_session):
    """Test querying CompanyUser records by user_id."""
    # Create companies and associations
    company1 = Company(name="Company 1", legal_name="Company 1 LLC", code="COMP01")
    company2 = Company(name="Company 2", legal_name="Company 2 LLC", code="COMP02")
    test_db_session.add_all([company1, company2])
    await test_db_session.commit()
    
    user_id = 888
    company_user1 = CompanyUser(company_id=company1.id, user_id=user_id, role="admin")
    company_user2 = CompanyUser(company_id=company2.id, user_id=user_id, role="user")
    
    test_db_session.add_all([company_user1, company_user2])
    await test_db_session.commit()
    
    # Query by user_id
    stmt = select(CompanyUser).where(CompanyUser.user_id == user_id)
    result = await test_db_session.execute(stmt)
    user_companies = result.scalars().all()
    
    assert len(user_companies) == 2


@pytest.mark.unit
async def test_company_user_query_by_company(test_db_session, sample_company):
    """Test querying CompanyUser records by company_id."""
    # Create multiple users for the company
    users = [
        CompanyUser(company_id=sample_company.id, user_id=101, role="admin"),
        CompanyUser(company_id=sample_company.id, user_id=102, role="user"),
        CompanyUser(company_id=sample_company.id, user_id=103, role="viewer")
    ]
    
    test_db_session.add_all(users)
    await test_db_session.commit()
    
    # Query by company_id
    stmt = select(CompanyUser).where(CompanyUser.company_id == sample_company.id)
    result = await test_db_session.execute(stmt)
    company_users = result.scalars().all()
    
    assert len(company_users) == 3
    user_ids = {cu.user_id for cu in company_users}
    assert user_ids == {101, 102, 103}


@pytest.mark.unit
async def test_company_user_default_company_flag(test_db_session):
    """Test querying for user's default company."""
    # Create companies
    company1 = Company(name="Company 1", legal_name="Company 1 LLC", code="COMP01")
    company2 = Company(name="Company 2", legal_name="Company 2 LLC", code="COMP02")
    test_db_session.add_all([company1, company2])
    await test_db_session.commit()
    
    user_id = 999
    company_user1 = CompanyUser(
        company_id=company1.id, 
        user_id=user_id, 
        role="user", 
        is_default_company=False
    )
    company_user2 = CompanyUser(
        company_id=company2.id, 
        user_id=user_id, 
        role="admin", 
        is_default_company=True
    )
    
    test_db_session.add_all([company_user1, company_user2])
    await test_db_session.commit()
    
    # Query for default company
    stmt = select(CompanyUser).where(
        CompanyUser.user_id == user_id,
        CompanyUser.is_default_company == True
    )
    result = await test_db_session.execute(stmt)
    default_company_user = result.scalar_one()
    
    assert default_company_user.company_id == company2.id
    assert default_company_user.role == "admin"


@pytest.mark.unit
async def test_company_user_str_representation(test_db_session, sample_company):
    """Test string representation of CompanyUser model."""
    company_user = CompanyUser(
        company_id=sample_company.id,
        user_id=12345,
        role="manager"
    )
    
    test_db_session.add(company_user)
    await test_db_session.commit()
    
    # Test string representation
    company_user_str = str(company_user)
    assert "12345" in company_user_str
    assert "manager" in company_user_str
    assert str(sample_company.id) in company_user_str