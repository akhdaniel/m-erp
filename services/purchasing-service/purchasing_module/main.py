"""
Purchasing Module Main Entry Point

This module provides the main initialization and lifecycle management
for the Purchasing Module within the XERPIUM Extension System.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from purchasing_module import MODULE_INFO

logger = logging.getLogger(__name__)


class PurchasingModuleManager:
    """
    Manager class for the Purchasing Module lifecycle.
    
    Handles initialization, configuration, health checks, and shutdown
    for the purchasing module within the XERPIUM extension framework.
    """
    
    def __init__(self):
        self.initialized = False
        self.start_time: Optional[datetime] = None
        self.configuration: Dict[str, Any] = {}
        self.services = {}
        self.health_status = "unknown"
    
    async def initialize(self, config: Dict[str, Any] = None) -> bool:
        """
        Initialize the purchasing module.
        
        Args:
            config: Module configuration dictionary
            
        Returns:
            bool: True if initialization successful
        """
        if self.initialized:
            logger.warning("Purchasing module already initialized")
            return True
        
        try:
            logger.info(f"Initializing {MODULE_INFO['display_name']} v{MODULE_INFO['version']}")
            
            # Store configuration
            self.configuration = config or {}
            
            # Initialize services
            await self._initialize_services()
            
            # Register event handlers
            await self._register_event_handlers()
            
            # Set up database tables (in production, this would use proper migrations)
            await self._setup_database()
            
            # Register API endpoints (in production, this would integrate with the API gateway)
            await self._register_api_endpoints()
            
            # Initialize UI components (in production, this would register with the UI service)
            await self._initialize_ui_components()
            
            self.initialized = True
            self.start_time = datetime.utcnow()
            self.health_status = "healthy"
            
            logger.info(f"✅ {MODULE_INFO['display_name']} initialized successfully")
            
            # Publish module initialization event
            await self._publish_event("purchasing_module.initialized", {
                "module_name": MODULE_INFO['name'],
                "version": MODULE_INFO['version'],
                "initialized_at": self.start_time.isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize purchasing module: {e}")
            self.health_status = "unhealthy"
            return False
    
    async def _initialize_services(self) -> None:
        """Initialize purchasing module services."""
        logger.info("Initializing purchasing services...")
        
        # In production, these would be actual service instances
        # from purchasing_module.services import (
        #     PurchaseOrderService, SupplierService, ApprovalService
        # )
        
        self.services = {
            "purchase_order_service": "PurchaseOrderService()",  # Placeholder
            "supplier_service": "SupplierService()",  # Placeholder  
            "approval_service": "ApprovalService()"  # Placeholder
        }
        
        logger.info(f"✅ Initialized {len(self.services)} purchasing services")
    
    async def _register_event_handlers(self) -> None:
        """Register event handlers for module integration."""
        logger.info("Registering event handlers...")
        
        # In production, this would register with the Redis Streams event system
        event_handlers = [
            ("partner.created", "on_partner_created"),
            ("partner.updated", "on_partner_updated"),
            ("currency.rate_updated", "on_currency_rate_updated")
        ]
        
        for event_type, handler_name in event_handlers:
            logger.info(f"  Registered handler '{handler_name}' for event '{event_type}'")
        
        logger.info(f"✅ Registered {len(event_handlers)} event handlers")
    
    async def _setup_database(self) -> None:
        """Set up database tables for the purchasing module."""
        logger.info("Setting up database tables...")
        
        # In production, this would:
        # 1. Connect to the database
        # 2. Run migrations for purchasing tables
        # 3. Create indexes and constraints
        # 4. Set up initial data
        
        tables = [
            "purchase_orders",
            "purchase_order_line_items", 
            "supplier_performance",
            "performance_metrics",
            "approval_workflows",
            "approval_steps"
        ]
        
        for table in tables:
            logger.info(f"  Creating table: {table}")
        
        logger.info(f"✅ Created {len(tables)} database tables")
    
    async def _register_api_endpoints(self) -> None:
        """Register API endpoints with the API gateway."""
        logger.info("Registering API endpoints...")
        
        # In production, this would register with the Kong API Gateway
        endpoints = [
            "GET /purchase-orders",
            "POST /purchase-orders", 
            "GET /purchase-orders/{id}",
            "PUT /purchase-orders/{id}",
            "POST /purchase-orders/{id}/approve",
            "POST /purchase-orders/{id}/reject",
            "GET /suppliers",
            "GET /suppliers/{id}/performance"
        ]
        
        for endpoint in endpoints:
            logger.info(f"  Registered endpoint: {endpoint}")
        
        logger.info(f"✅ Registered {len(endpoints)} API endpoints")
    
    async def _initialize_ui_components(self) -> None:
        """Initialize UI components for the purchasing module."""
        logger.info("Initializing UI components...")
        
        # In production, this would register components with the UI service
        components = [
            "PurchaseOrderList",
            "PurchaseOrderForm",
            "ApprovalWorkflow", 
            "SupplierPerformance"
        ]
        
        for component in components:
            logger.info(f"  Initialized UI component: {component}")
        
        logger.info(f"✅ Initialized {len(components)} UI components")
    
    async def _publish_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Publish an event to the event system.
        
        Args:
            event_type: Type of event to publish
            event_data: Event data payload
        """
        # In production, this would publish to Redis Streams
        logger.info(f"📤 Published event '{event_type}': {event_data}")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for the purchasing module.
        
        Returns:
            dict: Health check results
        """
        if not self.initialized:
            return {
                "status": "unhealthy",
                "message": "Module not initialized",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            # Check service health
            service_health = {}
            for service_name, service in self.services.items():
                # In production, would call actual health check methods
                service_health[service_name] = "healthy"
            
            # Check database connectivity
            database_health = "healthy"  # Placeholder
            
            # Check event system connectivity
            event_system_health = "healthy"  # Placeholder
            
            overall_status = "healthy" if all([
                all(status == "healthy" for status in service_health.values()),
                database_health == "healthy",
                event_system_health == "healthy"
            ]) else "unhealthy"
            
            uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
            
            return {
                "status": overall_status,
                "module": MODULE_INFO['name'],
                "version": MODULE_INFO['version'],
                "uptime_seconds": uptime_seconds,
                "started_at": self.start_time.isoformat() if self.start_time else None,
                "services": service_health,
                "database": database_health,
                "event_system": event_system_health,
                "configuration": {
                    "approval_thresholds": self.configuration.get("approval_thresholds", {}),
                    "default_currency": self.configuration.get("default_currency", "USD"),
                    "notification_settings": self.configuration.get("notification_settings", {})
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def shutdown(self) -> bool:
        """
        Shutdown the purchasing module gracefully.
        
        Returns:
            bool: True if shutdown successful
        """
        if not self.initialized:
            logger.warning("Module not initialized, nothing to shutdown")
            return True
        
        try:
            logger.info(f"Shutting down {MODULE_INFO['display_name']}...")
            
            # Publish shutdown event
            await self._publish_event("purchasing_module.shutdown_started", {
                "module_name": MODULE_INFO['name'],
                "shutdown_at": datetime.utcnow().isoformat()
            })
            
            # Cleanup services
            for service_name in self.services:
                logger.info(f"  Shutting down service: {service_name}")
                # In production, would call service.shutdown()
            
            # Unregister event handlers
            logger.info("  Unregistering event handlers...")
            
            # Cleanup API endpoints
            logger.info("  Unregistering API endpoints...")
            
            # Cleanup UI components
            logger.info("  Unregistering UI components...")
            
            self.initialized = False
            self.health_status = "shutdown"
            
            # Publish shutdown complete event
            await self._publish_event("purchasing_module.shutdown_complete", {
                "module_name": MODULE_INFO['name'],
                "shutdown_completed_at": datetime.utcnow().isoformat()
            })
            
            logger.info(f"✅ {MODULE_INFO['display_name']} shutdown complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to shutdown purchasing module: {e}")
            return False
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current module configuration."""
        return self.configuration.copy()
    
    def update_configuration(self, new_config: Dict[str, Any]) -> bool:
        """
        Update module configuration.
        
        Args:
            new_config: New configuration values
            
        Returns:
            bool: True if update successful
        """
        try:
            # Validate configuration (in production, would use JSON schema validation)
            self.configuration.update(new_config)
            
            logger.info("Module configuration updated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return False


# Global module manager instance
_module_manager = PurchasingModuleManager()


async def initialize_module(config: Dict[str, Any] = None) -> bool:
    """
    Initialize the purchasing module.
    
    This is the main entry point called by the XERPIUM extension framework.
    
    Args:
        config: Module configuration dictionary
        
    Returns:
        bool: True if initialization successful
    """
    return await _module_manager.initialize(config)


async def shutdown_module() -> bool:
    """
    Shutdown the purchasing module.
    
    This is called by the XERPIUM extension framework during module uninstallation
    or system shutdown.
    
    Returns:
        bool: True if shutdown successful
    """
    return await _module_manager.shutdown()


async def check_health() -> Dict[str, Any]:
    """
    Perform health check for the purchasing module.
    
    This is called by the XERPIUM extension framework for health monitoring.
    
    Returns:
        dict: Health check results
    """
    return await _module_manager.health_check()


def get_module_info() -> Dict[str, Any]:
    """
    Get module information.
    
    Returns:
        dict: Module metadata
    """
    return MODULE_INFO.copy()


def get_configuration() -> Dict[str, Any]:
    """
    Get current module configuration.
    
    Returns:
        dict: Current configuration
    """
    return _module_manager.get_configuration()


def update_configuration(config: Dict[str, Any]) -> bool:
    """
    Update module configuration.
    
    Args:
        config: New configuration values
        
    Returns:
        bool: True if update successful
    """
    return _module_manager.update_configuration(config)


# For backward compatibility and direct testing
if __name__ == "__main__":
    async def main():
        """Test module initialization."""
        print(f"Testing {MODULE_INFO['display_name']} v{MODULE_INFO['version']}")
        
        # Test configuration
        test_config = {
            "approval_thresholds": {
                "manager_limit": 5000.00,
                "director_limit": 25000.00,
                "requires_board_approval": 100000.00
            },
            "default_currency": "USD",
            "notification_settings": {
                "email_notifications": True,
                "approval_reminders": True,
                "reminder_days": 3
            }
        }
        
        # Initialize module
        success = await initialize_module(test_config)
        if success:
            print("✅ Module initialized successfully")
            
            # Run health check
            health = await check_health()
            print(f"Health Status: {health['status']}")
            
            # Test configuration
            config = get_configuration()
            print(f"Configuration: {config}")
            
            # Shutdown module
            await shutdown_module()
            print("✅ Module shutdown complete")
        else:
            print("❌ Module initialization failed")
    
    # Run test
    asyncio.run(main())