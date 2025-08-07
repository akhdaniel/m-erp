#!/usr/bin/env python3
"""
Initialize inventory database tables.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from inventory_module.database import DATABASE_URL
from inventory_module.framework.base import Base

# Import all models to register them with Base
from inventory_module.models import (
    Product, ProductVariant, ProductCategory,
    StockLevel, StockMovement,
    Warehouse, WarehouseLocation,
    ReceivingRecord, ReceivingLineItem
)

def init_database():
    """Create all database tables."""
    print(f"Connecting to database: {DATABASE_URL}")
    
    # Create engine
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()