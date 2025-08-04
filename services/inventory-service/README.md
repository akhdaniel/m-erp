# M-ERP Inventory Service

Comprehensive inventory management service providing product catalog, stock management, warehouse operations, and receiving functionality for the M-ERP system.

## Features

### Product Management
- **Product Catalog**: Complete product information management with categories, variants, and attributes
- **Product Categories**: Hierarchical categorization system with parent-child relationships
- **Product Variants**: Support for product variations (size, color, material, etc.)
- **Pricing Management**: List and cost price tracking with margin calculations
- **Inventory Settings**: Reorder points, stock levels, and inventory tracking configuration

### Stock Management
- **Real-time Stock Levels**: Track quantity on-hand, reserved, and available across locations
- **Stock Movements**: Complete audit trail of all inventory transactions
- **Stock Adjustments**: Manual stock adjustments with approval workflows
- **Stock Reservations**: Reserve stock for orders and allocations
- **Multi-location Support**: Track stock across multiple warehouses and locations

### Warehouse Management
- **Warehouse Configuration**: Multi-warehouse support with capabilities and settings
- **Location Hierarchy**: Organize storage locations in hierarchical structures
- **Capacity Management**: Track weight, volume, and item capacity limits
- **Location Optimization**: Putaway location suggestions and optimization
- **Access Control**: Restricted access and permissions for sensitive locations

### Receiving Operations
- **Receiving Records**: Process inbound inventory from purchase orders
- **Line Item Management**: Detailed tracking of expected vs received quantities
- **Quality Control**: Quality inspection workflows with pass/fail tracking
- **Batch and Serial Tracking**: Support for batch numbers and serial number tracking
- **Exception Handling**: Manage damaged goods, rejections, and over-receipts

## Architecture

The inventory service follows a layered architecture:

```
├── inventory_module/
│   ├── models/          # SQLAlchemy database models
│   ├── services/        # Business logic layer
│   ├── api/             # FastAPI REST endpoints
│   └── framework/       # Base classes and utilities
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── Dockerfile          # Container configuration
```

## API Endpoints

### Products API (`/api/v1/products`)
- `GET /products` - List products with filtering
- `POST /products` - Create new product
- `GET /products/search` - Search products by text
- `GET /products/low-stock` - Get products with low stock
- `GET /products/{id}` - Get product by ID
- `PUT /products/{id}` - Update product
- `PUT /products/{id}/pricing` - Update product pricing
- `DELETE /products/{id}` - Delete product

### Categories API (`/api/v1/products/categories`)
- `GET /categories` - List categories
- `POST /categories` - Create category
- `GET /categories/tree` - Get category hierarchy
- `GET /categories/{id}` - Get category by ID
- `PUT /categories/{id}` - Update category

### Stock API (`/api/v1/stock`)
- `GET /stock/levels` - List stock levels
- `GET /stock/summary/product/{id}` - Get product stock summary
- `POST /stock/availability/check` - Check stock availability
- `POST /stock/adjust` - Adjust stock levels
- `POST /stock/reserve` - Reserve stock
- `GET /stock/movements` - List stock movements

### Warehouses API (`/api/v1/warehouses`)
- `GET /warehouses` - List warehouses
- `POST /warehouses` - Create warehouse
- `GET /warehouses/{id}/locations` - List warehouse locations
- `POST /warehouses/{id}/locations` - Create location
- `GET /warehouses/{id}/locations/hierarchy` - Get location tree
- `GET /warehouses/{id}/locations/available` - Get available locations

### Receiving API (`/api/v1/receiving`)
- `GET /receiving` - List receiving records
- `POST /receiving` - Create receiving record
- `PUT /receiving/{id}/start` - Start receiving process
- `PUT /receiving/{id}/complete` - Complete receiving
- `GET /receiving/{id}/line-items` - Get line items
- `PUT /receiving/line-items/{id}/receive` - Receive quantity

## Database Models

### Core Models
- **Product**: Product catalog with full product information
- **ProductCategory**: Hierarchical product categorization
- **ProductVariant**: Product variations and attributes
- **StockLevel**: Current stock quantities by location
- **StockMovement**: Audit trail of all stock changes
- **Warehouse**: Warehouse facilities and configuration
- **WarehouseLocation**: Storage locations within warehouses
- **ReceivingRecord**: Inbound receiving operations
- **ReceivingLineItem**: Individual line items in receipts

### Framework Integration
All models inherit from the Business Object Framework base classes providing:
- Multi-company data isolation
- Automatic audit logging
- Event publishing for integration
- Standardized CRUD operations
- Validation and error handling

## Service Layer

### Business Logic Services
- **ProductService**: Product catalog management
- **ProductCategoryService**: Category operations
- **ProductVariantService**: Variant management
- **StockService**: Stock level operations
- **StockMovementService**: Movement tracking
- **WarehouseService**: Warehouse management
- **WarehouseLocationService**: Location operations
- **ReceivingService**: Receiving operations

### Features
- Transaction management with automatic rollback
- Comprehensive error handling and validation
- Event publishing for system integration
- Multi-company data isolation
- Audit trail logging

## Development

### Prerequisites
- Python 3.12+
- PostgreSQL 17+
- Redis (for caching and messaging)

### Setup
```bash
# Clone repository
git clone <repository-url>
cd services/inventory-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost/inventory_db"
export REDIS_URL="redis://localhost:6379"

# Run application
python main.py
```

### Docker Deployment
```bash
# Build image
docker build -t m-erp/inventory-service .

# Run container
docker run -p 8005:8005 \
  -e DATABASE_URL="postgresql://user:password@db/inventory_db" \
  -e REDIS_URL="redis://redis:6379" \
  m-erp/inventory-service
```

### API Documentation
- Swagger UI: http://localhost:8005/api/docs
- ReDoc: http://localhost:8005/api/redoc
- OpenAPI JSON: http://localhost:8005/api/openapi.json

## Integration

### Event Publishing
The service publishes events for key operations:
- Product lifecycle events (created, updated, discontinued)
- Stock level changes and movements
- Receiving status updates
- Warehouse and location changes

### Multi-Company Support
All operations respect company boundaries:
- Automatic company ID filtering
- Company-scoped data access
- User permission validation

### Business Object Framework
Leverages the standardized framework for:
- Consistent API patterns
- Automatic audit trails
- Event-driven architecture
- Multi-company isolation

## Monitoring and Observability

### Health Checks
- `/health` - Service health status
- Database connectivity validation
- Redis connectivity validation

### Metrics and Logging
- Structured JSON logging
- Performance metrics tracking
- Error rate monitoring
- Business metrics (stock levels, movements, etc.)

## Security

### Authentication & Authorization
- JWT token validation
- Role-based access control
- Company-scoped data access
- API rate limiting

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- Secure error handling
- Audit trail maintenance

## Performance Considerations

### Caching Strategy
- Redis caching for frequently accessed data
- Stock level caching with TTL
- Product catalog caching

### Database Optimization
- Proper indexing on query fields
- Connection pooling
- Query optimization
- Batch operations for bulk updates

### Scalability
- Horizontal scaling support
- Stateless service design
- Background job processing
- Load balancing ready