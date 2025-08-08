# Business Object Framework Usage Examples

## 🎯 Common Business Object Patterns

This guide provides practical examples for common business object patterns using the XERPIUM Business Object Framework. Each pattern includes complete implementation examples with best practices.

## 📚 Table of Contents

1. [Simple Business Object](#simple-business-object)
2. [Hierarchical Business Object](#hierarchical-business-object)
3. [Business Object with Relationships](#business-object-with-relationships)
4. [Multi-Status Business Object](#multi-status-business-object)
5. [Configurable Business Object](#configurable-business-object)
6. [Approval Workflow Business Object](#approval-workflow-business-object)
7. [Document Management Business Object](#document-management-business-object)
8. [Time-Based Business Object](#time-based-business-object)
9. [Batch Processing Business Object](#batch-processing-business-object)
10. [Integration-Heavy Business Object](#integration-heavy-business-object)

## 🔧 Pattern 1: Simple Business Object

**Use Case**: Basic entity with CRUD operations (e.g., Category, Tag, Setting)

### Model Implementation

```python
# app/models/category.py
from sqlalchemy import Column, String, Text, Boolean
from app.framework.base import CompanyBaseModel
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin

class Category(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    """Simple category business object"""
    
    __tablename__ = "categories"
    
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"
```

### Schema Implementation

```python
# app/schemas/category.py
from typing import Optional
from pydantic import Field, validator
from app.framework.schemas import CompanyBusinessObjectSchema

class CategoryBase(CompanyBusinessObjectSchema):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$', description="Hex color code")
    is_active: bool = Field(True, description="Whether category is active")
    
    @validator('name')
    def validate_name(cls, v):
        return v.strip().title()  # Auto-format to title case
    
    @validator('color')
    def validate_color(cls, v):
        if v and not v.startswith('#'):
            v = f"#{v}"
        return v.upper() if v else v

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Service Implementation

```python
# app/services/category_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.framework.services import CompanyBusinessObjectService
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService(CompanyBusinessObjectService[Category, CategoryCreate, CategoryUpdate]):
    """Simple category service with framework capabilities"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Category)
    
    async def get_active_categories(self, company_id: int) -> List[Category]:
        """Get all active categories"""
        return await self.get_list(
            filters={"is_active": True},
            company_id=company_id,
            order_by="name"
        )
    
    async def find_category_by_name(self, name: str, company_id: int) -> Optional[Category]:
        """Find category by name (case-insensitive)"""
        return await self.get_one(
            filters={"name__ilike": name},
            company_id=company_id
        )
    
    async def get_categories_by_color(self, color: str, company_id: int) -> List[Category]:
        """Get categories by color"""
        return await self.get_list(
            filters={"color": color.upper()},
            company_id=company_id
        )
```

### Router Implementation

```python
# app/routers/categories.py
from fastapi import APIRouter, Depends, HTTPException, Query
from app.framework.controllers import create_business_object_router
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

# Auto-generate standard CRUD router
router = create_business_object_router(
    service_class=CategoryService,
    create_schema=CategoryCreate,
    update_schema=CategoryUpdate,
    response_schema=CategoryResponse,
    prefix="/categories",
    tags=["Categories"],
    company_scoped=True
)

# Add custom endpoints
@router.get("/by-color/{color}", response_model=List[CategoryResponse])
async def get_categories_by_color(
    color: str,
    company_id: int = Depends(get_current_user_company),
    service: CategoryService = Depends(get_category_service)
):
    """Get categories by color"""
    categories = await service.get_categories_by_color(color, company_id)
    return categories
```

## 🌳 Pattern 2: Hierarchical Business Object

**Use Case**: Tree-like structures (e.g., Organization Chart, Product Categories, File Folders)

### Model Implementation

```python
# app/models/department.py
from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.framework.base import CompanyBaseModel
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin

class Department(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    """Hierarchical department business object"""
    
    __tablename__ = "departments"
    
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    code = Column(String(20), nullable=False, index=True)
    manager_name = Column(String(100), nullable=True)
    budget = Column(Integer, nullable=True)  # Budget in cents
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Hierarchical relationship
    parent_id = Column(Integer, ForeignKey('departments.id'), nullable=True, index=True)
    
    # Self-referential relationships
    parent = relationship("Department", remote_side="Department.id", back_populates="children")
    children = relationship("Department", back_populates="parent", cascade="all, delete-orphan")
    
    @property
    def level(self) -> int:
        """Calculate department level in hierarchy"""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level
    
    @property
    def full_path(self) -> str:
        """Get full department path"""
        path_parts = []
        current = self
        while current:
            path_parts.append(current.name)
            current = current.parent
        return " > ".join(reversed(path_parts))
    
    def get_all_descendants(self) -> List['Department']:
        """Get all descendant departments"""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants
```

### Schema Implementation

```python
# app/schemas/department.py
from typing import Optional, List
from decimal import Decimal
from pydantic import Field, validator
from app.framework.schemas import CompanyBusinessObjectSchema

class DepartmentBase(CompanyBusinessObjectSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    code: str = Field(..., min_length=1, max_length=20)
    manager_name: Optional[str] = Field(None, max_length=100)
    budget: Optional[int] = Field(None, ge=0)  # Budget in cents
    parent_id: Optional[int] = Field(None, description="Parent department ID")
    
    @validator('code')
    def validate_code(cls, v):
        return v.upper().strip()
    
    @validator('budget')
    def validate_budget(cls, v):
        if v is not None and v < 0:
            raise ValueError('Budget cannot be negative')
        return v

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)

class DepartmentResponse(DepartmentBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    level: int
    full_path: str
    children_count: int = 0
    
    class Config:
        from_attributes = True

class DepartmentTreeResponse(DepartmentResponse):
    """Department with full tree structure"""
    children: List['DepartmentTreeResponse'] = []
```

### Service Implementation

```python
# app/services/department_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.framework.services import CompanyBusinessObjectService
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate

class DepartmentService(CompanyBusinessObjectService[Department, DepartmentCreate, DepartmentUpdate]):
    """Hierarchical department service"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Department)
    
    async def get_department_tree(self, company_id: int) -> List[Department]:
        """Get complete department tree"""
        query = (
            select(Department)
            .where(Department.company_id == company_id)
            .where(Department.parent_id.is_(None))  # Root departments
            .options(selectinload(Department.children))
            .order_by(Department.name)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_department_with_descendants(self, department_id: int, company_id: int) -> Optional[Department]:
        """Get department with all descendants loaded"""
        query = (
            select(Department)
            .where(Department.id == department_id)
            .where(Department.company_id == company_id)
            .options(selectinload(Department.children))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def move_department(self, department_id: int, new_parent_id: Optional[int], company_id: int) -> bool:
        """Move department to new parent"""
        department = await self.get_by_id(department_id, company_id)
        if not department:
            return False
        
        # Prevent circular references
        if new_parent_id and await self._would_create_cycle(department_id, new_parent_id, company_id):
            raise ValueError("Move would create circular reference")
        
        department.parent_id = new_parent_id
        await self.db.commit()
        return True
    
    async def get_department_budget_rollup(self, department_id: int, company_id: int) -> Dict[str, Any]:
        """Get department budget including all descendants"""
        department = await self.get_department_with_descendants(department_id, company_id)
        if not department:
            return {}
        
        total_budget = department.budget or 0
        for descendant in department.get_all_descendants():
            total_budget += descendant.budget or 0
        
        return {
            "department_id": department_id,
            "own_budget": department.budget,
            "total_budget": total_budget,
            "descendants_count": len(department.get_all_descendants())
        }
    
    async def _would_create_cycle(self, department_id: int, new_parent_id: int, company_id: int) -> bool:
        """Check if moving department would create a cycle"""
        current_parent_id = new_parent_id
        while current_parent_id:
            if current_parent_id == department_id:
                return True
            parent = await self.get_by_id(current_parent_id, company_id)
            current_parent_id = parent.parent_id if parent else None
        return False
```

### Router Implementation

```python
# app/routers/departments.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.department_service import DepartmentService
from app.schemas.department import DepartmentTreeResponse

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/tree", response_model=List[DepartmentTreeResponse])
async def get_department_tree(
    company_id: int = Depends(get_current_user_company),
    service: DepartmentService = Depends(get_department_service)
):
    """Get complete department hierarchy"""
    tree = await service.get_department_tree(company_id)
    return tree

@router.post("/{department_id}/move")
async def move_department(
    department_id: int,
    new_parent_id: Optional[int],
    company_id: int = Depends(get_current_user_company),
    service: DepartmentService = Depends(get_department_service)
):
    """Move department to new parent"""
    try:
        success = await service.move_department(department_id, new_parent_id, company_id)
        if not success:
            raise HTTPException(status_code=404, detail="Department not found")
        return {"message": "Department moved successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{department_id}/budget-rollup")
async def get_department_budget_rollup(
    department_id: int,
    company_id: int = Depends(get_current_user_company),
    service: DepartmentService = Depends(get_department_service)
):
    """Get department budget including descendants"""
    budget_info = await service.get_department_budget_rollup(department_id, company_id)
    if not budget_info:
        raise HTTPException(status_code=404, detail="Department not found")
    return budget_info
```

## 🔗 Pattern 3: Business Object with Relationships

**Use Case**: Objects with complex relationships (e.g., Order with Items, Project with Tasks)

### Model Implementation

```python
# app/models/order.py
from sqlalchemy import Column, String, Integer, Decimal, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.framework.base import CompanyBaseModel
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin

class Order(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    """Order with related items"""
    
    __tablename__ = "orders"
    
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False, index=True)
    order_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default='draft', index=True)
    subtotal = Column(Decimal(12, 2), nullable=False, default=0)
    tax_amount = Column(Decimal(12, 2), nullable=False, default=0)
    total_amount = Column(Decimal(12, 2), nullable=False, default=0)
    notes = Column(Text, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    @property
    def items_count(self) -> int:
        return len(self.order_items)
    
    def calculate_totals(self):
        """Recalculate order totals"""
        self.subtotal = sum(item.line_total for item in self.order_items)
        self.tax_amount = self.subtotal * Decimal('0.08')  # 8% tax
        self.total_amount = self.subtotal + self.tax_amount

class OrderItem(CompanyBaseModel, BusinessObjectMixin):
    """Order line item"""
    
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Decimal(10, 2), nullable=False)
    line_total = Column(Decimal(12, 2), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")
    
    def calculate_line_total(self):
        """Calculate line total"""
        self.line_total = self.quantity * self.unit_price
```

### Schema Implementation

```python
# app/schemas/order.py
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import Field, validator, root_validator
from app.framework.schemas import CompanyBusinessObjectSchema

class OrderItemBase(CompanyBusinessObjectSchema):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(OrderItemBase):
    quantity: Optional[int] = Field(None, ge=1)
    unit_price: Optional[Decimal] = Field(None, ge=0)

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    line_total: Decimal
    product_name: str = None  # From relationship
    
    class Config:
        from_attributes = True

class OrderBase(CompanyBusinessObjectSchema):
    customer_id: int = Field(..., description="Customer ID")
    order_date: datetime = Field(..., description="Order date")
    status: str = Field('draft', regex=r'^(draft|confirmed|shipped|delivered|cancelled)$')
    notes: Optional[str] = Field(None, max_length=1000)

class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate] = Field([], description="Order items")
    
    @validator('order_items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

class OrderUpdate(OrderBase):
    customer_id: Optional[int] = None
    order_date: Optional[datetime] = None
    status: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    order_number: str
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    items_count: int
    customer_name: str = None  # From relationship
    order_items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True
```

### Service Implementation

```python
# app/services/order_service.py
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.framework.services import CompanyBusinessObjectService
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate

class OrderService(CompanyBusinessObjectService[Order, OrderCreate, OrderUpdate]):
    """Order service with related items management"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Order)
    
    async def create_order_with_items(self, order_data: OrderCreate) -> Order:
        """Create order with items in single transaction"""
        # Generate order number
        order_number = await self._generate_order_number()
        
        # Create order
        order_dict = order_data.dict(exclude={'order_items'})
        order_dict['order_number'] = order_number
        
        order = Order(**order_dict)
        self.db.add(order)
        await self.db.flush()  # Get order ID
        
        # Create order items
        for item_data in order_data.order_items:
            item = OrderItem(
                order_id=order.id,
                company_id=order.company_id,
                **item_data.dict()
            )
            item.calculate_line_total()
            self.db.add(item)
        
        # Calculate order totals
        await self.db.flush()  # Ensure items are saved
        await self.db.refresh(order, ['order_items'])
        order.calculate_totals()
        
        await self.db.commit()
        return order
    
    async def get_order_with_items(self, order_id: int, company_id: int) -> Optional[Order]:
        """Get order with all related items loaded"""
        query = (
            select(Order)
            .where(Order.id == order_id)
            .where(Order.company_id == company_id)
            .options(
                selectinload(Order.order_items),
                selectinload(Order.customer)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def add_order_item(self, order_id: int, item_data: OrderItemCreate, company_id: int) -> OrderItem:
        """Add item to existing order"""
        order = await self.get_by_id(order_id, company_id)
        if not order:
            raise ValueError("Order not found")
        
        item = OrderItem(
            order_id=order_id,
            company_id=company_id,
            **item_data.dict()
        )
        item.calculate_line_total()
        self.db.add(item)
        
        # Recalculate order totals
        await self.db.flush()
        await self.db.refresh(order, ['order_items'])
        order.calculate_totals()
        
        await self.db.commit()
        return item
    
    async def update_order_status(self, order_id: int, status: str, company_id: int) -> Optional[Order]:
        """Update order status with validation"""
        valid_transitions = {
            'draft': ['confirmed', 'cancelled'],
            'confirmed': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': [],
            'cancelled': []
        }
        
        order = await self.get_by_id(order_id, company_id)
        if not order:
            return None
        
        if status not in valid_transitions.get(order.status, []):
            raise ValueError(f"Cannot transition from {order.status} to {status}")
        
        order.status = status
        await self.db.commit()
        return order
    
    async def get_orders_by_status(self, status: str, company_id: int) -> List[Order]:
        """Get orders by status"""
        return await self.get_list(
            filters={"status": status},
            company_id=company_id,
            order_by="-order_date"
        )
    
    async def _generate_order_number(self) -> str:
        """Generate unique order number"""
        import uuid
        return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
```

## 📊 Pattern 4: Multi-Status Business Object

**Use Case**: Objects with complex state machines (e.g., Invoice, Ticket, Application)

### Model Implementation

```python
# app/models/invoice.py
from sqlalchemy import Column, String, Integer, Decimal, DateTime, Boolean, Text
from enum import Enum
from app.framework.base import CompanyBaseModel
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Invoice(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin):
    """Invoice with complex status workflow"""
    
    __tablename__ = "invoices"
    
    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(Integer, nullable=False, index=True)
    issue_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default=InvoiceStatus.DRAFT, index=True)
    
    # Amounts
    subtotal = Column(Decimal(12, 2), nullable=False, default=0)
    tax_amount = Column(Decimal(12, 2), nullable=False, default=0)
    total_amount = Column(Decimal(12, 2), nullable=False, default=0)
    paid_amount = Column(Decimal(12, 2), nullable=False, default=0)
    
    # Status tracking
    sent_at = Column(DateTime, nullable=True)
    viewed_at = Column(DateTime, nullable=True)
    first_payment_at = Column(DateTime, nullable=True)
    fully_paid_at = Column(DateTime, nullable=True)
    
    # Settings
    auto_reminders = Column(Boolean, default=True)
    reminder_sent_count = Column(Integer, default=0)
    last_reminder_sent = Column(DateTime, nullable=True)
    
    # Additional info
    terms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        if self.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def balance_due(self) -> Decimal:
        """Calculate remaining balance"""
        return self.total_amount - self.paid_amount
    
    @property
    def days_overdue(self) -> int:
        """Calculate days overdue"""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days
    
    def can_transition_to(self, new_status: InvoiceStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            InvoiceStatus.DRAFT: [InvoiceStatus.SENT, InvoiceStatus.CANCELLED],
            InvoiceStatus.SENT: [InvoiceStatus.VIEWED, InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID, InvoiceStatus.OVERDUE, InvoiceStatus.CANCELLED],
            InvoiceStatus.VIEWED: [InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID, InvoiceStatus.OVERDUE, InvoiceStatus.CANCELLED],
            InvoiceStatus.PARTIALLY_PAID: [InvoiceStatus.PAID, InvoiceStatus.OVERDUE, InvoiceStatus.CANCELLED],
            InvoiceStatus.PAID: [InvoiceStatus.REFUNDED],
            InvoiceStatus.OVERDUE: [InvoiceStatus.PARTIALLY_PAID, InvoiceStatus.PAID, InvoiceStatus.CANCELLED],
            InvoiceStatus.CANCELLED: [],
            InvoiceStatus.REFUNDED: []
        }
        return new_status in valid_transitions.get(self.status, [])
```

### Service Implementation

```python
# app/services/invoice_service.py
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.framework.services import CompanyBusinessObjectService
from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate

class InvoiceService(CompanyBusinessObjectService[Invoice, InvoiceCreate, InvoiceUpdate]):
    """Invoice service with status management"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Invoice)
    
    async def send_invoice(self, invoice_id: int, company_id: int) -> Optional[Invoice]:
        """Send invoice and update status"""
        invoice = await self.get_by_id(invoice_id, company_id)
        if not invoice:
            return None
        
        if not invoice.can_transition_to(InvoiceStatus.SENT):
            raise ValueError(f"Cannot send invoice with status {invoice.status}")
        
        # Update status and timestamp
        invoice.status = InvoiceStatus.SENT
        invoice.sent_at = datetime.utcnow()
        
        # Send email notification (would integrate with email service)
        await self._send_invoice_email(invoice)
        
        await self.db.commit()
        return invoice
    
    async def record_payment(self, invoice_id: int, payment_amount: Decimal, company_id: int) -> Optional[Invoice]:
        """Record payment and update status"""
        invoice = await self.get_by_id(invoice_id, company_id)
        if not invoice:
            return None
        
        if invoice.status in [InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]:
            raise ValueError("Cannot record payment for cancelled or refunded invoice")
        
        # Update paid amount
        old_paid_amount = invoice.paid_amount
        invoice.paid_amount += payment_amount
        
        # Update timestamps
        if old_paid_amount == 0:
            invoice.first_payment_at = datetime.utcnow()
        
        # Determine new status
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = InvoiceStatus.PAID
            invoice.fully_paid_at = datetime.utcnow()
        elif invoice.paid_amount > 0:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        
        await self.db.commit()
        return invoice
    
    async def mark_as_viewed(self, invoice_id: int, company_id: int) -> Optional[Invoice]:
        """Mark invoice as viewed (from customer portal)"""
        invoice = await self.get_by_id(invoice_id, company_id)
        if not invoice:
            return None
        
        if invoice.status == InvoiceStatus.SENT and not invoice.viewed_at:
            invoice.status = InvoiceStatus.VIEWED
            invoice.viewed_at = datetime.utcnow()
            await self.db.commit()
        
        return invoice
    
    async def check_and_update_overdue_invoices(self, company_id: int) -> List[Invoice]:
        """Check for overdue invoices and update status"""
        overdue_invoices = []
        
        # Get invoices that should be overdue
        invoices = await self.get_list(
            filters={
                "status__in": [InvoiceStatus.SENT, InvoiceStatus.VIEWED, InvoiceStatus.PARTIALLY_PAID],
                "due_date__lt": datetime.utcnow()
            },
            company_id=company_id
        )
        
        for invoice in invoices:
            if invoice.can_transition_to(InvoiceStatus.OVERDUE):
                invoice.status = InvoiceStatus.OVERDUE
                overdue_invoices.append(invoice)
        
        if overdue_invoices:
            await self.db.commit()
        
        return overdue_invoices
    
    async def send_reminder(self, invoice_id: int, company_id: int) -> bool:
        """Send payment reminder"""
        invoice = await self.get_by_id(invoice_id, company_id)
        if not invoice:
            return False
        
        if not invoice.auto_reminders:
            return False
        
        if invoice.status not in [InvoiceStatus.SENT, InvoiceStatus.VIEWED, InvoiceStatus.OVERDUE]:
            return False
        
        # Send reminder email
        await self._send_reminder_email(invoice)
        
        # Update reminder tracking
        invoice.reminder_sent_count += 1
        invoice.last_reminder_sent = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def get_invoice_analytics(self, company_id: int, days: int = 30) -> Dict[str, Any]:
        """Get invoice analytics for dashboard"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get invoices from the period
        invoices = await self.get_list(
            filters={"issue_date__gte": since_date},
            company_id=company_id
        )
        
        total_amount = sum(inv.total_amount for inv in invoices)
        paid_amount = sum(inv.paid_amount for inv in invoices)
        
        status_counts = {}
        for status in InvoiceStatus:
            status_counts[status.value] = len([inv for inv in invoices if inv.status == status])
        
        overdue_amount = sum(
            inv.balance_due for inv in invoices 
            if inv.status == InvoiceStatus.OVERDUE
        )
        
        return {
            "period_days": days,
            "total_invoices": len(invoices),
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "outstanding_amount": total_amount - paid_amount,
            "overdue_amount": overdue_amount,
            "status_counts": status_counts,
            "average_invoice_amount": total_amount / len(invoices) if invoices else 0
        }
    
    async def _send_invoice_email(self, invoice: Invoice):
        """Send invoice email (integrate with email service)"""
        # This would integrate with your email service
        pass
    
    async def _send_reminder_email(self, invoice: Invoice):
        """Send reminder email (integrate with email service)"""
        # This would integrate with your email service
        pass
```

## ⚙️ Pattern 5: Configurable Business Object

**Use Case**: Objects with dynamic configuration (e.g., Product with variants, Service with options)

### Model Implementation

```python
# app/models/service_offering.py
from sqlalchemy import Column, String, Text, Boolean, Integer, Decimal, JSON
from app.framework.base import CompanyBaseModel
from app.framework.mixins import BusinessObjectMixin, AuditableMixin, EventPublisherMixin, ExtensibleMixin

class ServiceOffering(CompanyBaseModel, BusinessObjectMixin, AuditableMixin, EventPublisherMixin, ExtensibleMixin):
    """Configurable service offering"""
    
    __tablename__ = "service_offerings"
    
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, index=True)
    base_price = Column(Decimal(10, 2), nullable=False)
    
    # Configuration
    is_configurable = Column(Boolean, default=False)
    configuration_schema = Column(JSON, nullable=True)  # JSON schema for configuration
    default_configuration = Column(JSON, nullable=True)  # Default values
    
    # Pricing model
    pricing_model = Column(String(20), default='fixed')  # fixed, hourly, usage_based
    min_price = Column(Decimal(10, 2), nullable=True)
    max_price = Column(Decimal(10, 2), nullable=True)
    
    # Availability
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    max_concurrent_instances = Column(Integer, nullable=True)
    
    @property
    def configuration_options(self) -> Dict[str, Any]:
        """Get available configuration options"""
        if not self.configuration_schema:
            return {}
        return self.configuration_schema.get('properties', {})
    
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate configuration against schema"""
        if not self.is_configurable:
            return True
        
        # This would use jsonschema library for validation
        # import jsonschema
        # try:
        #     jsonschema.validate(config, self.configuration_schema)
        #     return True
        # except jsonschema.ValidationError:
        #     return False
        return True
    
    def calculate_price(self, configuration: Dict[str, Any], quantity: int = 1) -> Decimal:
        """Calculate price based on configuration"""
        base_price = self.base_price
        
        if self.pricing_model == 'fixed':
            return base_price * quantity
        
        # Add configuration-based pricing logic
        multiplier = Decimal('1.0')
        
        for option, value in configuration.items():
            option_config = self.configuration_options.get(option, {})
            price_modifier = option_config.get('price_modifier', 0)
            
            if isinstance(value, bool) and value:
                multiplier += Decimal(str(price_modifier))
            elif isinstance(value, (int, float)):
                multiplier += Decimal(str(price_modifier)) * Decimal(str(value))
        
        calculated_price = base_price * multiplier * quantity
        
        # Apply min/max constraints
        if self.min_price and calculated_price < self.min_price:
            calculated_price = self.min_price
        if self.max_price and calculated_price > self.max_price:
            calculated_price = self.max_price
        
        return calculated_price
```

### Schema Implementation

```python
# app/schemas/service_offering.py
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import Field, validator, root_validator
from app.framework.schemas import CompanyBusinessObjectSchema

class ServiceOfferingBase(CompanyBusinessObjectSchema):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    category: str = Field(..., min_length=1, max_length=100)
    base_price: Decimal = Field(..., ge=0)
    is_configurable: bool = Field(False)
    pricing_model: str = Field('fixed', regex=r'^(fixed|hourly|usage_based)$')
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    requires_approval: bool = Field(False)
    max_concurrent_instances: Optional[int] = Field(None, ge=1)
    
    @root_validator
    def validate_price_range(cls, values):
        min_price = values.get('min_price')
        max_price = values.get('max_price')
        base_price = values.get('base_price')
        
        if min_price and max_price and min_price > max_price:
            raise ValueError('min_price cannot be greater than max_price')
        
        if min_price and base_price and base_price < min_price:
            raise ValueError('base_price cannot be less than min_price')
        
        return values

class ServiceOfferingConfigurationSchema(BaseModel):
    """Schema for service configuration"""
    properties: Dict[str, Any] = Field({}, description="Configuration properties")
    required: List[str] = Field([], description="Required configuration fields")
    
class ServiceOfferingCreate(ServiceOfferingBase):
    configuration_schema: Optional[ServiceOfferingConfigurationSchema] = None
    default_configuration: Optional[Dict[str, Any]] = None

class ServiceOfferingUpdate(ServiceOfferingBase):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    base_price: Optional[Decimal] = Field(None, ge=0)

class ServiceOfferingResponse(ServiceOfferingBase):
    id: int
    is_active: bool
    configuration_schema: Optional[Dict[str, Any]] = None
    default_configuration: Optional[Dict[str, Any]] = None
    configuration_options: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True

class ServiceConfigurationRequest(BaseModel):
    """Request to configure a service instance"""
    service_offering_id: int
    configuration: Dict[str, Any] = {}
    quantity: int = Field(1, ge=1)

class ServiceConfigurationResponse(BaseModel):
    """Response with configured service details"""
    service_offering: ServiceOfferingResponse
    configuration: Dict[str, Any]
    quantity: int
    calculated_price: Decimal
    is_valid: bool
    validation_errors: List[str] = []
```

### Service Implementation

```python
# app/services/service_offering_service.py
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.framework.services import CompanyBusinessObjectService
from app.models.service_offering import ServiceOffering
from app.schemas.service_offering import ServiceOfferingCreate, ServiceOfferingUpdate, ServiceConfigurationRequest

class ServiceOfferingService(CompanyBusinessObjectService[ServiceOffering, ServiceOfferingCreate, ServiceOfferingUpdate]):
    """Configurable service offering service"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ServiceOffering)
    
    async def configure_service(self, config_request: ServiceConfigurationRequest, company_id: int) -> Dict[str, Any]:
        """Configure a service with custom options"""
        service = await self.get_by_id(config_request.service_offering_id, company_id)
        if not service:
            raise ValueError("Service offering not found")
        
        if not service.is_active:
            raise ValueError("Service offering is not available")
        
        # Validate configuration
        validation_errors = []
        is_valid = True
        
        if service.is_configurable:
            if not service.validate_configuration(config_request.configuration):
                is_valid = False
                validation_errors.append("Invalid configuration")
            
            # Check required fields
            required_fields = service.configuration_schema.get('required', []) if service.configuration_schema else []
            for field in required_fields:
                if field not in config_request.configuration:
                    is_valid = False
                    validation_errors.append(f"Required field missing: {field}")
        
        # Calculate price
        calculated_price = service.calculate_price(
            config_request.configuration,
            config_request.quantity
        )
        
        return {
            "service_offering": service,
            "configuration": config_request.configuration,
            "quantity": config_request.quantity,
            "calculated_price": calculated_price,
            "is_valid": is_valid,
            "validation_errors": validation_errors
        }
    
    async def create_service_template(self, service_id: int, template_name: str, configuration: Dict[str, Any], company_id: int) -> None:
        """Save configuration as template for reuse"""
        service = await self.get_by_id(service_id, company_id)
        if not service:
            raise ValueError("Service offering not found")
        
        # Store as custom field
        await self.set_extension(
            entity_id=service_id,
            field_name=f"template_{template_name}",
            field_type="json",
            field_value=json.dumps(configuration),
            metadata={
                "template_name": template_name,
                "created_by": "system"  # Would use actual user ID
            }
        )
    
    async def get_service_templates(self, service_id: int, company_id: int) -> List[Dict[str, Any]]:
        """Get saved configuration templates"""
        extensions = await self.get_extensions(service_id)
        
        templates = []
        for field_name, extension in extensions.items():
            if field_name.startswith("template_"):
                template_name = field_name.replace("template_", "")
                try:
                    configuration = json.loads(extension.field_value)
                    templates.append({
                        "name": template_name,
                        "configuration": configuration,
                        "created_at": extension.created_at
                    })
                except json.JSONDecodeError:
                    continue
        
        return templates
    
    async def get_popular_configurations(self, service_id: int, company_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most popular configurations (would require usage tracking)"""
        # This would analyze usage data to find popular configurations
        # For now, return empty list
        return []
    
    async def estimate_service_usage(self, service_id: int, configuration: Dict[str, Any], estimated_usage: Dict[str, Any], company_id: int) -> Dict[str, Any]:
        """Estimate costs based on usage patterns"""
        service = await self.get_by_id(service_id, company_id)
        if not service:
            raise ValueError("Service offering not found")
        
        if service.pricing_model == 'usage_based':
            # Calculate based on usage metrics
            base_cost = service.calculate_price(configuration, 1)
            
            # Apply usage multipliers
            usage_multiplier = Decimal('1.0')
            for metric, value in estimated_usage.items():
                # This would use service-specific usage calculation logic
                usage_multiplier += Decimal(str(value)) * Decimal('0.1')  # Example calculation
            
            estimated_monthly_cost = base_cost * usage_multiplier
            
            return {
                "base_monthly_cost": base_cost,
                "usage_multiplier": usage_multiplier,
                "estimated_monthly_cost": estimated_monthly_cost,
                "estimated_annual_cost": estimated_monthly_cost * 12
            }
        
        else:
            # Fixed or hourly pricing
            monthly_cost = service.calculate_price(configuration, 1)
            return {
                "monthly_cost": monthly_cost,
                "annual_cost": monthly_cost * 12
            }
```

This covers 5 comprehensive patterns. Each pattern demonstrates different aspects of the Business Object Framework:

1. **Simple Business Object**: Basic CRUD with validation
2. **Hierarchical Business Object**: Tree structures with parent-child relationships  
3. **Business Object with Relationships**: Complex object graphs with related entities
4. **Multi-Status Business Object**: State machines and workflow management
5. **Configurable Business Object**: Dynamic configuration with custom fields

Each pattern includes complete implementations showing:
- Model design with appropriate mixins
- Schema validation and serialization
- Service layer with business logic
- Custom endpoints and functionality
- Real-world business scenarios

The patterns can be combined and extended for more complex use cases. The framework provides the foundation while allowing complete customization for specific business needs.

Would you like me to continue with the remaining patterns (6-10) covering Approval Workflows, Document Management, Time-Based Objects, Batch Processing, and Integration-Heavy patterns?