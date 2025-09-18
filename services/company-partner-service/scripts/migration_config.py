#!/usr/bin/env python3
"""
Migration Configuration and Control Script

This script controls the migration from traditional Partner implementation
to the Business Object Framework implementation. It provides safe switching
between implementations and rollback capabilities.

Usage:
    python migration_config.py --enable-framework    # Switch to framework
    python migration_config.py --disable-framework   # Switch back to original
    python migration_config.py --status             # Check current status
    python migration_config.py --validate           # Validate both implementations
"""

import os
import sys
import argparse
import importlib
from pathlib import Path
from typing import Dict, Any, Tuple
import asyncio


class MigrationController:
    """Controls migration between original and framework Partner implementations."""
    
    def __init__(self, service_root: str = "."):
        self.service_root = Path(service_root)
        self.config_file = self.service_root / "app" / "migration_status.json"
        
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        try:
            import json
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Default status
        return {
            "framework_enabled": False,
            "migration_date": None,
            "rollback_available": True,
            "implementation": "original"
        }
    
    def set_migration_status(self, status: Dict[str, Any]) -> bool:
        """Set migration status."""
        try:
            import json
            from datetime import datetime
            
            status["last_updated"] = datetime.utcnow().isoformat()
            
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(status, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Failed to save migration status: {e}")
            return False
    
    def validate_implementations(self) -> Tuple[bool, bool]:
        """Validate both original and framework implementations."""
        print("🔍 Validating implementations...")
        
        # Check original implementation
        original_valid = self._validate_original()
        framework_valid = self._validate_framework()
        
        print(f"Original implementation: {'✅ Valid' if original_valid else '❌ Invalid'}")
        print(f"Framework implementation: {'✅ Valid' if framework_valid else '❌ Invalid'}")
        
        return original_valid, framework_valid
    
    def _validate_original(self) -> bool:
        """Validate original implementation exists and is functional."""
        try:
            # Check original files exist
            original_files = [
                "app/schemas/partner.py",
                "app/services/partner_service.py",
                "app/routers/partners.py"
            ]
            
            for file_path in original_files:
                full_path = self.service_root / file_path
                if not full_path.exists():
                    print(f"❌ Missing original file: {file_path}")
                    return False
            
            # Try importing original modules
            sys.path.insert(0, str(self.service_root))
            
            from app.schemas.partner import PartnerCreate, PartnerUpdate, PartnerResponse
            from app.services.partner_service import PartnerService
            from app.routers.partners import router
            
            return True
        except Exception as e:
            print(f"❌ Original implementation validation failed: {e}")
            return False
    
    def _validate_framework(self) -> bool:
        """Validate framework implementation exists and is functional."""
        try:
            # Check framework files exist
            framework_files = [
                "app/framework_migration/partner_schemas.py",
                "app/framework_migration/partner_service.py",
                "app/framework_migration/partner_router.py"
            ]
            
            for file_path in framework_files:
                full_path = self.service_root / file_path
                if not full_path.exists():
                    print(f"❌ Missing framework file: {file_path}")
                    return False
            
            # Try importing framework modules
            sys.path.insert(0, str(self.service_root))
            
            from app.framework_migration.partner_schemas import (
                PartnerFrameworkCreate, PartnerFrameworkUpdate, PartnerFrameworkResponse
            )
            from app.framework_migration.partner_service import PartnerFrameworkService
            from app.framework_migration.partner_router import router, framework_partner_router
            
            return True
        except Exception as e:
            print(f"❌ Framework implementation validation failed: {e}")
            return False
    
    def enable_framework(self) -> bool:
        """Enable framework implementation."""
        print("🚀 Enabling Business Object Framework implementation...")
        
        # Validate both implementations first
        original_valid, framework_valid = self.validate_implementations()
        
        if not framework_valid:
            print("❌ Framework implementation is not valid. Cannot enable.")
            return False
        
        if not original_valid:
            print("⚠️  Original implementation not valid. Proceeding with framework only.")
        
        # Create framework main.py
        if not self._create_framework_main():
            return False
        
        # Update migration status
        status = self.get_migration_status()
        status.update({
            "framework_enabled": True,
            "migration_date": None,  # Will be set by set_migration_status
            "implementation": "framework",
            "rollback_available": original_valid
        })
        
        if not self.set_migration_status(status):
            return False
        
        print("✅ Framework implementation enabled successfully!")
        print("📋 Next steps:")
        print("  1. Restart the application")
        print("  2. Test API endpoints: /api/v1/partners-framework/")
        print("  3. Verify new framework features work correctly")
        print("  4. Use --disable-framework to rollback if needed")
        
        return True
    
    def disable_framework(self) -> bool:
        """Disable framework implementation and return to original."""
        print("🔄 Disabling framework implementation...")
        
        status = self.get_migration_status()
        if not status["framework_enabled"]:
            print("ℹ️  Framework is not currently enabled.")
            return True
        
        # Validate original implementation
        original_valid, _ = self.validate_implementations()
        
        if not original_valid:
            print("❌ Original implementation is not valid. Cannot rollback.")
            print("💡 You may need to restore from backup:")
            print("   cp migrations/backups/TIMESTAMP/app/schemas/partner.py app/schemas/")
            print("   cp migrations/backups/TIMESTAMP/app/services/partner_service.py app/services/")
            print("   cp migrations/backups/TIMESTAMP/app/routers/partners.py app/routers/")
            return False
        
        # Restore original main.py if framework main exists
        framework_main = self.service_root / "app" / "main_framework.py"
        original_main = self.service_root / "app" / "main.py"
        original_backup = self.service_root / "app" / "main_original.py"
        
        if framework_main.exists() and original_backup.exists():
            # Restore original main.py
            import shutil
            shutil.copy2(original_backup, original_main)
            print("✅ Restored original main.py")
        
        # Update migration status
        status.update({
            "framework_enabled": False,
            "implementation": "original"
        })
        
        if not self.set_migration_status(status):
            return False
        
        print("✅ Framework implementation disabled successfully!")
        print("📋 Application is now using original implementation")
        print("  1. Restart the application")
        print("  2. Test API endpoints: /api/v1/partners/")
        
        return True
    
    def _create_framework_main(self) -> bool:
        """Create framework-enabled main.py."""
        try:
            original_main = self.service_root / "app" / "main.py"
            framework_main = self.service_root / "app" / "main_framework.py"
            original_backup = self.service_root / "app" / "main_original.py"
            
            # Backup original main.py
            if original_main.exists() and not original_backup.exists():
                import shutil
                shutil.copy2(original_main, original_backup)
                print("✅ Backed up original main.py")
            
            # Create framework-enabled main.py
            framework_main_content = '''import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_db, get_db
from app.middleware.auth import auth_client
from app.services.messaging_service import init_messaging, shutdown_messaging

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Company & Partner Management Service (Framework Mode)...")
    logger.info("Database migrations handled by startup script")
    
    # Initialize messaging service
    try:
        await init_messaging()
        logger.info("✓ Messaging service initialized")
    except Exception as e:
        logger.error(f"Messaging service initialization error: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Company & Partner Management Service...")
    
    # Shutdown messaging service
    try:
        await shutdown_messaging()
        logger.info("✓ Messaging service shutdown complete")
    except Exception as e:
        logger.error(f"Messaging service shutdown error: {e}")
    
    await close_db()
    await auth_client.close()
    logger.info("Database connections and auth client closed")


def create_application() -> FastAPI:
    application = FastAPI(
        title=f"{settings.project_name} (Framework Edition)",
        description=f"{settings.description} - Enhanced with Business Object Framework",
        version=f"{settings.version}-framework",
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routers
    from app.routers import companies, currencies, extensions
    
    # Original routers (non-Partner services)
    application.include_router(companies.router, prefix="/api/v1")
    application.include_router(currencies.router)
    application.include_router(extensions.router, prefix="/api/v1")
    
    # Framework-based Partner routers
    from app.framework_migration.partner_router import router as framework_partner_router
    from app.framework_migration.partner_router import framework_partner_router as generated_partner_router
    
    # Include both framework router options
    application.include_router(framework_partner_router, prefix="/api/v1")
    application.include_router(generated_partner_router.router, prefix="/api/v1")
    
    # Original Partner router for compatibility (at different path)
    try:
        from app.routers.partners import router as original_partner_router
        application.include_router(original_partner_router, prefix="/api/v1/partners-original", tags=["partners-original"])
        logger.info("✓ Original partner router included at /api/v1/partners-original/")
    except Exception as e:
        logger.warning(f"Could not include original partner router: {e}")
    
    logger.info("✓ Framework-based Partner routers included")
    logger.info("📋 Available Partner endpoints:")
    logger.info("  • /api/v1/partners-framework/ - Custom framework router")
    logger.info("  • /api/v1/partners/ - Auto-generated framework router")
    logger.info("  • /api/v1/partners-original/ - Original router (compatibility)")
    
    return application


app = create_application()


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Company & Partner Management Service",
        "version": f"{settings.version}-framework",
        "description": f"{settings.description} - Enhanced with Business Object Framework",
        "status": "running",
        "mode": "framework",
        "features": [
            "Custom fields support",
            "Audit logging", 
            "Event publishing",
            "Bulk operations",
            "Enhanced validation",
            "Auto-generated documentation"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with dependency status."""
    from app.core.database import get_db
    
    # Basic health response
    health_data = {
        "status": "healthy",
        "service": "company-partner-service",
        "version": f"{settings.version}-framework",
        "mode": "framework",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {
            "database": "unknown",
            "auth_service": "unknown",
            "framework": "unknown"
        }
    }
    
    # Check database connectivity
    try:
        from sqlalchemy import text
        async for db in get_db():
            await db.execute(text("SELECT 1"))
            health_data["dependencies"]["database"] = "healthy"
            break
    except Exception as e:
        health_data["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_data["status"] = "degraded"
    
    # Check auth service connectivity
    try:
        token = await auth_client.get_service_token()
        if token:
            health_data["dependencies"]["auth_service"] = "healthy"
        else:
            health_data["dependencies"]["auth_service"] = "unhealthy: failed to get token"
            health_data["status"] = "degraded"
    except Exception as e:
        health_data["dependencies"]["auth_service"] = f"unhealthy: {str(e)}"
        health_data["status"] = "degraded"
    
    # Check framework components
    try:
        from app.framework_migration.partner_service import PartnerFrameworkService
        from app.framework.services import CompanyBusinessObjectService
        health_data["dependencies"]["framework"] = "healthy"
    except Exception as e:
        health_data["dependencies"]["framework"] = f"unhealthy: {str(e)}"
        health_data["status"] = "degraded"
    
    return health_data


@app.get("/migration/status")
async def migration_status():
    """Get migration status information."""
    try:
        import json
        from pathlib import Path
        
        config_file = Path("app/migration_status.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                status = json.load(f)
        else:
            status = {"framework_enabled": True, "implementation": "framework"}
        
        return {
            "migration_status": status,
            "available_endpoints": {
                "framework_partners": "/api/v1/partners-framework/",
                "generated_partners": "/api/v1/partners/",
                "original_partners": "/api/v1/partners-original/",
                "extensions": "/api/v1/partners/{id}/extensions",
                "audit": "/api/v1/partners/{id}/audit"
            },
            "framework_features": [
                "Custom field support",
                "Automatic audit logging",
                "Event publishing to Redis",
                "Bulk operations",
                "Enhanced validation",
                "Multi-company isolation"
            ]
        }
    except Exception as e:
        return {"error": f"Failed to get migration status: {e}"}
'''
            
            # Write framework main.py
            framework_main.write_text(framework_main_content)
            
            # Replace current main.py with framework version
            import shutil
            shutil.copy2(framework_main, original_main)
            
            print("✅ Created framework-enabled main.py")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create framework main.py: {e}")
            return False
    
    def show_status(self):
        """Show current migration status."""
        status = self.get_migration_status()
        
        print("📊 Migration Status Report")
        print("=" * 50)
        print(f"Framework Enabled: {'✅ Yes' if status['framework_enabled'] else '❌ No'}")
        print(f"Current Implementation: {status['implementation']}")
        print(f"Migration Date: {status.get('migration_date', 'N/A')}")
        print(f"Rollback Available: {'✅ Yes' if status.get('rollback_available', False) else '❌ No'}")
        print(f"Last Updated: {status.get('last_updated', 'N/A')}")
        
        # Validate implementations
        print("\n🔍 Implementation Validation:")
        original_valid, framework_valid = self.validate_implementations()
        
        print(f"\n📋 Available Actions:")
        if not status['framework_enabled'] and framework_valid:
            print("  • Use --enable-framework to switch to framework implementation")
        if status['framework_enabled'] and original_valid:
            print("  • Use --disable-framework to switch back to original implementation")
        print("  • Use --validate to check implementation health")
        
        return status


def main():
    """Main migration control script entry point."""
    parser = argparse.ArgumentParser(description="Control Partner service migration")
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument("--enable-framework", action="store_true", 
                      help="Enable Business Object Framework implementation")
    group.add_argument("--disable-framework", action="store_true",
                      help="Disable framework and return to original implementation")
    group.add_argument("--status", action="store_true",
                      help="Show current migration status")
    group.add_argument("--validate", action="store_true",
                      help="Validate both implementations")
    
    parser.add_argument("--service-root", default=".", 
                       help="Root directory of the service")
    
    args = parser.parse_args()
    
    try:
        controller = MigrationController(args.service_root)
        
        if args.enable_framework:
            success = controller.enable_framework()
            return 0 if success else 1
            
        elif args.disable_framework:
            success = controller.disable_framework()
            return 0 if success else 1
            
        elif args.status:
            controller.show_status()
            return 0
            
        elif args.validate:
            original_valid, framework_valid = controller.validate_implementations()
            if original_valid and framework_valid:
                print("✅ Both implementations are valid")
                return 0
            else:
                print("❌ One or more implementations have issues")
                return 1
                
    except Exception as e:
        print(f"❌ Migration control failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())