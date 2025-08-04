"""
Product management services for inventory catalog operations.

Provides business logic for products, categories, variants,
and product-related operations with validation and integration.
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import time
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from inventory_module.models import Product, ProductCategory, ProductVariant, ProductType, ProductStatus
from inventory_module.services.base_service import BaseService, ServiceError, ValidationError, NotFoundError


class ProductCategoryService(BaseService):
    """
    Product Category Service for managing product categorization.
    
    Handles hierarchical category structure, category management,
    and category-related operations.
    """
    
    def create_category(self, name: str, code: str, description: str = None,
                       parent_category_id: int = None, **kwargs) -> ProductCategory:
        """Create a new product category."""
        # Validate parent category exists if specified
        if parent_category_id:
            parent = self.get_by_id_or_raise(ProductCategory, parent_category_id)
            if not parent.is_active:
                raise ValidationError("Parent category must be active")
        
        # Check for duplicate code within company
        existing = self.db.query(ProductCategory).filter(
            and_(
                ProductCategory.code == code,
                ProductCategory.company_id == self.company_id
            )
        ).first()
        
        if existing:
            raise ValidationError(f"Category code '{code}' already exists")
        
        category_data = {
            'name': name,
            'code': code,
            'description': description,
            'parent_category_id': parent_category_id,
            **kwargs
        }
        
        category = self.create(ProductCategory, category_data)
        
        # Update parent category product count
        if parent_category_id:
            self._update_category_product_count(parent_category_id)
        
        return category
    
    def get_root_categories(self) -> List[ProductCategory]:
        """Get all root-level categories (no parent)."""
        query = self.db.query(ProductCategory).filter(
            ProductCategory.parent_category_id.is_(None)
        )
        query = self._apply_company_filter(query, ProductCategory)
        query = query.filter(ProductCategory.is_active == True)
        query = query.order_by(ProductCategory.display_order, ProductCategory.name)
        
        return query.all()
    
    def get_child_categories(self, parent_id: int) -> List[ProductCategory]:
        """Get child categories of a parent category."""
        query = self.db.query(ProductCategory).filter(
            ProductCategory.parent_category_id == parent_id
        )
        query = self._apply_company_filter(query, ProductCategory)
        query = query.filter(ProductCategory.is_active == True)
        query = query.order_by(ProductCategory.display_order, ProductCategory.name)
        
        return query.all()
    
    def get_category_tree(self, root_id: int = None) -> List[Dict[str, Any]]:
        """Get hierarchical category tree structure."""
        if root_id:
            categories = self.get_child_categories(root_id)
        else:
            categories = self.get_root_categories()
        
        tree = []
        for category in categories:
            category_dict = category.to_dict()
            category_dict['children'] = self.get_category_tree(category.id)
            tree.append(category_dict)
        
        return tree
    
    def move_category(self, category_id: int, new_parent_id: int = None) -> ProductCategory:
        """Move category to a new parent."""
        category = self.get_by_id_or_raise(ProductCategory, category_id)
        old_parent_id = category.parent_category_id
        
        # Validate new parent
        if new_parent_id:
            new_parent = self.get_by_id_or_raise(ProductCategory, new_parent_id)
            if not new_parent.is_active:
                raise ValidationError("New parent category must be active")
            
            # Prevent circular references
            if self._would_create_circular_reference(category_id, new_parent_id):
                raise ValidationError("Moving category would create circular reference")
        
        # Update category
        category.parent_category_id = new_parent_id
        
        # Update product counts
        if old_parent_id:
            self._update_category_product_count(old_parent_id)
        if new_parent_id:
            self._update_category_product_count(new_parent_id)
        
        return category
    
    def _would_create_circular_reference(self, category_id: int, new_parent_id: int) -> bool:
        """Check if moving category would create circular reference."""
        current_id = new_parent_id
        while current_id:
            if current_id == category_id:
                return True
            
            parent = self.get_by_id(ProductCategory, current_id)
            current_id = parent.parent_category_id if parent else None
        
        return False
    
    def _update_category_product_count(self, category_id: int) -> None:
        """Update product count for a category."""
        count = self.db.query(func.count(Product.id)).filter(
            Product.category_id == category_id
        ).scalar()
        
        category = self.get_by_id(ProductCategory, category_id)
        if category:
            category.product_count = count


class ProductService(BaseService):
    """
    Product Service for managing product catalog.
    
    Handles product creation, updates, pricing, inventory settings,
    and product lifecycle management.
    """
    
    def create_product(self, name: str, sku: str = None, 
                      product_type: ProductType = ProductType.PHYSICAL,
                      **kwargs) -> Product:
        """Create a new product."""
        # Generate SKU if not provided
        if not sku:
            sku = self._generate_sku(kwargs.get('sku_prefix', 'PRD'))
        
        # Validate SKU uniqueness
        existing = self.db.query(Product).filter(Product.sku == sku).first()
        if existing:
            raise ValidationError(f"SKU '{sku}' already exists")
        
        # Validate category if specified
        category_id = kwargs.get('category_id')
        if category_id:
            category = self.get_by_id_or_raise(ProductCategory, category_id)
            if not category.is_active:
                raise ValidationError("Product category must be active")
        
        product_data = {
            'name': name,
            'sku': sku,
            'product_type': product_type,
            **kwargs
        }
        
        product = self.create(Product, product_data)
        
        # Update category product count
        if category_id:
            category_service = ProductCategoryService(self.db, self.user_id, self.company_id)
            category_service._update_category_product_count(category_id)
        
        return product
    
    def update_product_pricing(self, product_id: int, list_price: Decimal = None,
                              cost_price: Decimal = None) -> Product:
        """Update product pricing information."""
        product = self.get_by_id_or_raise(Product, product_id)
        
        update_data = {}
        if list_price is not None:
            if list_price < 0:
                raise ValidationError("List price cannot be negative")
            update_data['list_price'] = list_price
        
        if cost_price is not None:
            if cost_price < 0:
                raise ValidationError("Cost price cannot be negative")
            update_data['cost_price'] = cost_price
        
        # Validate pricing relationship
        if (list_price or product.list_price) and (cost_price or product.cost_price):
            final_list = list_price if list_price is not None else product.list_price
            final_cost = cost_price if cost_price is not None else product.cost_price
            
            if final_list < final_cost:
                raise ValidationError("List price should not be less than cost price")
        
        return self.update(product, update_data)
    
    def update_inventory_settings(self, product_id: int, 
                                 minimum_stock_level: Decimal = None,
                                 maximum_stock_level: Decimal = None,
                                 reorder_point: Decimal = None,
                                 reorder_quantity: Decimal = None,
                                 **kwargs) -> Product:
        """Update product inventory management settings."""
        product = self.get_by_id_or_raise(Product, product_id)
        
        update_data = {}
        if minimum_stock_level is not None:
            update_data['minimum_stock_level'] = minimum_stock_level
        if maximum_stock_level is not None:
            update_data['maximum_stock_level'] = maximum_stock_level
        if reorder_point is not None:
            update_data['reorder_point'] = reorder_point
        if reorder_quantity is not None:
            update_data['reorder_quantity'] = reorder_quantity
        
        # Add other inventory settings
        update_data.update(kwargs)
        
        return self.update(product, update_data)
    
    def get_products_by_category(self, category_id: int, 
                                include_subcategories: bool = False,
                                active_only: bool = True) -> List[Product]:
        """Get products in a specific category."""
        category_ids = [category_id]
        
        if include_subcategories:
            # Get all descendant category IDs
            category = self.get_by_id_or_raise(ProductCategory, category_id)
            category_ids.extend(category.get_all_child_ids())
        
        query = self.db.query(Product).filter(
            Product.category_id.in_(category_ids)
        )
        
        if active_only:
            query = query.filter(Product.is_active == True)
        
        query = self._apply_company_filter(query, Product)
        query = query.order_by(Product.name)
        
        return query.all()
    
    def search_products(self, search_term: str, 
                       category_id: int = None,
                       product_type: ProductType = None,
                       status: ProductStatus = None,
                       limit: int = 50) -> List[Product]:
        """Search products by various criteria."""
        search_fields = ['name', 'sku', 'description', 'manufacturer_part_number']
        query = self.db.query(Product)
        
        # Apply text search
        search_conditions = []
        for field in search_fields:
            if hasattr(Product, field):
                field_attr = getattr(Product, field)
                search_conditions.append(field_attr.ilike(f"%{search_term}%"))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if product_type:
            query = query.filter(Product.product_type == product_type)
        if status:
            query = query.filter(Product.status == status)
        
        query = self._apply_company_filter(query, Product)
        query = query.filter(Product.is_active == True)
        query = query.order_by(Product.name)
        
        return query.limit(limit).all()
    
    def get_low_stock_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get products with low stock levels."""
        # This would integrate with StockService in production
        query = self.db.query(Product).filter(
            and_(
                Product.track_inventory == True,
                Product.reorder_point.isnot(None),
                Product.is_active == True
            )
        )
        
        query = self._apply_company_filter(query, Product)
        products = query.limit(limit).all()
        
        # In production, would check actual stock levels
        return [
            {
                'product_id': p.id,
                'name': p.name,
                'sku': p.sku,
                'reorder_point': p.reorder_point,
                'current_stock': Decimal('0.00')  # Would get from StockService
            }
            for p in products
        ]
    
    def discontinue_product(self, product_id: int, 
                           discontinuation_date: datetime = None) -> Product:
        """Discontinue a product."""
        product = self.get_by_id_or_raise(Product, product_id)
        
        update_data = {
            'status': ProductStatus.DISCONTINUED,
            'discontinued_date': discontinuation_date or datetime.utcnow()
        }
        
        return self.update(product, update_data)
    
    def _generate_sku(self, prefix: str = "PRD") -> str:
        """Generate unique SKU."""
        # In production, would use company settings and sequence numbers
        import time
        timestamp = int(time.time())
        return f"{prefix}{timestamp:08d}"


