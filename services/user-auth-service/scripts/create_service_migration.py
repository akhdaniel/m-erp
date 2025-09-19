#!/usr/bin/env python3
"""
Script to create a new migration for Service models.
"""

import subprocess
import sys
import os

def create_migration():
    """Create Alembic migration for Service models."""
    print("Creating migration for Service models...")
    
    # Change to the project directory
    os.chdir('/Users/daniel/data/m-erp/services/user-auth-service')
    
    try:
        # Run alembic revision
        result = subprocess.run([
            'alembic', 'revision', '--autogenerate', 
            '-m', 'Add service authentication tables'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Migration created successfully!")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create migration: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install dependencies first:")
        print("pip install alembic")
        return False

if __name__ == "__main__":
    success = create_migration()
    sys.exit(0 if success else 1)