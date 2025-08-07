"""
Menu model for dynamic navigation system.
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey, JSON, CheckConstraint
from sqlalchemy.orm import relationship, backref

from app.models.base import BaseModel


class MenuItem(BaseModel):
    """
    Menu item model for dynamic navigation system.
    
    Supports hierarchical menu structures with permission-based visibility.
    """
    
    __tablename__ = "menu_items"
    
    # Menu item identification
    code = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Menu hierarchy
    parent_id = Column(
        Integer, 
        ForeignKey("menu_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    order_index = Column(Integer, default=0, nullable=False)  # Ordering within parent
    level = Column(Integer, default=0, nullable=False)  # Depth level for performance
    
    # Navigation properties
    url = Column(String(500))  # URL path or route
    icon = Column(String(100))  # Icon class or name
    target = Column(String(20), default="_self")  # Link target (_self, _blank, etc.)
    
    # Menu item type and behavior
    item_type = Column(String(20), default="link", nullable=False)  # link, divider, header, dropdown
    is_external = Column(Boolean, default=False, nullable=False)  # External URL
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_visible = Column(Boolean, default=True, nullable=False)
    
    # Permission requirements
    required_permission = Column(String(100))  # Permission code required to see this menu item
    required_role_level = Column(Integer)  # Minimum role level required
    
    # Additional configuration
    metadata_info = Column(JSON, default=dict)  # Additional menu configuration
    css_class = Column(String(255))  # Custom CSS classes
    
    # Relationships
    
    # Constraints
    __table_args__ = (
        CheckConstraint("level >= 0", name="menu_items_level_check"),
        CheckConstraint("order_index >= 0", name="menu_items_order_check"),
        CheckConstraint(
            "item_type IN ('link', 'divider', 'header', 'dropdown')", 
            name="menu_items_type_check"
        ),
        {'extend_existing': True}
    )
    
    def __str__(self):
        """String representation of the menu item."""
        return f"MenuItem(code='{self.code}', title='{self.title}')"
    
    def __repr__(self):
        """Detailed representation of the menu item."""
        return (
            f"MenuItem(id={self.id}, code='{self.code}', title='{self.title}', "
            f"level={self.level}, active={self.is_active})"
        )
    
    @property
    def full_path(self) -> str:
        """Get full menu path from root to this item."""
        if self.parent:
            return f"{self.parent.full_path} > {self.title}"
        return self.title
    
    def can_access(self, user_permissions: list[str], user_role_level: int = 999) -> bool:
        """Check if user can access this menu item based on permissions and role level."""
        # Check if menu item is active and visible
        if not self.is_active or not self.is_visible:
            return False
        
        # Check permission requirement
        if self.required_permission:
            if self.required_permission not in user_permissions:
                return False
        
        # Check role level requirement
        if self.required_role_level is not None:
            if user_role_level > self.required_role_level:
                return False
        
        return True


# Define self-referential relationship after class definition
MenuItem.parent = relationship(
    "MenuItem", 
    remote_side=[MenuItem.id],
    backref=backref("children", cascade="all, delete-orphan", order_by=MenuItem.order_index)
)