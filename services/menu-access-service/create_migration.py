#!/usr/bin/env python3
"""
Create initial database migration for Menu & Access Rights Service.
"""

import subprocess
import sys
import os

def main():
    """Create the initial migration."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Create initial migration
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", 
            "-m", "Create initial tables"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration created successfully!")
            print(result.stdout)
        else:
            print("❌ Migration creation failed!")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()