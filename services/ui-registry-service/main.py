"""
UI Registry Service for M-ERP.

This service manages UI component registrations from other microservices,
allowing them to register their dashboards, forms, lists, and other UI components.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import redis
import json
import os

app = FastAPI(
    title="UI Registry Service",
    description="Service for managing UI component registrations from microservices",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Pydantic models
class UIComponent(BaseModel):
    """Base UI component registration"""
    id: str
    service: str
    type: str  # dashboard, list, form, chart, widget, etc.
    title: str
    description: Optional[str] = None
    path: Optional[str] = None  # URL path for routing
    config: Dict[str, Any] = {}  # Component-specific configuration
    permissions: List[str] = []  # Required permissions
    order: int = 0
    icon: Optional[str] = None
    parent_id: Optional[str] = None  # For hierarchical components
    metadata: Dict[str, Any] = {}

class DashboardWidget(BaseModel):
    """Dashboard widget registration"""
    id: str
    service: str
    title: str
    type: str  # metric, chart, list, table, etc.
    size: str = "medium"  # small, medium, large, full
    position: Optional[Dict[str, int]] = None  # {row: 0, col: 0}
    data_endpoint: str  # API endpoint for data
    refresh_interval: int = 60  # seconds
    config: Dict[str, Any] = {}
    permissions: List[str] = []

class ListView(BaseModel):
    """List view configuration"""
    id: str
    service: str
    title: str
    entity: str  # Entity type (products, orders, etc.)
    columns: List[Dict[str, Any]]  # Column definitions
    data_endpoint: str  # API endpoint for data
    actions: List[Dict[str, Any]] = []  # Available actions
    filters: List[Dict[str, Any]] = []  # Filter definitions
    sorting: Dict[str, Any] = {}
    pagination: bool = True
    permissions: List[str] = []

class FormView(BaseModel):
    """Form view configuration"""
    id: str
    service: str
    title: str
    entity: str
    mode: str = "create"  # create, edit, view
    fields: List[Dict[str, Any]]  # Field definitions
    submit_endpoint: str  # API endpoint for form submission
    data_endpoint: Optional[str] = None  # For edit mode
    validation_rules: Dict[str, Any] = {}
    layout: str = "single"  # single, multi-column, wizard
    permissions: List[str] = []

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "UI Registry Service",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

# Component Registration

@app.post("/api/v1/components")
async def register_component(component: UIComponent):
    """Register a UI component"""
    key = f"ui:component:{component.service}:{component.id}"
    redis_client.setex(
        key,
        86400,  # 24 hour TTL
        json.dumps(component.dict())
    )
    # Also add to service index
    redis_client.sadd(f"ui:service:{component.service}:components", component.id)
    return {"status": "registered", "component_id": component.id}

@app.get("/api/v1/components")
async def list_components(
    service: Optional[str] = None,
    type: Optional[str] = None
):
    """List all registered UI components"""
    pattern = "ui:component:*"
    if service:
        pattern = f"ui:component:{service}:*"
    
    keys = redis_client.keys(pattern)
    components = []
    
    for key in keys:
        data = redis_client.get(key)
        if data:
            component = json.loads(data)
            if not type or component.get("type") == type:
                components.append(component)
    
    return components

@app.get("/api/v1/components/{service}/{component_id}")
async def get_component(service: str, component_id: str):
    """Get a specific component"""
    key = f"ui:component:{service}:{component_id}"
    data = redis_client.get(key)
    
    if not data:
        raise HTTPException(status_code=404, detail="Component not found")
    
    return json.loads(data)

@app.delete("/api/v1/components/{service}/{component_id}")
async def unregister_component(service: str, component_id: str):
    """Unregister a UI component"""
    key = f"ui:component:{service}:{component_id}"
    redis_client.delete(key)
    redis_client.srem(f"ui:service:{service}:components", component_id)
    return {"status": "unregistered"}

# Dashboard Widget Registration

@app.post("/api/v1/dashboard/widgets")
async def register_dashboard_widget(widget: DashboardWidget):
    """Register a dashboard widget"""
    key = f"ui:dashboard:widget:{widget.service}:{widget.id}"
    redis_client.setex(
        key,
        86400,
        json.dumps(widget.dict())
    )
    redis_client.sadd(f"ui:dashboard:widgets", f"{widget.service}:{widget.id}")
    return {"status": "registered", "widget_id": widget.id}

@app.get("/api/v1/dashboard/widgets")
async def list_dashboard_widgets():
    """List all dashboard widgets"""
    widget_keys = redis_client.smembers("ui:dashboard:widgets")
    widgets = []
    
    for widget_key in widget_keys:
        service, widget_id = widget_key.split(":", 1)
        key = f"ui:dashboard:widget:{service}:{widget_id}"
        data = redis_client.get(key)
        if data:
            widgets.append(json.loads(data))
    
    return widgets

# List View Registration

@app.post("/api/v1/lists")
async def register_list_view(list_view: ListView):
    """Register a list view configuration"""
    key = f"ui:list:{list_view.service}:{list_view.id}"
    redis_client.setex(
        key,
        86400,
        json.dumps(list_view.dict())
    )
    redis_client.sadd(f"ui:lists", f"{list_view.service}:{list_view.id}")
    return {"status": "registered", "list_id": list_view.id}

@app.get("/api/v1/lists")
async def list_list_views():
    """List all list view configurations"""
    list_keys = redis_client.smembers("ui:lists")
    lists = []
    
    for list_key in list_keys:
        service, list_id = list_key.split(":", 1)
        key = f"ui:list:{service}:{list_id}"
        data = redis_client.get(key)
        if data:
            lists.append(json.loads(data))
    
    return lists

# Form View Registration

@app.post("/api/v1/forms")
async def register_form_view(form_view: FormView):
    """Register a form view configuration"""
    key = f"ui:form:{form_view.service}:{form_view.id}"
    redis_client.setex(
        key,
        86400,
        json.dumps(form_view.dict())
    )
    redis_client.sadd(f"ui:forms", f"{form_view.service}:{form_view.id}")
    return {"status": "registered", "form_id": form_view.id}

@app.get("/api/v1/forms")
async def list_form_views():
    """List all form view configurations"""
    form_keys = redis_client.smembers("ui:forms")
    forms = []
    
    for form_key in form_keys:
        service, form_id = form_key.split(":", 1)
        key = f"ui:form:{service}:{form_id}"
        data = redis_client.get(key)
        if data:
            forms.append(json.loads(data))
    
    return forms

# Service UI Package Registration

@app.post("/api/v1/services/{service}/ui-package")
async def register_service_ui_package(service: str, package: Dict[str, Any]):
    """
    Register a complete UI package for a service.
    Package includes dashboards, lists, forms, and other components.
    """
    # Store the entire package
    key = f"ui:package:{service}"
    redis_client.setex(
        key,
        86400,
        json.dumps(package)
    )
    
    # Process individual components
    if "components" in package:
        for component in package["components"]:
            component["service"] = service
            await register_component(UIComponent(**component))
    
    if "widgets" in package:
        for widget in package["widgets"]:
            widget["service"] = service
            await register_dashboard_widget(DashboardWidget(**widget))
    
    if "lists" in package:
        for list_view in package["lists"]:
            list_view["service"] = service
            await register_list_view(ListView(**list_view))
    
    if "forms" in package:
        for form_view in package["forms"]:
            form_view["service"] = service
            await register_form_view(FormView(**form_view))
    
    return {"status": "package registered", "service": service}

@app.get("/api/v1/services/{service}/ui-package")
async def get_service_ui_package(service: str):
    """Get the complete UI package for a service"""
    key = f"ui:package:{service}"
    data = redis_client.get(key)
    
    if not data:
        # Build package from individual components
        package = {
            "service": service,
            "components": [],
            "widgets": [],
            "lists": [],
            "forms": []
        }
        
        # Get components
        component_keys = redis_client.keys(f"ui:component:{service}:*")
        for key in component_keys:
            data = redis_client.get(key)
            if data:
                package["components"].append(json.loads(data))
        
        # Get widgets
        widget_keys = redis_client.keys(f"ui:dashboard:widget:{service}:*")
        for key in widget_keys:
            data = redis_client.get(key)
            if data:
                package["widgets"].append(json.loads(data))
        
        # Get lists
        list_keys = redis_client.keys(f"ui:list:{service}:*")
        for key in list_keys:
            data = redis_client.get(key)
            if data:
                package["lists"].append(json.loads(data))
        
        # Get forms
        form_keys = redis_client.keys(f"ui:form:{service}:*")
        for key in form_keys:
            data = redis_client.get(key)
            if data:
                package["forms"].append(json.loads(data))
        
        return package
    
    return json.loads(data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)