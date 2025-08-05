"""
Test configuration and fixtures for sales module.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import datetime, timedelta

from sales_module.framework.base import Base
from sales_module.models.quote import SalesQuote, SalesQuoteLineItem, QuoteVersion, QuoteApproval


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(engine):
    """Create test database session."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_company_id():
    """Sample company ID for testing."""
    return 1


@pytest.fixture
def sample_customer_id():
    """Sample customer ID for testing."""
    return 100


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing."""
    return 1


@pytest.fixture
def sample_quote_data(sample_company_id, sample_customer_id, sample_user_id):
    """Sample quote data for testing."""
    return {
        "company_id": sample_company_id,
        "quote_number": "QUO-2025-001",
        "title": "Test Quote",
        "description": "Test quote description",
        "customer_id": sample_customer_id,
        "prepared_by_user_id": sample_user_id,
        "valid_until": datetime.utcnow() + timedelta(days=30),
        "subtotal": Decimal("1000.00"),
        "total_amount": Decimal("1080.00"),
        "tax_amount": Decimal("80.00"),
        "currency_code": "USD"
    }


@pytest.fixture
def sample_quote(db_session, sample_quote_data):
    """Create sample quote for testing."""
    quote = SalesQuote(**sample_quote_data)
    db_session.add(quote)
    db_session.commit()
    db_session.refresh(quote)
    return quote


@pytest.fixture
def sample_line_item_data(sample_company_id):
    """Sample line item data for testing."""
    return {
        "company_id": sample_company_id,
        "line_number": 1,
        "item_name": "Test Product",
        "description": "Test product description",
        "quantity": Decimal("2.0"),
        "unit_price": Decimal("500.00"),
        "line_total": Decimal("1000.00")
    }


@pytest.fixture
def sample_line_item(db_session, sample_quote, sample_line_item_data):
    """Create sample line item for testing."""
    line_item_data = sample_line_item_data.copy()
    line_item_data["quote_id"] = sample_quote.id
    line_item = SalesQuoteLineItem(**line_item_data)
    db_session.add(line_item)
    db_session.commit()
    db_session.refresh(line_item)
    return line_item