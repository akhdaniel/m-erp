"""
UI Registration Client for XERPIUM Services.

This client library allows services to register their UI components
with the UI Registry Service.
"""

import os
import requests
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

# Get UI Registry Service URL from environment or use default
UI_REGISTRY_URL = os.getenv("UI_REGISTRY_URL", "http://ui-registry-service:8010")


@dataclass
class UIComponent:
    """UI Component definition"""
    id: str
    type: str  # dashboard, list, form, chart, widget, etc.
    title: str
    description: Optional[str] = None
    path: Optional[str] = None
    config: Dict[str, Any] = None
    permissions: List[str] = None
    order: int = 0
    icon: Optional[str] = None
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.permissions is None:
            self.permissions = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DashboardWidget:
    """Dashboard widget definition"""
    id: str
    title: str
    type: str  # metric, chart, list, table, etc.
    data_endpoint: str
    size: str = "medium"  # small, medium, large, full
    position: Optional[Dict[str, int]] = None
    refresh_interval: int = 60
    config: Dict[str, Any] = None
    permissions: List[str] = None

    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.permissions is None:
            self.permissions = []


@dataclass
class ListView:
    """List view definition"""
    id: str
    title: str
    entity: str
    columns: List[Dict[str, Any]]
    data_endpoint: str
    actions: List[Dict[str, Any]] = None
    filters: List[Dict[str, Any]] = None
    sorting: Dict[str, Any] = None
    pagination: bool = True
    permissions: List[str] = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.filters is None:
            self.filters = []
        if self.sorting is None:
            self.sorting = {}
        if self.permissions is None:
            self.permissions = []


@dataclass
class FormView:
    """Form view definition"""
    id: str
    title: str
    entity: str
    fields: List[Dict[str, Any]]
    submit_endpoint: str
    mode: str = "create"
    data_endpoint: Optional[str] = None
    validation_rules: Dict[str, Any] = None
    layout: str = "single"
    permissions: List[str] = None

    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = {}
        if self.permissions is None:
            self.permissions = []


class UIRegistrationClient:
    """Client for registering UI components with the UI Registry Service"""

    def __init__(self, service_name: str, registry_url: Optional[str] = None):
        self.service_name = service_name
        self.registry_url = registry_url or UI_REGISTRY_URL
        self.session = requests.Session()

    def register_component(self, component: UIComponent) -> bool:
        """Register a UI component"""
        try:
            data = asdict(component)
            data["service"] = self.service_name
            
            response = self.session.post(
                f"{self.registry_url}/api/v1/components",
                json=data
            )
            response.raise_for_status()
            logger.info(f"Registered UI component: {component.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register UI component {component.id}: {e}")
            return False

    def register_dashboard_widget(self, widget: DashboardWidget) -> bool:
        """Register a dashboard widget"""
        try:
            data = asdict(widget)
            data["service"] = self.service_name
            
            response = self.session.post(
                f"{self.registry_url}/api/v1/dashboard/widgets",
                json=data
            )
            response.raise_for_status()
            logger.info(f"Registered dashboard widget: {widget.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register dashboard widget {widget.id}: {e}")
            return False

    def register_list_view(self, list_view: ListView) -> bool:
        """Register a list view configuration"""
        try:
            data = asdict(list_view)
            data["service"] = self.service_name
            
            response = self.session.post(
                f"{self.registry_url}/api/v1/lists",
                json=data
            )
            response.raise_for_status()
            logger.info(f"Registered list view: {list_view.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register list view {list_view.id}: {e}")
            return False

    def register_form_view(self, form_view: FormView) -> bool:
        """Register a form view configuration"""
        try:
            data = asdict(form_view)
            data["service"] = self.service_name
            
            response = self.session.post(
                f"{self.registry_url}/api/v1/forms",
                json=data
            )
            response.raise_for_status()
            logger.info(f"Registered form view: {form_view.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register form view {form_view.id}: {e}")
            return False

    def register_ui_package(self, package: Dict[str, Any]) -> bool:
        """Register a complete UI package for the service"""
        try:
            response = self.session.post(
                f"{self.registry_url}/api/v1/services/{self.service_name}/ui-package",
                json=package
            )
            response.raise_for_status()
            logger.info(f"Registered UI package for service: {self.service_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register UI package: {e}")
            return False


# Helper function for services to register their UI on startup
def register_service_ui(service_name: str, ui_definitions: Dict[str, Any]):
    """
    Register all UI components for a service.
    
    Args:
        service_name: Name of the service
        ui_definitions: Dictionary containing UI definitions
            {
                "components": [...],
                "widgets": [...],
                "lists": [...],
                "forms": [...]
            }
    """
    client = UIRegistrationClient(service_name)
    
    # Register components
    if "components" in ui_definitions:
        for comp_def in ui_definitions["components"]:
            component = UIComponent(**comp_def)
            client.register_component(component)
    
    # Register dashboard widgets
    if "widgets" in ui_definitions:
        for widget_def in ui_definitions["widgets"]:
            widget = DashboardWidget(**widget_def)
            client.register_dashboard_widget(widget)
    
    # Register list views
    if "lists" in ui_definitions:
        for list_def in ui_definitions["lists"]:
            list_view = ListView(**list_def)
            client.register_list_view(list_view)
    
    # Register form views
    if "forms" in ui_definitions:
        for form_def in ui_definitions["forms"]:
            form_view = FormView(**form_def)
            client.register_form_view(form_view)
    
    logger.info(f"UI registration completed for service: {service_name}")