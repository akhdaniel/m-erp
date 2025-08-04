#!/usr/bin/env python3
"""
Migration Rollback Script

This script provides safe rollback from the Business Object Framework
back to the original Partner implementation.

Usage:
    python rollback_migration.py [--confirm]
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime


def rollback_migration(confirm: bool = False):
    """Rollback from framework to original implementation."""
    
    if not confirm:
        print("⚠️  This will rollback to the original Partner implementation.")
        print("   Framework features will be disabled:")
        print("   • Custom fields")
        print("   • Enhanced audit logging")
        print("   • Event publishing")
        print("   • Bulk operations")
        print("   • Auto-generated documentation")
        print()
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Rollback cancelled.")
            return False
    
    try:
        print("🔄 Starting rollback to original implementation...")
        
        # Check if backup exists
        original_backup = Path("app/main_original.py")
        if not original_backup.exists():
            print("❌ Original main.py backup not found!")
            print("   You may need to manually restore from migrations/backups/")
            return False
        
        # Restore original main.py
        shutil.copy2(original_backup, "app/main.py")
        print("✅ Restored original main.py")
        
        # Update migration status
        status_file = Path("app/migration_status.json")
        if status_file.exists():
            import json
            status = {
                "framework_enabled": False,
                "implementation": "original",
                "rollback_date": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            }
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
            print("✅ Updated migration status")
        
        print("\n✅ Rollback completed successfully!")
        print("📋 Next steps:")
        print("  1. Restart the application")
        print("  2. Test API endpoints: /api/v1/partners/")
        print("  3. Verify original functionality works correctly")
        print("  4. Framework files remain available in app/framework_migration/")
        
        return True
        
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        return False


def main():
    """Main rollback script entry point."""
    parser = argparse.ArgumentParser(description="Rollback Partner service migration")
    parser.add_argument("--confirm", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    success = rollback_migration(args.confirm)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())