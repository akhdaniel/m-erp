# Testing Guide for XERPIUM

> **Comprehensive guide to testing strategies, patterns, and tools for XERPIUM services**
>
> Version: 1.0.0  
> Last Updated: August 8, 2025

## 📋 Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Testing Pyramid](#testing-pyramid)
3. [Unit Testing Patterns](#unit-testing-patterns)
4. [Integration Testing](#integration-testing)
5. [API Testing](#api-testing)
6. [Event-Driven Testing](#event-driven-testing)
7. [Multi-Company Testing](#multi-company-testing)
8. [Test Data Management](#test-data-management)
9. [Performance Testing](#performance-testing)
10. [End-to-End Testing](#end-to-end-testing)

## Testing Philosophy

XERPIUM follows a **comprehensive testing strategy** that ensures:

- **Reliability**: All business logic is thoroughly tested
- **Multi-Tenancy**: Company isolation is validated at every level
- **Event Integrity**: Event-driven communication works correctly
- **API Contracts**: REST API behavior is consistent and documented
- **Performance**: Services meet performance requirements
- **Integration**: Services work together seamlessly

### Testing Principles

- **Test First**: Write tests before or alongside implementation
- **Fast Feedback**: Unit tests run quickly and provide immediate feedback
- **Realistic Data**: Use realistic test data that mirrors production
- **Isolated Tests**: Each test is independent and can run in any order
- **Clear Intent**: Test names and structure make intent obvious
- **Comprehensive Coverage**: Critical paths and edge cases are covered

## Testing Pyramid

XERPIUM follows the testing pyramid with appropriate distribution:

```
                    ▲
                 /     \
              /           \
           /                 \
        /                       \
     /        E2E Tests             \    ←  5% (End-to-end scenarios)
   /      (Browser, Full Stack)       \
  /___________________________________  \
 /                                       \
/           Integration Tests             \  ← 25% (Service integration)
\        (API, Database, Events)         /
 \_____________________________________ /
  \                                     /
   \           Unit Tests              /    ← 70% (Business logic)
    \    (Models, Services, Utils)   /
     \_____________________________ /
```

### Test Distribution

| Test Type | Percentage | Purpose | Speed | Scope |
|-----------|------------|---------|--------|-------|
| **Unit Tests** | 70% | Business logic, models, utilities | Very Fast | Single function/class |
| **Integration Tests** | 25% | API endpoints, database, events | Fast | Service boundaries |
| **E2E Tests** | 5% | Complete user workflows | Slow | Full application |

## Unit Testing Patterns

### 1. Testing Framework Setup

**conftest.py**
```python
"""Pytest configuration for XERPIUM services."""

import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.core.database import Base, get_db_session
from app.main import app

# Test Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "poolclass": StaticPool,
    }
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client(db_session):
    """Create FastAPI test client with test database."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()

@pytest.fixture
def sample_company_data():
    """Sample company data for testing."""
    return {
        "name": "Test Company Ltd",
        "code": "TEST001",
        "email": "info@testcompany.com",
        "phone": "+1234567890",
        "address": "123 Test Street",
        "city": "Test City",
        "country": "Test Country",
        "is_active": True
    }

@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "sku": "TEST-PROD-001",
        "description": "A product for testing",
        "list_price": "99.99",
        "cost_price": "75.00",
        "is_active": True,
        "is_sellable": True,
        "track_inventory": True,
        "minimum_stock": 10,
        "maximum_stock": 100
    }

@pytest.fixture
def mock_event_publisher():
    """Mock event publisher to avoid Redis dependency in unit tests."""
    with patch('app.services.product_service.EventPublisher') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    with patch('messaging.config.get_redis_connection') as mock:
        mock_redis = Mock()
        mock.return_value = mock_redis
        yield mock_redis

# Async test support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

### 2. Model Testing

**test_product_models.py**
```python
"""Unit tests for product models."""

import pytest
from decimal import Decimal
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.product import Product, ProductCategory
from app.models.company import Company

class TestProductModel:
    """Test Product model functionality."""
    
    def test_create_product(self, db_session):
        """Test basic product creation."""
        # Create company first (required for CompanyBusinessObject)
        company = Company(
            name="Test Company",
            code="TEST001",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        
        # Create product
        product = Product(
            company_id=company.id,
            name="iPhone 15",
            sku="IPHONE15-128",
            list_price=Decimal("999.99"),
            cost_price=Decimal("800.00")
        )
        
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        # Assertions
        assert product.id is not None
        assert product.company_id == company.id
        assert product.name == "iPhone 15"
        assert product.sku == "IPHONE15-128"
        assert product.list_price == Decimal("999.99")
        assert product.cost_price == Decimal("800.00")
        assert product.created_at is not None
        assert product.updated_at is not None
        assert product.framework_version == "1.0.0"
    
    def test_product_string_representation(self, db_session, sample_company_data):
        """Test product __str__ method."""
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()
        
        product = Product(
            company_id=company.id,
            name="Test Product",
            sku="TEST-001"
        )
        db_session.add(product)
        db_session.commit()
        
        # Test string representation
        assert str(product) == f"Product(id={product.id}, name='Test Product')"
    
    def test_product_margin_calculation(self, db_session, sample_company_data):
        """Test product margin property."""
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()
        
        product = Product(
            company_id=company.id,
            name="Margin Test Product",
            sku="MARGIN-001",
            list_price=Decimal("100.00"),
            cost_price=Decimal("75.00")
        )
        db_session.add(product)
        db_session.commit()
        
        # Test margin calculation
        expected_margin = 25.0  # (100 - 75) / 100 * 100
        assert product.margin_percentage == expected_margin
    
    def test_product_margin_zero_division(self, db_session, sample_company_data):
        """Test margin calculation with zero list price."""
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()
        
        product = Product(
            company_id=company.id,
            name="Zero Price Product",
            sku="ZERO-001",
            list_price=Decimal("0.00"),
            cost_price=Decimal("10.00")
        )
        db_session.add(product)
        db_session.commit()
        
        # Should handle zero division gracefully
        assert product.margin_percentage == 0.0
    
    def test_sku_uniqueness_within_company(self, db_session):
        """Test that SKU must be unique within a company."""
        # Create two companies
        company1 = Company(name="Company 1", code="COMP1", email="comp1@test.com")
        company2 = Company(name="Company 2", code="COMP2", email="comp2@test.com")
        db_session.add_all([company1, company2])
        db_session.commit()
        
        # Create product in company 1
        product1 = Product(
            company_id=company1.id,
            name="Product 1",
            sku="DUPLICATE-SKU"
        )
        db_session.add(product1)
        db_session.commit()
        
        # Same SKU in different company should be allowed
        product2 = Product(
            company_id=company2.id,
            name="Product 2", 
            sku="DUPLICATE-SKU"
        )
        db_session.add(product2)
        db_session.commit()  # Should succeed
        
        # Same SKU in same company should fail
        product3 = Product(
            company_id=company1.id,
            name="Product 3",
            sku="DUPLICATE-SKU"
        )
        db_session.add(product3)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

class TestProductCategoryModel:
    """Test ProductCategory model functionality."""
    
    def test_create_category(self, db_session, sample_company_data):
        """Test category creation."""
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()
        
        category = ProductCategory(
            company_id=company.id,
            name="Electronics",
            description="Electronic products"
        )
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == "Electronics"
        assert category.description == "Electronic products"
        assert category.is_active is True
    
    def test_hierarchical_categories(self, db_session, sample_company_data):
        """Test parent-child category relationships."""
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()
        
        # Create parent category
        parent = ProductCategory(
            company_id=company.id,
            name="Electronics"
        )
        db_session.add(parent)
        db_session.commit()
        
        # Create child category
        child = ProductCategory(
            company_id=company.id,
            name="Smartphones",
            parent_id=parent.id
        )
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)
        
        # Test relationships
        assert child.parent_id == parent.id
        assert child.parent == parent
        assert child in parent.children
    
    def test_category_product_relationship(self, db_session, sample_company_data):
        """Test category-product relationships."""
        company = Company(**sample_company_data)
        db_session.add(company)
        db_session.commit()
        
        # Create category
        category = ProductCategory(
            company_id=company.id,
            name="Test Category"
        )
        db_session.add(category)
        db_session.commit()
        
        # Create products in category
        products = [
            Product(
                company_id=company.id,
                name=f"Product {i}",
                sku=f"PROD-{i}",
                category_id=category.id
            )
            for i in range(3)
        ]
        db_session.add_all(products)
        db_session.commit()
        
        # Test relationships
        assert len(category.products) == 3
        for product in products:
            assert product.category == category
            assert product in category.products
```

### 3. Service Layer Testing

**test_product_service.py**
```python
"""Unit tests for product service layer."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from app.services.product_service import ProductService
from app.models.product import Product, ProductCategory
from app.models.company import Company

class TestProductService:
    """Test ProductService business logic."""
    
    @pytest.fixture
    def product_service(self, db_session):
        """Create ProductService instance with test database."""
        return ProductService(db_session)
    
    @pytest.fixture
    def test_company(self, db_session):
        """Create test company."""
        company = Company(
            name="Test Company",
            code="TEST",
            email="test@company.com"
        )
        db_session.add(company)
        db_session.commit()
        return company
    
    @pytest.fixture
    def test_category(self, db_session, test_company):
        """Create test category."""
        category = ProductCategory(
            company_id=test_company.id,
            name="Test Category"
        )
        db_session.add(category)
        db_session.commit()
        return category
    
    def test_create_product_success(self, product_service, test_company, mock_event_publisher):
        """Test successful product creation."""
        product_data = {
            "name": "Test Product",
            "sku": "TEST-001",
            "list_price": Decimal("99.99"),
            "cost_price": Decimal("75.00")
        }
        
        product = product_service.create_product(product_data, test_company.id)
        
        # Assertions
        assert product.id is not None
        assert product.company_id == test_company.id
        assert product.name == "Test Product"
        assert product.sku == "TEST-001"
        assert product.list_price == Decimal("99.99")
        
        # Verify event was published
        mock_event_publisher.publish_business_event.assert_called_once()
    
    def test_create_product_duplicate_sku(self, product_service, test_company):
        """Test creating product with duplicate SKU fails."""
        product_data = {
            "name": "Product 1",
            "sku": "DUPLICATE"
        }
        
        # Create first product
        product_service.create_product(product_data, test_company.id)
        
        # Attempt to create duplicate
        product_data["name"] = "Product 2"
        with pytest.raises(ValueError, match="already exists"):
            product_service.create_product(product_data, test_company.id)
    
    def test_get_product_by_id(self, product_service, test_company):
        """Test retrieving product by ID."""
        # Create product
        product = product_service.create_product({
            "name": "Find Me",
            "sku": "FIND-001"
        }, test_company.id)
        
        # Retrieve product
        found_product = product_service.get_product_by_id(product.id, test_company.id)
        
        assert found_product is not None
        assert found_product.id == product.id
        assert found_product.name == "Find Me"
    
    def test_get_product_wrong_company(self, product_service, db_session):
        """Test that products are isolated by company."""
        # Create two companies
        company1 = Company(name="Company 1", code="COMP1", email="c1@test.com")
        company2 = Company(name="Company 2", code="COMP2", email="c2@test.com")
        db_session.add_all([company1, company2])
        db_session.commit()
        
        # Create product in company 1
        product = product_service.create_product({
            "name": "Company 1 Product",
            "sku": "C1-PROD"
        }, company1.id)
        
        # Try to access from company 2
        found_product = product_service.get_product_by_id(product.id, company2.id)
        
        assert found_product is None  # Should not be accessible
    
    def test_update_product(self, product_service, test_company, mock_event_publisher):
        """Test product updates."""
        # Create product
        product = product_service.create_product({
            "name": "Original Name",
            "sku": "UPDATE-001",
            "list_price": Decimal("100.00")
        }, test_company.id)
        
        # Reset mock to ignore creation event
        mock_event_publisher.reset_mock()
        
        # Update product
        update_data = {
            "name": "Updated Name",
            "list_price": Decimal("150.00")
        }
        
        updated_product = product_service.update_product(
            product.id, update_data, test_company.id
        )
        
        # Assertions
        assert updated_product.name == "Updated Name"
        assert updated_product.list_price == Decimal("150.00")
        assert updated_product.sku == "UPDATE-001"  # Unchanged
        
        # Verify update event was published
        mock_event_publisher.publish_business_event.assert_called_once()
    
    def test_calculate_margin(self, product_service, test_company):
        """Test margin calculation business logic."""
        # Create product with known margins
        product = product_service.create_product({
            "name": "Margin Test",
            "sku": "MARGIN-001", 
            "list_price": Decimal("200.00"),
            "cost_price": Decimal("150.00")
        }, test_company.id)
        
        # Calculate margin
        margin_data = product_service.calculate_margin(product.id, test_company.id)
        
        # Assertions
        assert margin_data["product_id"] == product.id
        assert margin_data["list_price"] == Decimal("200.00")
        assert margin_data["cost_price"] == Decimal("150.00")
        assert margin_data["margin_amount"] == Decimal("50.00")
        assert margin_data["margin_percentage"] == 25.0
    
    def test_get_products_with_filters(self, product_service, test_company, test_category):
        """Test product filtering and search."""
        # Create test products
        products = [
            Product(
                company_id=test_company.id,
                name="Active Product",
                sku="ACTIVE-001",
                category_id=test_category.id,
                is_active=True
            ),
            Product(
                company_id=test_company.id,
                name="Inactive Product",
                sku="INACTIVE-001",
                is_active=False
            ),
            Product(
                company_id=test_company.id,
                name="Special Widget",
                sku="WIDGET-001",
                is_active=True
            )
        ]
        
        product_service.db.add_all(products)
        product_service.db.commit()
        
        # Test active only filter
        active_products = product_service.get_products(
            test_company.id, 
            active_only=True
        )
        assert len(active_products) == 2
        assert all(p.is_active for p in active_products)
        
        # Test category filter
        category_products = product_service.get_products(
            test_company.id,
            category_id=test_category.id
        )
        assert len(category_products) == 1
        assert category_products[0].name == "Active Product"
        
        # Test search
        search_results = product_service.get_products(
            test_company.id,
            search_term="Widget"
        )
        assert len(search_results) == 1
        assert search_results[0].name == "Special Widget"
    
    def test_bulk_price_update(self, product_service, test_company):
        """Test bulk price update operation."""
        # Create test products
        products = []
        for i in range(3):
            product = product_service.create_product({
                "name": f"Bulk Product {i}",
                "sku": f"BULK-{i:03d}",
                "list_price": Decimal("100.00")
            }, test_company.id)
            products.append(product)
        
        # Prepare bulk update
        price_updates = [
            {"product_id": products[0].id, "list_price": "120.00"},
            {"product_id": products[1].id, "list_price": "130.00"},
            {"product_id": 99999, "list_price": "140.00"},  # Non-existent
        ]
        
        # Execute bulk update
        result = product_service.bulk_update_prices(price_updates, test_company.id)
        
        # Assertions
        assert result["updated_count"] == 2
        assert result["total_attempted"] == 3
        assert len(result["errors"]) == 1
        assert "99999" in result["errors"][0]
        
        # Verify prices were updated
        updated_product_0 = product_service.get_product_by_id(products[0].id, test_company.id)
        assert updated_product_0.list_price == Decimal("120.00")
    
    @patch('app.services.product_service.EventPublisher')
    def test_event_publishing_failure_handling(self, mock_publisher_class, product_service, test_company):
        """Test that event publishing failures don't break business operations."""
        # Configure mock to raise exception
        mock_publisher = mock_publisher_class.return_value
        mock_publisher.publish_business_event.side_effect = Exception("Redis connection failed")
        
        # Create product (should succeed despite event failure)
        product = product_service.create_product({
            "name": "Event Fail Test",
            "sku": "EVENT-FAIL-001"
        }, test_company.id)
        
        # Product should still be created
        assert product.id is not None
        assert product.name == "Event Fail Test"
        
        # Event publisher should have been called (and failed)
        mock_publisher.publish_business_event.assert_called_once()
```

## Integration Testing

### 1. Database Integration Tests

**test_product_integration.py**
```python
"""Integration tests for product service with real database operations."""

import pytest
from decimal import Decimal
from sqlalchemy import text

from app.services.product_service import ProductService
from app.models.product import Product, ProductCategory
from app.models.company import Company

class TestProductDatabaseIntegration:
    """Test product service with real database operations."""
    
    @pytest.fixture
    def product_service(self, db_session):
        """Product service with real database session."""
        return ProductService(db_session)
    
    def test_complex_product_queries(self, product_service, db_session):
        """Test complex database queries and relationships."""
        # Create test data
        company = Company(name="Integration Test Co", code="INTEG", email="int@test.com")
        db_session.add(company)
        db_session.commit()
        
        # Create categories hierarchy
        parent_category = ProductCategory(
            company_id=company.id,
            name="Electronics"
        )
        child_category = ProductCategory(
            company_id=company.id,
            name="Smartphones",
            parent_id=parent_category.id
        )
        db_session.add_all([parent_category, child_category])
        db_session.commit()
        
        # Create products
        products = []
        for i in range(5):
            product = Product(
                company_id=company.id,
                name=f"Phone {i}",
                sku=f"PHONE-{i:03d}",
                list_price=Decimal(f"{500 + i * 100}.00"),
                cost_price=Decimal(f"{400 + i * 80}.00"),
                category_id=child_category.id,
                is_active=i < 4  # Last one inactive
            )
            products.append(product)
        
        db_session.add_all(products)
        db_session.commit()
        
        # Test various queries
        
        # 1. Active products only
        active_products = product_service.get_products(company.id, active_only=True)
        assert len(active_products) == 4
        
        # 2. Products by category
        category_products = product_service.get_products(
            company.id, 
            category_id=child_category.id
        )
        assert len(category_products) == 4  # active only by default
        
        # 3. Search functionality
        search_results = product_service.get_products(
            company.id,
            search_term="Phone 2"
        )
        assert len(search_results) == 1
        assert search_results[0].name == "Phone 2"
        
        # 4. Complex filter combinations
        results = product_service.get_products(
            company.id,
            category_id=child_category.id,
            active_only=False,
            search_term="Phone"
        )
        assert len(results) == 5  # All phones including inactive
    
    def test_transaction_rollback(self, product_service, db_session):
        """Test that failed operations rollback properly."""
        company = Company(name="Rollback Test", code="ROLL", email="roll@test.com")
        db_session.add(company)
        db_session.commit()
        
        # Create first product successfully
        product1 = product_service.create_product({
            "name": "Product 1",
            "sku": "ROLLBACK-001"
        }, company.id)
        
        # Verify it exists
        assert product_service.get_product_by_id(product1.id, company.id) is not None
        
        # Attempt to create product with duplicate SKU (should fail)
        try:
            product_service.create_product({
                "name": "Product 2",
                "sku": "ROLLBACK-001"  # Duplicate SKU
            }, company.id)
        except ValueError:
            pass  # Expected
        
        # Verify first product still exists and database is consistent
        existing_product = product_service.get_product_by_id(product1.id, company.id)
        assert existing_product is not None
        assert existing_product.name == "Product 1"
        
        # Verify no partial data
        all_products = product_service.get_products(company.id)
        assert len(all_products) == 1
    
    def test_concurrent_access_simulation(self, db_session):
        """Test concurrent access patterns (simulated)."""
        # Create test company
        company = Company(name="Concurrent Test", code="CONC", email="conc@test.com")
        db_session.add(company)
        db_session.commit()
        
        # Simulate concurrent services
        service1 = ProductService(db_session)
        service2 = ProductService(db_session)
        
        # Service 1 creates a product
        product1 = service1.create_product({
            "name": "Concurrent Product 1",
            "sku": "CONC-001"
        }, company.id)
        
        # Service 2 should be able to read it
        product1_from_service2 = service2.get_product_by_id(product1.id, company.id)
        assert product1_from_service2 is not None
        assert product1_from_service2.name == "Concurrent Product 1"
        
        # Service 2 updates the product
        updated_product = service2.update_product(
            product1.id,
            {"name": "Updated by Service 2"},
            company.id
        )
        
        # Service 1 should see the update
        refreshed_product = service1.get_product_by_id(product1.id, company.id)
        assert refreshed_product.name == "Updated by Service 2"
    
    def test_database_constraints(self, db_session):
        """Test database-level constraints are enforced."""
        service = ProductService(db_session)
        
        # Test company isolation constraint
        company1 = Company(name="Company 1", code="COMP1", email="c1@test.com")
        company2 = Company(name="Company 2", code="COMP2", email="c2@test.com")
        db_session.add_all([company1, company2])
        db_session.commit()
        
        # Create product in company 1
        product = service.create_product({
            "name": "Constraint Test",
            "sku": "CONSTRAINT-001"
        }, company1.id)
        
        # Verify direct SQL query respects company isolation
        result = db_session.execute(
            text("SELECT COUNT(*) FROM products WHERE company_id = :company_id"),
            {"company_id": company1.id}
        ).scalar()
        assert result == 1
        
        result = db_session.execute(
            text("SELECT COUNT(*) FROM products WHERE company_id = :company_id"),
            {"company_id": company2.id}
        ).scalar()
        assert result == 0
    
    def test_performance_bulk_operations(self, product_service, db_session):
        """Test performance of bulk operations."""
        import time
        
        company = Company(name="Performance Test", code="PERF", email="perf@test.com")
        db_session.add(company)
        db_session.commit()
        
        # Bulk create products
        start_time = time.time()
        products = []
        
        for i in range(100):
            product = product_service.create_product({
                "name": f"Bulk Product {i}",
                "sku": f"BULK-{i:03d}",
                "list_price": Decimal("10.00")
            }, company.id)
            products.append(product)
        
        creation_time = time.time() - start_time
        
        # Should complete reasonably quickly
        assert creation_time < 5.0  # 5 seconds for 100 products
        
        # Bulk query performance
        start_time = time.time()
        all_products = product_service.get_products(company.id)
        query_time = time.time() - start_time
        
        assert len(all_products) == 100
        assert query_time < 0.5  # 500ms for query
```

## API Testing

### 1. FastAPI Endpoint Testing

**test_product_api.py**
```python
"""API integration tests for product endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

class TestProductAPI:
    """Test Product API endpoints."""
    
    @pytest.fixture
    def authenticated_headers(self):
        """Mock authenticated headers."""
        return {"Authorization": "Bearer mock-jwt-token"}
    
    @pytest.fixture
    def mock_company_context(self):
        """Mock company context dependency."""
        with patch('app.routers.products.get_company_context') as mock:
            mock.return_value = type('CompanyContext', (), {'company_id': 1, 'user_id': 1})()
            yield mock
    
    def test_create_product_success(self, test_client, authenticated_headers, mock_company_context):
        """Test successful product creation via API."""
        product_data = {
            "name": "API Test Product",
            "sku": "API-001",
            "list_price": "99.99",
            "cost_price": "75.00",
            "description": "Created via API test"
        }
        
        response = test_client.post(
            "/api/v1/products/",
            json=product_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == 201
        
        response_data = response.json()
        assert response_data["name"] == product_data["name"]
        assert response_data["sku"] == product_data["sku"]
        assert response_data["id"] is not None
        assert response_data["company_id"] == 1
        assert "created_at" in response_data
    
    def test_create_product_validation_error(self, test_client, authenticated_headers, mock_company_context):
        """Test product creation with invalid data."""
        invalid_data = {
            "name": "",  # Empty name should fail
            "sku": "INVALID",
            "list_price": -10.00  # Negative price should fail
        }
        
        response = test_client.post(
            "/api/v1/products/",
            json=invalid_data,
            headers=authenticated_headers
        )
        
        assert response.status_code == 422  # Validation error
        
        error_data = response.json()
        assert "detail" in error_data
        
        # Should have multiple validation errors
        errors = error_data["detail"]
        error_fields = [error["loc"][-1] for error in errors]
        assert "name" in error_fields
        assert "list_price" in error_fields
    
    def test_get_product_by_id(self, test_client, authenticated_headers, mock_company_context):
        """Test retrieving product by ID."""
        # Create product first
        create_data = {
            "name": "Get Test Product",
            "sku": "GET-001",
            "list_price": "50.00"
        }
        
        create_response = test_client.post(
            "/api/v1/products/",
            json=create_data,
            headers=authenticated_headers
        )
        
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Retrieve product
        get_response = test_client.get(
            f"/api/v1/products/{product_id}",
            headers=authenticated_headers
        )
        
        assert get_response.status_code == 200
        
        product_data = get_response.json()
        assert product_data["id"] == product_id
        assert product_data["name"] == create_data["name"]
        assert product_data["sku"] == create_data["sku"]
    
    def test_get_product_not_found(self, test_client, authenticated_headers, mock_company_context):
        """Test retrieving non-existent product."""
        response = test_client.get(
            "/api/v1/products/99999",
            headers=authenticated_headers
        )
        
        assert response.status_code == 404
        error_data = response.json()
        assert "not found" in error_data["detail"].lower()
    
    def test_update_product(self, test_client, authenticated_headers, mock_company_context):
        """Test product update via API."""
        # Create product
        create_data = {
            "name": "Update Test Product",
            "sku": "UPDATE-001",
            "list_price": "100.00"
        }
        
        create_response = test_client.post(
            "/api/v1/products/",
            json=create_data,
            headers=authenticated_headers
        )
        
        product_id = create_response.json()["id"]
        
        # Update product
        update_data = {
            "name": "Updated Product Name",
            "list_price": "150.00"
        }
        
        update_response = test_client.put(
            f"/api/v1/products/{product_id}",
            json=update_data,
            headers=authenticated_headers
        )
        
        assert update_response.status_code == 200
        
        updated_product = update_response.json()
        assert updated_product["name"] == update_data["name"]
        assert updated_product["list_price"] == update_data["list_price"]
        assert updated_product["sku"] == create_data["sku"]  # Unchanged
    
    def test_delete_product(self, test_client, authenticated_headers, mock_company_context):
        """Test product deletion (soft delete)."""
        # Create product
        create_data = {
            "name": "Delete Test Product",
            "sku": "DELETE-001"
        }
        
        create_response = test_client.post(
            "/api/v1/products/",
            json=create_data,
            headers=authenticated_headers
        )
        
        product_id = create_response.json()["id"]
        
        # Delete product
        delete_response = test_client.delete(
            f"/api/v1/products/{product_id}",
            headers=authenticated_headers
        )
        
        assert delete_response.status_code == 204
        
        # Verify product is soft-deleted (should return 404 for active products)
        get_response = test_client.get(
            f"/api/v1/products/{product_id}",
            headers=authenticated_headers
        )
        assert get_response.status_code == 404
    
    def test_get_products_with_filters(self, test_client, authenticated_headers, mock_company_context):
        """Test product listing with filters."""
        # Create test products
        products = [
            {"name": "Filter Product 1", "sku": "FILTER-001", "list_price": "100.00"},
            {"name": "Filter Product 2", "sku": "FILTER-002", "list_price": "200.00"},
            {"name": "Special Widget", "sku": "WIDGET-001", "list_price": "150.00"}
        ]
        
        for product_data in products:
            test_client.post(
                "/api/v1/products/",
                json=product_data,
                headers=authenticated_headers
            )
        
        # Test search filter
        search_response = test_client.get(
            "/api/v1/products/?search_term=Widget",
            headers=authenticated_headers
        )
        
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) == 1
        assert search_results[0]["name"] == "Special Widget"
        
        # Test without filters (should get all active products)
        all_response = test_client.get(
            "/api/v1/products/",
            headers=authenticated_headers
        )
        
        assert all_response.status_code == 200
        all_products = all_response.json()
        assert len(all_products) >= 3
    
    def test_product_margin_calculation_endpoint(self, test_client, authenticated_headers, mock_company_context):
        """Test margin calculation endpoint."""
        # Create product with known margin
        product_data = {
            "name": "Margin Test Product",
            "sku": "MARGIN-001",
            "list_price": "200.00",
            "cost_price": "150.00"
        }
        
        create_response = test_client.post(
            "/api/v1/products/",
            json=product_data,
            headers=authenticated_headers
        )
        
        product_id = create_response.json()["id"]
        
        # Calculate margin
        margin_response = test_client.get(
            f"/api/v1/products/{product_id}/margin",
            headers=authenticated_headers
        )
        
        assert margin_response.status_code == 200
        
        margin_data = margin_response.json()
        assert margin_data["product_id"] == product_id
        assert margin_data["margin_amount"] == "50.00"
        assert margin_data["margin_percentage"] == 25.0
    
    def test_unauthorized_access(self, test_client):
        """Test that endpoints require authentication."""
        # Try to access without auth headers
        response = test_client.get("/api/v1/products/")
        assert response.status_code == 401
        
        # Try with invalid token
        response = test_client.get(
            "/api/v1/products/",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401
    
    def test_api_documentation_available(self, test_client):
        """Test that API documentation is accessible."""
        # OpenAPI JSON
        openapi_response = test_client.get("/api/openapi.json")
        assert openapi_response.status_code == 200
        
        openapi_data = openapi_response.json()
        assert "paths" in openapi_data
        assert "/api/v1/products/" in openapi_data["paths"]
        
        # Swagger UI
        docs_response = test_client.get("/api/docs")
        assert docs_response.status_code == 200
        assert "swagger" in docs_response.text.lower()
    
    def test_cors_headers(self, test_client):
        """Test CORS headers are present."""
        response = test_client.options("/api/v1/products/")
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
```

## Event-Driven Testing

### 1. Event Publishing Tests

**test_product_events.py**
```python
"""Tests for event publishing and consumption in product service."""

import pytest
from unittest.mock import Mock, patch, call
import json
from datetime import datetime

from app.services.product_service import ProductService
from messaging.publisher import EventType, EventPublisher
from messaging.consumer import EventConsumer

class TestProductEvents:
    """Test event publishing and consumption for products."""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection."""
        with patch('messaging.config.get_redis_connection') as mock:
            mock_redis = Mock()
            mock.return_value = mock_redis
            yield mock_redis
    
    @pytest.fixture
    def event_publisher(self, mock_redis):
        """Event publisher with mocked Redis."""
        return EventPublisher("product-service")
    
    def test_product_created_event_publishing(self, db_session, mock_redis):
        """Test that product creation publishes correct event."""
        # Setup
        from app.models.company import Company
        company = Company(name="Event Test Co", code="EVENT", email="event@test.com")
        db_session.add(company)
        db_session.commit()
        
        service = ProductService(db_session)
        
        # Create product
        product_data = {
            "name": "Event Test Product",
            "sku": "EVENT-001",
            "list_price": "99.99"
        }
        
        product = service.create_product(product_data, company.id)
        
        # Verify Redis stream was called
        mock_redis.xadd.assert_called()
        
        # Get the call arguments
        call_args = mock_redis.xadd.call_args
        stream_name = call_args[0][0]
        message_data = call_args[0][1]
        
        assert stream_name == "xerpium:events"
        assert message_data['event_type'] == EventType.PRODUCT_CREATED.value
        assert message_data['entity_type'] == "Product"
        assert message_data['entity_id'] == str(product.id)
        assert message_data['company_id'] == str(company.id)
        assert message_data['service_name'] == "product-service"
        
        # Verify event data contains product information
        event_data = json.loads(message_data['data'])
        assert event_data['name'] == product_data['name']
        assert event_data['action'] == 'created'
    
    def test_product_updated_event_publishing(self, db_session, mock_redis):
        """Test that product updates publish correct events."""
        from app.models.company import Company
        company = Company(name="Update Event Test", code="UPDATE", email="update@test.com")
        db_session.add(company)
        db_session.commit()
        
        service = ProductService(db_session)
        
        # Create product
        product = service.create_product({
            "name": "Original Product",
            "sku": "UPDATE-001",
            "list_price": "100.00"
        }, company.id)
        
        # Reset mock to ignore creation event
        mock_redis.reset_mock()
        
        # Update product
        service.update_product(product.id, {
            "name": "Updated Product",
            "list_price": "150.00"
        }, company.id)
        
        # Verify update event was published
        mock_redis.xadd.assert_called()
        
        call_args = mock_redis.xadd.call_args
        message_data = call_args[0][1]
        
        assert message_data['event_type'] == EventType.PRODUCT_UPDATED.value
        
        event_data = json.loads(message_data['data'])
        assert event_data['action'] == 'updated'
        assert 'changed_fields' in event_data
        assert 'name' in event_data['changed_fields']
        assert 'list_price' in event_data['changed_fields']
    
    def test_event_consumer_setup(self):
        """Test event consumer registration."""
        from app.event_handlers import setup_event_handlers
        from app.services.product_service import ProductService
        
        # Mock product service
        mock_service = Mock(spec=ProductService)
        
        # Setup event consumer
        consumer = setup_event_handlers(mock_service)
        
        # Verify handlers are registered
        assert EventType.PARTNER_CREATED in consumer.handlers
        assert EventType.STOCK_LOW in consumer.handlers
        assert EventType.ORDER_CREATED in consumer.handlers
    
    @pytest.mark.asyncio
    async def test_partner_created_event_handling(self, db_session):
        """Test handling of partner created events."""
        from app.event_handlers import ProductEventHandlers
        from messaging.publisher import EventPayload
        from app.models.company import Company
        
        # Setup
        company = Company(name="Handler Test", code="HANDLER", email="handler@test.com")
        db_session.add(company)
        db_session.commit()
        
        service = ProductService(db_session)
        handler = ProductEventHandlers(service)
        
        # Create mock event
        event = EventPayload(
            event_id="test-event-001",
            event_type=EventType.PARTNER_CREATED,
            service_name="company-partner-service",
            entity_type="Partner",
            entity_id=123,
            company_id=company.id,
            user_id=1,
            timestamp=datetime.utcnow().isoformat(),
            data={
                "name": "Test Supplier",
                "partner_type": "supplier"
            }
        )
        
        # Handle event
        await handler.handle_partner_created(event)
        
        # Verify category was created
        categories = service.get_categories(company.id)
        assert len(categories) == 1
        assert "Test Supplier" in categories[0].name
    
    def test_event_serialization(self, event_publisher):
        """Test that events are properly serialized for Redis."""
        from decimal import Decimal
        
        # Test with complex data types
        complex_data = {
            "price": Decimal("99.99"),
            "created_at": datetime.utcnow(),
            "tags": ["electronics", "smartphone"],
            "metadata": {
                "warranty": "2 years",
                "color": "black"
            }
        }
        
        # Should not raise serialization errors
        event_id = event_publisher.publish_event(
            event_type=EventType.PRODUCT_CREATED,
            entity_type="Product",
            entity_id=123,
            company_id=1,
            data=complex_data
        )
        
        assert event_id is not None
    
    @pytest.mark.asyncio
    async def test_event_consumer_error_handling(self, mock_redis):
        """Test event consumer handles processing errors gracefully."""
        from messaging.consumer import EventConsumer
        
        consumer = EventConsumer("test-service")
        
        # Register handler that raises exception
        def failing_handler(event):
            raise Exception("Handler processing failed")
        
        consumer.register_handler(EventType.PRODUCT_CREATED, failing_handler)
        
        # Mock Redis to return a test message
        mock_redis.xreadgroup.return_value = [
            ('xerpium:events', [
                (b'123-0', {
                    b'event_id': b'test-123',
                    b'event_type': b'product_created',
                    b'service_name': b'test-service',
                    b'entity_type': b'Product',
                    b'entity_id': b'123',
                    b'company_id': b'1',
                    b'user_id': b'',
                    b'timestamp': b'2025-08-08T10:30:00',
                    b'data': b'{}',
                    b'version': b'1.0',
                    b'correlation_id': b''
                })
            ])
        ]
        
        # Process message (should not crash)
        await consumer._process_message(
            'xerpium:events',
            b'123-0',
            mock_redis.xreadgroup.return_value[0][1][0][1]
        )
        
        # Message should not be acknowledged due to handler failure
        mock_redis.xack.assert_not_called()
    
    def test_event_correlation_tracking(self, event_publisher, mock_redis):
        """Test event correlation ID tracking."""
        correlation_id = "user-action-123"
        
        # Publish event with correlation ID
        event_publisher.publish_event(
            event_type=EventType.PRODUCT_CREATED,
            entity_type="Product", 
            entity_id=456,
            company_id=1,
            correlation_id=correlation_id
        )
        
        # Verify correlation ID is included in message
        call_args = mock_redis.xadd.call_args
        message_data = call_args[0][1]
        
        assert message_data['correlation_id'] == correlation_id
```

## Multi-Company Testing

### 1. Multi-Company Isolation Tests

**test_multicompany_isolation.py**
```python
"""Tests for multi-company data isolation."""

import pytest
from app.services.product_service import ProductService
from app.models.product import Product, ProductCategory
from app.models.company import Company

class TestMultiCompanyIsolation:
    """Test data isolation between companies."""
    
    @pytest.fixture
    def companies(self, db_session):
        """Create test companies."""
        companies = [
            Company(name="Company A", code="COMPA", email="a@test.com"),
            Company(name="Company B", code="COMPB", email="b@test.com"),
            Company(name="Company C", code="COMPC", email="c@test.com")
        ]
        db_session.add_all(companies)
        db_session.commit()
        return companies
    
    @pytest.fixture
    def product_service(self, db_session):
        """Product service instance."""
        return ProductService(db_session)
    
    def test_product_company_isolation(self, product_service, companies):
        """Test that products are isolated by company."""
        # Create products in different companies
        products_company_a = []
        products_company_b = []
        
        for i in range(3):
            # Company A products
            product_a = product_service.create_product({
                "name": f"Company A Product {i}",
                "sku": f"A-PROD-{i:03d}"
            }, companies[0].id)
            products_company_a.append(product_a)
            
            # Company B products  
            product_b = product_service.create_product({
                "name": f"Company B Product {i}",
                "sku": f"B-PROD-{i:03d}"
            }, companies[1].id)
            products_company_b.append(product_b)
        
        # Verify company A can only see its products
        company_a_products = product_service.get_products(companies[0].id)
        assert len(company_a_products) == 3
        
        for product in company_a_products:
            assert product.company_id == companies[0].id
            assert product.name.startswith("Company A")
        
        # Verify company B can only see its products
        company_b_products = product_service.get_products(companies[1].id)
        assert len(company_b_products) == 3
        
        for product in company_b_products:
            assert product.company_id == companies[1].id
            assert product.name.startswith("Company B")
        
        # Verify company C sees no products
        company_c_products = product_service.get_products(companies[2].id)
        assert len(company_c_products) == 0
    
    def test_cross_company_access_denied(self, product_service, companies):
        """Test that cross-company access is denied."""
        # Create product in company A
        product_a = product_service.create_product({
            "name": "Private Product",
            "sku": "PRIVATE-001"
        }, companies[0].id)
        
        # Company B should not be able to access it
        product_from_b = product_service.get_product_by_id(
            product_a.id, 
            companies[1].id
        )
        assert product_from_b is None
        
        # Company B should not be able to update it
        with pytest.raises(ValueError, match="not found"):
            product_service.update_product(
                product_a.id,
                {"name": "Hijacked Product"},
                companies[1].id
            )
        
        # Company B should not be able to delete it
        delete_success = product_service.deactivate_product(
            product_a.id,
            companies[1].id
        )
        assert delete_success is False
    
    def test_sku_uniqueness_per_company(self, product_service, companies):
        """Test that SKU uniqueness is enforced per company."""
        # Same SKU should be allowed in different companies
        sku = "DUPLICATE-SKU"
        
        # Create product with same SKU in company A
        product_a = product_service.create_product({
            "name": "Product A",
            "sku": sku
        }, companies[0].id)
        
        # Create product with same SKU in company B (should succeed)
        product_b = product_service.create_product({
            "name": "Product B",
            "sku": sku
        }, companies[1].id)
        
        assert product_a.sku == product_b.sku
        assert product_a.company_id != product_b.company_id
        
        # But duplicate in same company should fail
        with pytest.raises(ValueError, match="already exists"):
            product_service.create_product({
                "name": "Duplicate A",
                "sku": sku
            }, companies[0].id)
    
    def test_category_company_isolation(self, product_service, companies, db_session):
        """Test category isolation between companies."""
        # Create categories in different companies
        category_a = ProductCategory(
            company_id=companies[0].id,
            name="Electronics"
        )
        category_b = ProductCategory(
            company_id=companies[1].id,
            name="Electronics"  # Same name, different company
        )
        
        db_session.add_all([category_a, category_b])
        db_session.commit()
        
        # Create products in each category
        product_a = product_service.create_product({
            "name": "Company A Electronics Product",
            "sku": "A-ELEC-001",
            "category_id": category_a.id
        }, companies[0].id)
        
        product_b = product_service.create_product({
            "name": "Company B Electronics Product",
            "sku": "B-ELEC-001",
            "category_id": category_b.id
        }, companies[1].id)
        
        # Verify products are properly associated with their company's category
        assert product_a.category_id == category_a.id
        assert product_b.category_id == category_b.id
        
        # Verify company A can't access company B's category products
        company_a_electronics = product_service.get_products(
            companies[0].id,
            category_id=category_b.id  # Wrong company's category
        )
        assert len(company_a_electronics) == 0
    
    def test_search_company_isolation(self, product_service, companies):
        """Test that search respects company boundaries."""
        # Create products with similar names in different companies
        search_term = "SearchTest"
        
        product_a = product_service.create_product({
            "name": f"{search_term} Product A",
            "sku": "SEARCH-A-001"
        }, companies[0].id)
        
        product_b = product_service.create_product({
            "name": f"{search_term} Product B",
            "sku": "SEARCH-B-001"
        }, companies[1].id)
        
        # Search from company A should only find company A's product
        company_a_results = product_service.get_products(
            companies[0].id,
            search_term=search_term
        )
        assert len(company_a_results) == 1
        assert company_a_results[0].id == product_a.id
        
        # Search from company B should only find company B's product
        company_b_results = product_service.get_products(
            companies[1].id,
            search_term=search_term
        )
        assert len(company_b_results) == 1
        assert company_b_results[0].id == product_b.id
    
    def test_bulk_operations_company_isolation(self, product_service, companies):
        """Test bulk operations respect company boundaries."""
        # Create products in both companies
        products_a = []
        products_b = []
        
        for i in range(3):
            product_a = product_service.create_product({
                "name": f"Bulk A {i}",
                "sku": f"BULK-A-{i:03d}",
                "list_price": "100.00"
            }, companies[0].id)
            products_a.append(product_a)
            
            product_b = product_service.create_product({
                "name": f"Bulk B {i}",
                "sku": f"BULK-B-{i:03d}",
                "list_price": "100.00"
            }, companies[1].id)
            products_b.append(product_b)
        
        # Attempt bulk price update from company A including company B's products
        price_updates = [
            {"product_id": products_a[0].id, "list_price": "150.00"},  # Own product
            {"product_id": products_a[1].id, "list_price": "160.00"},  # Own product  
            {"product_id": products_b[0].id, "list_price": "170.00"},  # Other company's product
        ]
        
        result = product_service.bulk_update_prices(price_updates, companies[0].id)
        
        # Should only update own products
        assert result["updated_count"] == 2
        assert result["total_attempted"] == 3
        assert len(result["errors"]) == 1
        
        # Verify other company's product was not updated
        unchanged_product = product_service.get_product_by_id(
            products_b[0].id,
            companies[1].id
        )
        assert unchanged_product.list_price == 100.00  # Original price
    
    def test_company_context_validation(self, product_service, companies):
        """Test validation of company context in operations."""
        # Create product
        product = product_service.create_product({
            "name": "Context Test Product",
            "sku": "CONTEXT-001"
        }, companies[0].id)
        
        # Operations with invalid company ID should fail gracefully
        invalid_company_id = 99999
        
        # Get operation
        result = product_service.get_product_by_id(product.id, invalid_company_id)
        assert result is None
        
        # Update operation
        with pytest.raises(ValueError):
            product_service.update_product(
                product.id,
                {"name": "Should Fail"},
                invalid_company_id
            )
        
        # Delete operation
        delete_result = product_service.deactivate_product(product.id, invalid_company_id)
        assert delete_result is False
        
        # Original product should be unchanged
        original_product = product_service.get_product_by_id(product.id, companies[0].id)
        assert original_product is not None
        assert original_product.name == "Context Test Product"
        assert original_product.is_active is True
```

## Test Data Management

### 1. Test Data Factories

**test_data_factories.py**
```python
"""Test data factories for creating realistic test data."""

import factory
from factory.alchemy import SQLAlchemyModelFactory
from decimal import Decimal
import random
from datetime import datetime, timedelta

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.product import Product, ProductCategory

class CompanyFactory(SQLAlchemyModelFactory):
    """Factory for creating test companies."""
    
    class Meta:
        model = Company
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"
    
    name = factory.Sequence(lambda n: f"Test Company {n}")
    code = factory.Sequence(lambda n: f"TC{n:03d}")
    email = factory.LazyAttribute(lambda obj: f"{obj.code.lower()}@testcompany.com")
    phone = factory.Faker('phone_number')
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    country = factory.Faker('country')
    is_active = True

class ProductCategoryFactory(SQLAlchemyModelFactory):
    """Factory for creating test product categories."""
    
    class Meta:
        model = ProductCategory
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"
    
    company = factory.SubFactory(CompanyFactory)
    company_id = factory.LazyAttribute(lambda obj: obj.company.id)
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=200)
    is_active = True

class ProductFactory(SQLAlchemyModelFactory):
    """Factory for creating test products."""
    
    class Meta:
        model = Product
        sqlalchemy_session = SessionLocal()
        sqlalchemy_session_persistence = "commit"
    
    company = factory.SubFactory(CompanyFactory)
    company_id = factory.LazyAttribute(lambda obj: obj.company.id)
    category = factory.SubFactory(ProductCategoryFactory, company=factory.SelfAttribute('..company'))
    category_id = factory.LazyAttribute(lambda obj: obj.category.id)
    
    name = factory.Faker('catch_phrase')
    sku = factory.Sequence(lambda n: f"PROD-{n:06d}")
    description = factory.Faker('text', max_nb_chars=500)
    barcode = factory.Sequence(lambda n: f"12345{n:07d}")
    
    # Realistic pricing
    cost_price = factory.LazyFunction(lambda: Decimal(str(round(random.uniform(10, 500), 2))))
    list_price = factory.LazyAttribute(lambda obj: obj.cost_price * Decimal(str(round(random.uniform(1.2, 2.5), 2))))
    
    is_active = True
    is_sellable = True
    is_purchasable = True
    track_inventory = True
    minimum_stock = factory.LazyFunction(lambda: random.randint(5, 50))
    maximum_stock = factory.LazyAttribute(lambda obj: obj.minimum_stock * random.randint(5, 20))

class ProductTestDataSet:
    """Pre-configured test data sets for different scenarios."""
    
    @staticmethod
    def create_electronics_catalog(company=None, db_session=None):
        """Create a realistic electronics product catalog."""
        if not company:
            company = CompanyFactory()
        
        # Create electronics categories
        electronics = ProductCategoryFactory(
            company=company,
            name="Electronics",
            description="Electronic devices and accessories"
        )
        
        smartphones = ProductCategoryFactory(
            company=company,
            name="Smartphones",
            description="Mobile phones and smartphones",
            parent=electronics
        )
        
        laptops = ProductCategoryFactory(
            company=company,
            name="Laptops",
            description="Laptop computers",
            parent=electronics
        )
        
        # Create products
        products = []
        
        # Smartphones
        smartphone_names = ["iPhone 15", "Samsung Galaxy S24", "Google Pixel 8", "OnePlus 12"]
        for name in smartphone_names:
            product = ProductFactory(
                company=company,
                category=smartphones,
                name=name,
                cost_price=Decimal("600.00"),
                list_price=Decimal("999.99"),
                minimum_stock=10,
                maximum_stock=100
            )
            products.append(product)
        
        # Laptops  
        laptop_names = ["MacBook Pro", "Dell XPS 13", "ThinkPad X1", "Surface Laptop"]
        for name in laptop_names:
            product = ProductFactory(
                company=company,
                category=laptops,
                name=name,
                cost_price=Decimal("800.00"),
                list_price=Decimal("1299.99"),
                minimum_stock=5,
                maximum_stock=50
            )
            products.append(product)
        
        return {
            "company": company,
            "categories": [electronics, smartphones, laptops],
            "products": products
        }
    
    @staticmethod
    def create_multi_company_scenario(num_companies=3, products_per_company=10):
        """Create multi-company test scenario."""
        companies = []
        all_products = []
        
        for i in range(num_companies):
            company = CompanyFactory(
                name=f"Multi-Test Company {i+1}",
                code=f"MTC{i+1:02d}"
            )
            companies.append(company)
            
            # Create categories for this company
            category = ProductCategoryFactory(
                company=company,
                name=f"Company {i+1} Products"
            )
            
            # Create products
            company_products = []
            for j in range(products_per_company):
                product = ProductFactory(
                    company=company,
                    category=category,
                    name=f"Product {j+1} from Company {i+1}",
                    sku=f"C{i+1}-PROD-{j+1:03d}"
                )
                company_products.append(product)
            
            all_products.extend(company_products)
        
        return {
            "companies": companies,
            "products": all_products
        }
    
    @staticmethod
    def create_performance_test_data(company=None, num_products=1000):
        """Create large dataset for performance testing."""
        if not company:
            company = CompanyFactory(name="Performance Test Co")
        
        # Create categories
        categories = []
        for i in range(10):
            category = ProductCategoryFactory(
                company=company,
                name=f"Performance Category {i+1}"
            )
            categories.append(category)
        
        # Create products in batches
        products = []
        batch_size = 100
        
        for batch in range(0, num_products, batch_size):
            batch_products = []
            for i in range(batch, min(batch + batch_size, num_products)):
                category = random.choice(categories)
                product = ProductFactory(
                    company=company,
                    category=category,
                    name=f"Performance Product {i+1}",
                    sku=f"PERF-{i+1:06d}"
                )
                batch_products.append(product)
            
            products.extend(batch_products)
        
        return {
            "company": company,
            "categories": categories,
            "products": products
        }

# Usage in tests
@pytest.fixture
def electronics_catalog(db_session):
    """Electronics catalog test data."""
    return ProductTestDataSet.create_electronics_catalog()

@pytest.fixture
def multi_company_data(db_session):
    """Multi-company test data."""
    return ProductTestDataSet.create_multi_company_scenario(num_companies=3, products_per_company=5)

@pytest.fixture
def large_dataset(db_session):
    """Large dataset for performance testing."""
    return ProductTestDataSet.create_performance_test_data(num_products=100)  # Smaller for tests
```

### 2. Test Database Management

**test_database_utils.py**
```python
"""Utilities for test database management."""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.core.database import Base

class TestDatabaseManager:
    """Manage test databases for different testing scenarios."""
    
    def __init__(self):
        self.engines = {}
        self.sessions = {}
        self.temp_files = []
    
    def create_test_db(self, name: str = "default"):
        """Create a fresh test database."""
        # Create temporary SQLite database
        temp_fd, temp_path = tempfile.mkstemp(suffix=f'_{name}.db')
        os.close(temp_fd)  # Close file descriptor
        self.temp_files.append(temp_path)
        
        # Create engine and session
        database_url = f"sqlite:///{temp_path}"
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}
        )
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        
        # Store engine and create session factory
        self.engines[name] = engine
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.sessions[name] = SessionLocal
        
        return engine, SessionLocal
    
    def get_session(self, name: str = "default"):
        """Get session factory for named database."""
        if name not in self.sessions:
            self.create_test_db(name)
        return self.sessions[name]
    
    def reset_database(self, name: str = "default"):
        """Reset database by dropping and recreating all tables."""
        if name in self.engines:
            engine = self.engines[name]
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
    
    def cleanup(self):
        """Clean up all test databases."""
        # Close all sessions
        for session_factory in self.sessions.values():
            # Close any open sessions
            try:
                session_factory.close_all()
            except:
                pass
        
        # Close all engines
        for engine in self.engines.values():
            engine.dispose()
        
        # Remove temporary files
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        # Clear collections
        self.engines.clear()
        self.sessions.clear()
        self.temp_files.clear()
    
    def execute_sql(self, sql: str, name: str = "default"):
        """Execute raw SQL on named database."""
        if name in self.engines:
            with self.engines[name].connect() as conn:
                return conn.execute(text(sql))
        return None
    
    def get_table_count(self, table_name: str, name: str = "default"):
        """Get row count for table."""
        result = self.execute_sql(f"SELECT COUNT(*) FROM {table_name}", name)
        if result:
            return result.scalar()
        return 0

# Global test database manager
test_db_manager = TestDatabaseManager()

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_databases():
    """Clean up test databases after test session."""
    yield
    test_db_manager.cleanup()

@pytest.fixture
def isolated_db():
    """Provide isolated database for tests that need complete isolation."""
    import uuid
    db_name = f"isolated_{uuid.uuid4().hex[:8]}"
    
    engine, session_factory = test_db_manager.create_test_db(db_name)
    session = session_factory()
    
    try:
        yield session
    finally:
        session.close()
        test_db_manager.reset_database(db_name)

@pytest.fixture
def populated_db(isolated_db):
    """Database pre-populated with test data."""
    from test_data_factories import ProductTestDataSet
    
    # Create realistic test data
    catalog = ProductTestDataSet.create_electronics_catalog(db_session=isolated_db)
    
    yield isolated_db, catalog

@pytest.fixture(params=["sqlite", "postgresql"])
def multi_db_test(request):
    """Test fixture that runs tests against multiple database types."""
    db_type = request.param
    
    if db_type == "sqlite":
        # Use SQLite (default for tests)
        engine, session_factory = test_db_manager.create_test_db(f"multi_{db_type}")
        session = session_factory()
        
        try:
            yield session, db_type
        finally:
            session.close()
    
    elif db_type == "postgresql":
        # Skip PostgreSQL tests if not available
        pytest.skip("PostgreSQL not available in test environment")
```

## Performance Testing

### 1. Load Testing

**test_performance.py**
```python
"""Performance tests for product service."""

import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from app.services.product_service import ProductService
from test_data_factories import ProductTestDataSet, CompanyFactory

class TestProductServicePerformance:
    """Performance tests for product service operations."""
    
    def test_bulk_product_creation_performance(self, db_session):
        """Test performance of bulk product creation."""
        service = ProductService(db_session)
        company = CompanyFactory()
        
        # Warm up
        for i in range(10):
            service.create_product({
                "name": f"Warmup Product {i}",
                "sku": f"WARMUP-{i:03d}"
            }, company.id)
        
        # Performance test
        start_time = time.time()
        products_created = []
        
        for i in range(100):
            product = service.create_product({
                "name": f"Bulk Product {i}",
                "sku": f"BULK-{i:06d}",
                "list_price": Decimal("99.99")
            }, company.id)
            products_created.append(product)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert len(products_created) == 100
        assert total_time < 10.0  # Should complete in under 10 seconds
        
        avg_time_per_product = total_time / 100
        assert avg_time_per_product < 0.1  # Less than 100ms per product
        
        print(f"Created 100 products in {total_time:.2f}s ({avg_time_per_product*1000:.1f}ms per product)")
    
    def test_product_query_performance(self, db_session):
        """Test performance of product queries."""
        service = ProductService(db_session)
        
        # Create test data
        large_dataset = ProductTestDataSet.create_performance_test_data(num_products=500)
        company = large_dataset["company"]
        
        # Test various query patterns
        query_times = {}
        
        # 1. Get all products
        start_time = time.time()
        all_products = service.get_products(company.id)
        query_times["get_all"] = time.time() - start_time
        
        assert len(all_products) == 500
        assert query_times["get_all"] < 1.0  # Under 1 second
        
        # 2. Get products by category
        category = large_dataset["categories"][0]
        start_time = time.time()
        category_products = service.get_products(company.id, category_id=category.id)
        query_times["by_category"] = time.time() - start_time
        
        assert len(category_products) > 0
        assert query_times["by_category"] < 0.5  # Under 500ms
        
        # 3. Search products
        start_time = time.time()
        search_results = service.get_products(company.id, search_term="Product 1")
        query_times["search"] = time.time() - start_time
        
        assert len(search_results) >= 10  # Should find "Product 1", "Product 10", etc.
        assert query_times["search"] < 0.5  # Under 500ms
        
        # 4. Get single product by ID
        test_product = all_products[0]
        times = []
        
        for _ in range(100):
            start_time = time.time()
            product = service.get_product_by_id(test_product.id, company.id)
            times.append(time.time() - start_time)
            assert product is not None
        
        avg_single_query_time = statistics.mean(times)
        assert avg_single_query_time < 0.01  # Under 10ms average
        
        print(f"Query performance: get_all={query_times['get_all']:.3f}s, "
              f"by_category={query_times['by_category']:.3f}s, "
              f"search={query_times['search']:.3f}s, "
              f"single={avg_single_query_time*1000:.1f}ms")
    
    def test_concurrent_access_performance(self, db_session):
        """Test performance under concurrent access."""
        service = ProductService(db_session)
        company = CompanyFactory()
        
        # Create some initial data
        for i in range(50):
            service.create_product({
                "name": f"Concurrent Product {i}",
                "sku": f"CONC-{i:03d}"
            }, company.id)
        
        def worker_function(worker_id):
            """Worker function for concurrent testing."""
            results = []
            
            # Simulate mixed workload
            for i in range(10):
                start_time = time.time()
                
                if i % 3 == 0:
                    # Query operation
                    products = service.get_products(company.id)
                    results.append(("query", time.time() - start_time, len(products)))
                
                elif i % 3 == 1:
                    # Create operation
                    product = service.create_product({
                        "name": f"Worker {worker_id} Product {i}",
                        "sku": f"W{worker_id}-{i:03d}"
                    }, company.id)
                    results.append(("create", time.time() - start_time, product.id))
                
                else:
                    # Search operation
                    search_results = service.get_products(company.id, search_term="Product")
                    results.append(("search", time.time() - start_time, len(search_results)))
            
            return results
        
        # Run concurrent workers
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker_function, i) for i in range(5)]
            all_results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        
        # Analyze results
        operation_times = {"query": [], "create": [], "search": []}
        
        for worker_results in all_results:
            for operation, duration, result_value in worker_results:
                operation_times[operation].append(duration)
        
        # Performance assertions
        assert total_time < 15.0  # Should complete in under 15 seconds
        
        for operation, times in operation_times.items():
            if times:
                avg_time = statistics.mean(times)
                max_time = max(times)
                
                # No operation should take more than 1 second
                assert max_time < 1.0, f"{operation} took {max_time:.3f}s"
                
                print(f"{operation}: avg={avg_time*1000:.1f}ms, max={max_time*1000:.1f}ms, count={len(times)}")
    
    def test_memory_usage_under_load(self, db_session):
        """Test memory usage during high-load operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        service = ProductService(db_session)
        company = CompanyFactory()
        
        # Create and query products in batches
        products_created = []
        memory_samples = [initial_memory]
        
        for batch in range(10):
            # Create batch of products
            batch_products = []
            for i in range(50):
                product = service.create_product({
                    "name": f"Memory Test Product {batch}-{i}",
                    "sku": f"MEM-{batch:02d}-{i:03d}"
                }, company.id)
                batch_products.append(product)
            
            products_created.extend(batch_products)
            
            # Query all products
            all_products = service.get_products(company.id)
            assert len(all_products) == (batch + 1) * 50
            
            # Sample memory usage
            current_memory = process.memory_info().rss
            memory_samples.append(current_memory)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        
        # Memory should not increase excessively
        assert memory_increase_mb < 100, f"Memory increased by {memory_increase_mb:.1f}MB"
        
        print(f"Memory usage: initial={initial_memory/1024/1024:.1f}MB, "
              f"final={final_memory/1024/1024:.1f}MB, "
              f"increase={memory_increase_mb:.1f}MB")
    
    @pytest.mark.parametrize("num_products", [100, 500, 1000])
    def test_scalability_with_dataset_size(self, db_session, num_products):
        """Test how performance scales with dataset size."""
        service = ProductService(db_session)
        
        # Create dataset
        dataset = ProductTestDataSet.create_performance_test_data(num_products=num_products)
        company = dataset["company"]
        
        # Test query performance
        start_time = time.time()
        all_products = service.get_products(company.id)
        query_time = time.time() - start_time
        
        assert len(all_products) == num_products
        
        # Performance should scale sub-linearly
        expected_max_time = 0.001 * num_products + 0.5  # Linear scaling + overhead
        assert query_time < expected_max_time, f"Query took {query_time:.3f}s for {num_products} products"
        
        # Test search performance
        start_time = time.time()
        search_results = service.get_products(company.id, search_term="Product")
        search_time = time.time() - start_time
        
        assert len(search_results) >= num_products * 0.8  # Most products should match
        assert search_time < expected_max_time, f"Search took {search_time:.3f}s for {num_products} products"
        
        print(f"Dataset {num_products}: query={query_time:.3f}s, search={search_time:.3f}s")
```

---

## Summary

This comprehensive testing guide provides:

- **Complete testing strategy** following the testing pyramid
- **Unit testing patterns** for models, services, and utilities
- **Integration testing** for database and API endpoints
- **Event-driven testing** for Redis Streams messaging
- **Multi-company isolation testing** for tenant separation
- **Test data management** with factories and realistic datasets
- **Performance testing** for scalability and load handling
- **End-to-end testing patterns** for complete workflows

These testing patterns ensure XERPIUM services are reliable, performant, and maintain proper multi-tenant isolation while providing fast feedback to developers.