class ProductVariantService(BaseService):
    """
    Product Variant Service for managing product variations.
    
    Handles variant creation, attribute management, and
    variant-specific pricing and inventory settings.
    """
    
    def create_variant(self, parent_product_id: int, variant_name: str,
                      attributes: Dict[str, str], sku: str = None,
                      **kwargs) -> ProductVariant:
        """Create a new product variant."""
        # Validate parent product
        parent_product = self.get_by_id_or_raise(Product, parent_product_id)
        if not parent_product.is_active:
            raise ValidationError("Parent product must be active")
        
        # Generate SKU if not provided
        if not sku:
            sku = f"{parent_product.sku}-VAR{int(time.time() % 10000):04d}"
        
        # Validate SKU uniqueness
        existing = self.db.query(ProductVariant).filter(ProductVariant.sku == sku).first()
        if existing:
            raise ValidationError(f"Variant SKU '{sku}' already exists")
        
        variant_data = {
            'parent_product_id': parent_product_id,
            'variant_name': variant_name,
            'sku': sku,
            'attributes': attributes,
            **kwargs
        }
        
        variant = self.create(ProductVariant, variant_data)
        
        return variant
    
    def get_product_variants(self, parent_product_id: int, 
                            active_only: bool = True) -> List[ProductVariant]:
        """Get all variants for a product."""
        query = self.db.query(ProductVariant).filter(
            ProductVariant.parent_product_id == parent_product_id
        )
        
        if active_only:
            query = query.filter(ProductVariant.is_active == True)
        
        query = self._apply_company_filter(query, ProductVariant)
        query = query.order_by(ProductVariant.variant_name)
        
        return query.all()
    
    def search_variants_by_attributes(self, attributes: Dict[str, str],
                                     parent_product_id: int = None) -> List[ProductVariant]:
        """Search variants by attribute values."""
        query = self.db.query(ProductVariant)
        
        if parent_product_id:
            query = query.filter(ProductVariant.parent_product_id == parent_product_id)
        
        # Filter by attributes (simplified - would use JSON operators in production)
        for attr_name, attr_value in attributes.items():
            query = query.filter(
                ProductVariant.attributes.op('->')(attr_name).astext == attr_value
            )
        
        query = self._apply_company_filter(query, ProductVariant)
        query = query.filter(ProductVariant.is_active == True)
        
        return query.all()
    
    def update_variant_attributes(self, variant_id: int, 
                                 attributes: Dict[str, str]) -> ProductVariant:
        """Update variant attributes."""
        variant = self.get_by_id_or_raise(ProductVariant, variant_id)
        
        # Merge with existing attributes
        current_attributes = variant.attributes or {}
        current_attributes.update(attributes)
        
        return self.update(variant, {'attributes': current_attributes})
    
    def get_unique_attribute_values(self, parent_product_id: int,
                                   attribute_name: str) -> List[str]:
        """Get unique values for a specific attribute across variants."""
        # In production, would use JSON operators to extract attribute values
        variants = self.get_product_variants(parent_product_id)
        
        values = set()
        for variant in variants:
            if variant.attributes and attribute_name in variant.attributes:
                values.add(variant.attributes[attribute_name])
        
        return sorted(list(values))