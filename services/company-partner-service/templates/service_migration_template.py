#!/usr/bin/env python3
"""
Business Object Framework Service Migration Template

This template provides a complete example for migrating any service to use the
Business Object Framework. Replace {SERVICE}, {Model}, and {model} placeholders
with your actual service, model, and instance names.

Usage:
1. Copy this template to your service directory
2. Replace all placeholders with your service-specific values
3. Run the migration script to generate framework files
4. Test and validate the migration
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


class {Service}FrameworkMigration:
    """Migration script for {Service} service to Business Object Framework."""
    
    def __init__(self, service_root: str = ".", dry_run: bool = False, backup: bool = False):
        self.service_root = Path(service_root)
        self.dry_run = dry_run
        self.backup = backup
        self.backup_dir = self.service_root / "migrations" / "backups" / f"{model}_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Service-specific configuration
        self.service_name = "{service}"
        self.model_name = "{Model}"
        self.model_plural = "{models}"
        self.service_class = "{Service}Service"
        self.framework_service_class = "{Model}FrameworkService"
        
    def run_migration(self):
        """Execute the complete migration process."""
        print(f"🚀 Starting {self.service_name.title()} Service Migration to Business Object Framework")
        print("=" * 80)
        
        try:
            # Step 1: Backup existing files
            if self.backup:
                self._create_backups()
            
            # Step 2: Create framework-based schemas
            self._create_framework_schemas()
            
            # Step 3: Create framework-based service
            self._create_framework_service()
            
            # Step 4: Create framework-based router
            self._create_framework_router()
            
            # Step 5: Create migration tests
            self._create_migration_tests()
            
            # Step 6: Update main application
            self._update_main_app()
            
            # Step 7: Create migration documentation
            self._create_migration_docs()
            
            print("\n✅ Migration completed successfully!")
            print("\n📋 Next steps:")
            print(f"  1. Review generated files in app/framework_migration/")
            print(f"  2. Run tests: pytest tests/test_{model}_migration_integration.py")
            print(f"  3. Start server and test API endpoints")
            print(f"  4. Replace existing files when ready")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            raise
    
    def _create_backups(self):
        """Create backups of existing files."""
        print("📦 Creating backups...")
        
        files_to_backup = [
            f"app/schemas/{model}.py",
            f"app/services/{model}_service.py",
            f"app/routers/{self.model_plural}.py"
        ]
        
        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in files_to_backup:
                source = self.service_root / file_path
                if source.exists():
                    dest = self.backup_dir / file_path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    import shutil
                    shutil.copy2(source, dest)
                    print(f"  ✓ Backed up {file_path}")
        else:
            print("  [DRY RUN] Would backup:", files_to_backup)
    
    def _create_framework_schemas(self):
        """Create framework-based schemas."""
        print("\n📄 Creating framework-based schemas...")
        
        schema_content = f'''"""
Framework-based {self.model_name} schemas using Business Object Framework.

This file demonstrates how to migrate existing {self.model_name} schemas to use the
Business Object Framework base classes while maintaining compatibility.
"""

from typing import Optional
from datetime import datetime
from pydantic import Field, validator

from app.framework.schemas import (
    CompanyBusinessObjectSchema,
    CreateSchemaBase,
    UpdateSchemaBase
)


class {self.model_name}FrameworkBase(CompanyBusinessObjectSchema):
    """Framework-based base schema for {model} data."""
    
    # TODO: Add your model fields here
    # Example fields (replace with your actual fields):
    name: str = Field(..., min_length=1, max_length=255, description="{Model} name")
    code: Optional[str] = Field(None, max_length=50, description="{Model} code")
    description: Optional[str] = Field(None, max_length=500, description="{Model} description")
    is_active: bool = Field(True, description="Is active")
    
    # TODO: Add field validators
    @validator('name')
    def validate_name(cls, v):
        """Validate {model} name."""
        if not v or len(v.strip()) < 1:
            raise ValueError('{Model} name cannot be empty')
        return v.strip()
    
    @validator('code')
    def validate_code(cls, v):
        """Validate and normalize {model} code."""
        if v and len(v.strip()) < 1:
            raise ValueError('{Model} code cannot be empty')
        return v.strip().upper() if v else v


class {self.model_name}FrameworkCreate(CreateSchemaBase, {self.model_name}FrameworkBase):
    """Framework-based schema for creating a new {model}."""
    
    # Override company_id to make it required for creation
    company_id: int = Field(..., gt=0, description="Company ID")
    
    class Config:
        schema_extra = {{
            "example": {{
                "name": "Example {self.model_name}",
                "code": "EX001",
                "description": "Example {model} description",
                "company_id": 1,
                "is_active": True
            }}
        }}


class {self.model_name}FrameworkUpdate(UpdateSchemaBase):
    """Framework-based schema for updating a {model}."""
    
    # All fields optional for updates
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    
    # TODO: Add validators for update fields
    @validator('name')
    def validate_name(cls, v):
        """Validate {model} name if provided."""
        if v and len(v.strip()) < 1:
            raise ValueError('{Model} name cannot be empty')
        return v.strip() if v else v
    
    @validator('code')
    def validate_code(cls, v):
        """Validate and normalize {model} code if provided."""
        if v and len(v.strip()) < 1:
            raise ValueError('{Model} code cannot be empty')
        return v.strip().upper() if v else v

    class Config:
        schema_extra = {{
            "example": {{
                "name": "Updated {self.model_name}",
                "description": "Updated description",
                "is_active": True
            }}
        }}


class {self.model_name}FrameworkResponse({self.model_name}FrameworkBase):
    """Framework-based schema for {model} response."""
    
    # Add ID field from framework
    id: int = Field(..., description="{Model} ID")
    
    class Config:
        from_attributes = True
        schema_extra = {{
            "example": {{
                "id": 1,
                "company_id": 1,
                "name": "Example {self.model_name}",
                "code": "EX001",
                "description": "Example {model} description",
                "is_active": True,
                "created_at": "2025-08-01T10:00:00Z",
                "updated_at": "2025-08-01T10:00:00Z"
            }}
        }}


class {self.model_name}FrameworkListResponse(CompanyBusinessObjectSchema):
    """Framework-based schema for {model} list response."""
    
    {self.model_plural}: list[{self.model_name}FrameworkResponse] = Field(..., description="List of {self.model_plural}")
    total: int = Field(..., description="Total number of {self.model_plural}")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Number of {self.model_plural} per page")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        schema_extra = {{
            "example": {{
                "{self.model_plural}": [
                    {{
                        "id": 1,
                        "company_id": 1,
                        "name": "Example {self.model_name}",
                        "code": "EX001",
                        "is_active": True,
                        "created_at": "2025-08-01T10:00:00Z",
                        "updated_at": "2025-08-01T10:00:00Z"
                    }}
                ],
                "total": 1,
                "page": 1,
                "per_page": 50,
                "pages": 1
            }}
        }}
'''
        
        self._write_migration_file(f"app/framework_migration/{model}_schemas.py", schema_content)
    
    def _create_framework_service(self):
        """Create framework-based service."""
        print("\n🔧 Creating framework-based service...")
        
        service_content = f'''"""
Framework-based {self.model_name} service using Business Object Framework.

This service demonstrates how to migrate existing {self.model_name} service logic to use
the Business Object Framework while maintaining all existing functionality.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_

from app.models.{model} import {self.model_name}
from app.framework.services import CompanyBusinessObjectService
from app.framework_migration.{model}_schemas import {self.model_name}FrameworkCreate, {self.model_name}FrameworkUpdate


class {self.framework_service_class}(CompanyBusinessObjectService[{self.model_name}]):
    """Framework-based {self.model_name} service with enhanced capabilities."""
    
    def __init__(self, db: AsyncSession):
        """Initialize {self.model_name} service with framework support."""
        super().__init__(db, {self.model_name})
    
    # === Enhanced Framework Operations ===
    
    async def create_{model}(self, {model}_data: {self.model_name}FrameworkCreate) -> {self.model_name}:
        """Create a new {model} using framework create method."""
        return await self.create({model}_data.dict())
    
    async def get_{model}(self, {model}_id: int, company_id: Optional[int] = None) -> Optional[{self.model_name}]:
        """Get {model} by ID with optional company validation."""
        if company_id:
            return await self.get_by_id({model}_id, {{"company_id": company_id}})
        return await self.get_by_id({model}_id)
    
    async def update_{model}(self, {model}_id: int, {model}_data: {self.model_name}FrameworkUpdate, company_id: Optional[int] = None) -> Optional[{self.model_name}]:
        """Update {model} using framework update method."""
        filters = {{"company_id": company_id}} if company_id else {{}}
        return await self.update({model}_id, {model}_data.dict(exclude_unset=True), filters)
    
    async def delete_{model}(self, {model}_id: int, company_id: Optional[int] = None) -> bool:
        """Soft delete {model} using framework delete method."""
        filters = {{"company_id": company_id}} if company_id else {{}}
        return await self.soft_delete({model}_id, filters)
    
    async def activate_{model}(self, {model}_id: int, company_id: Optional[int] = None) -> Optional[{self.model_name}]:
        """Activate {model} using framework update method."""
        filters = {{"company_id": company_id}} if company_id else {{}}
        return await self.update({model}_id, {{"is_active": True}}, filters)
    
    async def deactivate_{model}(self, {model}_id: int, company_id: Optional[int] = None) -> Optional[{self.model_name}]:
        """Deactivate {model} using framework update method."""
        filters = {{"company_id": company_id}} if company_id else {{}}
        return await self.update({model}_id, {{"is_active": False}}, filters)
    
    # === Business-Specific Methods ===
    
    async def get_{model}_by_code(self, company_id: int, code: str) -> Optional[{self.model_name}]:
        """Get {model} by code within a company."""
        return await self.get_by_filters({{"company_id": company_id, "code": code.upper()}})
    
    async def get_{self.model_plural}_by_company(
        self,
        company_id: int,
        active_only: bool = True
    ) -> List[{self.model_name}]:
        """Get all {self.model_plural} for a specific company with filtering."""
        filters = {{"company_id": company_id}}
        
        if active_only:
            filters["is_active"] = True
        
        return await self.get_list(filters=filters)
    
    async def get_{self.model_plural}(
        self,
        company_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> tuple[List[{self.model_name}], int]:
        """Get {self.model_plural} with pagination and search using framework methods."""
        
        # Build base filters
        filters = {{}}
        if company_id:
            filters["company_id"] = company_id
        if active_only:
            filters["is_active"] = True
        
        # Use framework list method with search
        {self.model_plural} = await self.get_list(
            filters=filters,
            search_fields=["name", "code", "description"] if search else None,
            search_term=search,
            skip=skip,
            limit=limit
        )
        
        # Get total count
        total = await self.count(filters)
        
        return {self.model_plural}, total
    
    async def bulk_create_{self.model_plural}(self, {self.model_plural}_data: List[{self.model_name}FrameworkCreate]) -> List[{self.model_name}]:
        """Bulk create {self.model_plural} using framework bulk operations."""
        return await self.bulk_create([p.dict() for p in {self.model_plural}_data])
    
    async def get_{model}_statistics(self, company_id: int) -> Dict[str, Any]:
        """Get {model} statistics for a company."""
        
        # Use framework count method for different statistics
        total_{self.model_plural} = await self.count({{"company_id": company_id}})
        active_{self.model_plural} = await self.count({{"company_id": company_id, "is_active": True}})
        
        # TODO: Add more business-specific statistics
        
        return {{
            "total_{self.model_plural}": total_{self.model_plural},
            "active_{self.model_plural}": active_{self.model_plural},
            "inactive_{self.model_plural}": total_{self.model_plural} - active_{self.model_plural}
        }}


# Factory function for creating {self.model_name} service instances
def create_{model}_service(db: AsyncSession) -> {self.framework_service_class}:
    """Factory function to create {self.model_name} service instance."""
    return {self.framework_service_class}(db)
'''
        
        self._write_migration_file(f"app/framework_migration/{model}_service.py", service_content)
    
    def _create_framework_router(self):
        """Create framework-based router."""
        print("\n🌐 Creating framework-based router...")
        
        router_content = f'''"""
Framework-based {self.model_name} router using Business Object Framework.

This router demonstrates how to migrate existing {self.model_name} API endpoints to use
the Business Object Framework while maintaining full API compatibility.
"""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.middleware.auth import get_current_active_user, verify_company_access
from app.models.{model} import {self.model_name}
from app.framework.controllers import create_business_object_router
from app.framework_migration.{model}_service import {self.framework_service_class}, create_{model}_service
from app.framework_migration.{model}_schemas import (
    {self.model_name}FrameworkCreate,
    {self.model_name}FrameworkUpdate,
    {self.model_name}FrameworkResponse,
    {self.model_name}FrameworkListResponse
)


# === Framework-Generated Router ===
# This demonstrates the new framework approach with automatic CRUD operations

framework_{model}_router = create_business_object_router(
    model_class={self.model_name},
    service_class={self.framework_service_class},
    create_schema={self.model_name}FrameworkCreate,
    update_schema={self.model_name}FrameworkUpdate,
    response_schema={self.model_name}FrameworkResponse,
    prefix="/api/v1/{self.model_plural}",
    tags=["{self.model_plural}-framework"],
    enable_extensions=True,
    enable_audit_trail=True,
    enable_bulk_operations=True
)


# === Custom Router with Business Logic ===
# This maintains existing API patterns while using framework services

router = APIRouter(prefix="/{self.model_plural}-framework", tags=["{self.model_plural}-framework"])


async def get_{model}_service(db: AsyncSession = Depends(get_db)) -> {self.framework_service_class}:
    """Dependency to get {self.model_name} service instance."""
    return create_{model}_service(db)


@router.post("/", response_model={self.model_name}FrameworkResponse, status_code=status.HTTP_201_CREATED)
async def create_{model}(
    {model}_data: {self.model_name}FrameworkCreate,
    {model}_service: {self.framework_service_class} = Depends(get_{model}_service),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create a new {model} using framework service.
    
    Enhanced with automatic audit logging and event publishing.
    """
    # Verify user has access to the company
    await verify_company_access({model}_data.company_id, current_user)
    
    try:
        # Framework automatically handles audit logging and event publishing
        {model} = await {model}_service.create_{model}({model}_data)
        return {model}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model={self.model_name}FrameworkListResponse)
async def list_{self.model_plural}(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search term for {model} name, code, or description"),
    active_only: bool = Query(True, description="Return only active {self.model_plural}"),
    {model}_service: {self.framework_service_class} = Depends(get_{model}_service),
    current_user: dict = Depends(get_current_active_user)
):
    """
    List {self.model_plural} with pagination and filtering using framework service.
    
    Enhanced with automatic multi-company data isolation.
    """
    # If company_id is specified, verify access
    if company_id:
        await verify_company_access(company_id, current_user)
    
    {self.model_plural}, total = await {model}_service.get_{self.model_plural}(
        company_id=company_id,
        skip=skip,
        limit=limit,
        search=search,
        active_only=active_only
    )
    
    pages = math.ceil(total / limit) if total > 0 else 1
    page = (skip // limit) + 1
    
    return {self.model_name}FrameworkListResponse(
        {self.model_plural}={self.model_plural},
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.get("/{{object_id}}", response_model={self.model_name}FrameworkResponse)
async def get_{model}(
    object_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    {model}_service: {self.framework_service_class} = Depends(get_{model}_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific {model} by ID using framework service."""
    {model} = await {model}_service.get_{model}(object_id, company_id)
    if not {model}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{self.model_name} not found"
        )
    
    # Verify user has access to the {model}'s company
    await verify_company_access({model}.company_id, current_user)
    
    return {model}


@router.put("/{{object_id}}", response_model={self.model_name}FrameworkResponse)
async def update_{model}(
    object_id: int,
    {model}_data: {self.model_name}FrameworkUpdate,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    {model}_service: {self.framework_service_class} = Depends(get_{model}_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a {model} using framework service with automatic audit logging."""
    # First get the {model} to verify company access
    {model} = await {model}_service.get_{model}(object_id, company_id)
    if not {model}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{self.model_name} not found"
        )
    
    # Verify user has access to the {model}'s company
    await verify_company_access({model}.company_id, current_user)
    
    try:
        # Framework automatically handles audit logging and event publishing
        updated_{model} = await {model}_service.update_{model}(object_id, {model}_data, company_id)
        if not updated_{model}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{self.model_name} not found"
            )
        return updated_{model}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{{object_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{model}(
    object_id: int,
    company_id: Optional[int] = Query(None, description="Company ID for access verification"),
    {model}_service: {self.framework_service_class} = Depends(get_{model}_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Delete a {model} (soft delete) using framework service."""
    # First get the {model} to verify company access
    {model} = await {model}_service.get_{model}(object_id, company_id)
    if not {model}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{self.model_name} not found"
        )
    
    # Verify user has access to the {model}'s company
    await verify_company_access({model}.company_id, current_user)
    
    success = await {model}_service.delete_{model}(object_id, company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{self.model_name} not found"
        )


# === Additional Business Logic Endpoints ===

@router.get("/company/{{company_id}}/statistics")
async def get_{model}_statistics(
    company_id: int = Path(..., description="Company ID"),
    {model}_service: {self.framework_service_class} = Depends(get_{model}_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Get {model} statistics for a company."""
    # Verify user has access to the company
    await verify_company_access(company_id, current_user)
    
    statistics = await {model}_service.get_{model}_statistics(company_id)
    return statistics


@router.post("/bulk-create", response_model=list[{self.model_name}FrameworkResponse])
async def bulk_create_{self.model_plural}(
    {self.model_plural}_data: list[{self.model_name}FrameworkCreate],
    {model}_service: {self.framework_service_class} = Depends(get_{model}_service),
    current_user: dict = Depends(get_current_active_user)
):
    """Bulk create {self.model_plural} using framework service."""
    # Verify access to all companies
    company_ids = {{p.company_id for p in {self.model_plural}_data}}
    for company_id in company_ids:
        await verify_company_access(company_id, current_user)
    
    try:
        {self.model_plural} = await {model}_service.bulk_create_{self.model_plural}({self.model_plural}_data)
        return {self.model_plural}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
'''
        
        self._write_migration_file(f"app/framework_migration/{model}_router.py", router_content)
    
    def _create_migration_tests(self):
        """Create migration tests."""
        print("\n🧪 Creating migration tests...")
        
        test_content = f'''"""
Integration tests for migrating {self.model_name} service to Business Object Framework.

This test suite validates that the {self.model_name} service can be successfully migrated
to use the Business Object Framework while maintaining all existing functionality.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch, Mock
from typing import Dict, Any, List

from app.models.{model} import {self.model_name}
from app.framework_migration.{model}_schemas import {self.model_name}FrameworkCreate, {self.model_name}FrameworkUpdate, {self.model_name}FrameworkResponse
from app.framework_migration.{model}_service import {self.framework_service_class}


class Test{self.model_name}FrameworkCompatibility:
    """Test that {self.model_name} model is compatible with Business Object Framework."""
    
    def test_{model}_inherits_from_company_base_model(self):
        """Test that {self.model_name} inherits from CompanyBaseModel."""
        from app.models.base import CompanyBaseModel
        assert issubclass({self.model_name}, CompanyBaseModel)
        print("✓ {self.model_name} model inherits from CompanyBaseModel")
    
    def test_{model}_has_framework_fields(self):
        """Test that {self.model_name} has all required framework fields."""
        # Check that {self.model_name} model has required fields for framework
        {model}_columns = [column.name for column in {self.model_name}.__table__.columns]
        
        required_fields = ['id', 'company_id', 'created_at', 'updated_at']
        missing_fields = [field for field in required_fields if field not in {model}_columns]
        
        assert not missing_fields, f"{self.model_name} missing required fields: {{missing_fields}}"
        print(f"✓ {self.model_name} has all {{len(required_fields)}} required framework fields")


class Test{self.model_name}FrameworkSchemas:
    """Test {self.model_name} schema compatibility with framework schemas."""
    
    def test_framework_schema_validation(self):
        """Test that framework schemas validate correctly."""
        # Test valid {model} creation schema
        valid_data = {{
            "name": "Test {self.model_name}",
            "code": "TEST001",
            "company_id": 1
        }}
        
        {model}_create = {self.model_name}FrameworkCreate(**valid_data)
        assert {model}_create.name == valid_data["name"]
        assert {model}_create.company_id == valid_data["company_id"]
        print("✓ {self.model_name} creation schema validates correctly")


class Test{self.model_name}FrameworkService:
    """Test {self.model_name} service framework migration."""
    
    async def test_framework_service_methods(self):
        """Test that framework service has all expected methods."""
        mock_db = AsyncMock()
        service = {self.framework_service_class}(mock_db)
        
        expected_methods = [
            'create_{model}', 'get_{model}', 'update_{model}', 'delete_{model}',
            'activate_{model}', 'deactivate_{model}', 'get_{model}_by_code',
            'get_{self.model_plural}_by_company', 'get_{model}_statistics'
        ]
        
        for method_name in expected_methods:
            assert hasattr(service, method_name), f"Missing method: {{method_name}}"
        
        print("✓ {self.framework_service_class} has all expected methods")


def test_{model}_migration_integration_summary():
    """Summary test to verify {self.model_name} migration readiness."""
    
    print("\\n🧪 {self.model_name} Migration Integration Test Summary:")
    print("=" * 60)
    
    # Model compatibility
    from app.models.base import CompanyBaseModel
    assert issubclass({self.model_name}, CompanyBaseModel)
    print("✅ {self.model_name} model is framework compatible")
    
    # Schema compatibility
    {model}_create = {self.model_name}FrameworkCreate(name="Test", company_id=1)
    assert {model}_create.name == "Test"
    print("✅ {self.model_name} schemas are framework compatible")
    
    print("\\n🎉 {self.model_name} is ready for migration to Business Object Framework!")
    print("📋 Migration will provide:")
    print("  • Standardized CRUD endpoints")
    print("  • Custom field support via extension endpoints")
    print("  • Audit trail endpoints")
    print("  • Consistent error handling and response formatting")
    print("  • Automatic multi-company isolation")
    print("  • Type-safe operations with Pydantic validation")


if __name__ == "__main__":
    # Run the summary test
    test_{model}_migration_integration_summary()
'''
        
        self._write_migration_file(f"tests/test_{model}_migration_integration.py", test_content)
    
    def _update_main_app(self):
        """Create updated main application integration."""
        print("\n📱 Creating main application integration...")
        
        main_app_content = f'''"""
Updated main application with framework-based {self.model_name} endpoints.

This demonstrates how to integrate the framework-based {self.model_name} service
into the main FastAPI application.
"""

from fastapi import FastAPI
from app.framework_migration.{model}_router import router as framework_{model}_router
from app.framework_migration.{model}_router import framework_{model}_router as generated_{model}_router

# Add to existing FastAPI app
def include_framework_{model}_routes(app: FastAPI):
    """Include framework-based {self.model_name} routes in the application."""
    
    # Option 1: Custom router with business logic
    app.include_router(framework_{model}_router, prefix="/api/v1")
    
    # Option 2: Auto-generated framework router
    app.include_router(generated_{model}_router.router, prefix="/api/v1")
    
    print("✅ Framework-based {self.model_name} routes included")
    print("📋 Available endpoints:")
    print("  • /api/v1/{self.model_plural}-framework/ - Custom framework router")
    print("  • /api/v1/{self.model_plural}/ - Auto-generated framework router")
    print("  • Both routers include extension and audit endpoints")


# Example usage in main.py:
\"\"\"
from app.framework_migration.{model}_main_app_update import include_framework_{model}_routes

app = FastAPI(title="XERPIUM", version="2.0.0")

# Include framework routes
include_framework_{model}_routes(app)
\"\"\"
'''
        
        self._write_migration_file(f"app/framework_migration/{model}_main_app_update.py", main_app_content)
    
    def _create_migration_docs(self):
        """Create migration documentation."""
        print("\n📚 Creating migration documentation...")
        
        migration_guide_content = f'''# {self.model_name} Service Migration Guide

## Overview

This document describes the migration of the {self.model_name} service from a traditional implementation to the Business Object Framework. The migration maintains full API compatibility while adding powerful new capabilities.

## Migration Benefits

### 🚀 Enhanced Capabilities
- **Custom Fields**: Add custom fields to {self.model_plural} without database changes
- **Audit Trail**: Automatic tracking of all {model} changes
- **Event Publishing**: Automatic event publishing for {model} operations
- **Bulk Operations**: Efficient bulk create/update/delete operations
- **Standardized APIs**: Consistent error handling and response formatting

### 🔧 Developer Experience
- **Type Safety**: Full Pydantic validation with type hints
- **Auto-documentation**: Comprehensive OpenAPI documentation
- **Test Coverage**: Built-in test patterns and utilities
- **Extension Endpoints**: Automatic extension field management APIs

## Generated Files

### Framework Implementation
- `app/framework_migration/{model}_schemas.py` - Framework-based schemas
- `app/framework_migration/{model}_service.py` - Framework-based service
- `app/framework_migration/{model}_router.py` - Framework-based router
- `app/framework_migration/{model}_main_app_update.py` - Application integration

### Testing and Documentation
- `tests/test_{model}_migration_integration.py` - Integration tests
- `docs/{self.model_name.upper()}_MIGRATION_GUIDE.md` - This guide

## API Compatibility

### Existing Endpoints Maintained
All existing {self.model_name} API endpoints are maintained with identical behavior:

- `POST /{self.model_plural}/` - Create {model}
- `GET /{self.model_plural}/` - List {self.model_plural} with pagination
- `GET /{self.model_plural}/{{id}}` - Get {model} by ID
- `PUT /{self.model_plural}/{{id}}` - Update {model}
- `DELETE /{self.model_plural}/{{id}}` - Soft delete {model}

### New Framework Endpoints
Additional endpoints provided by the framework:

- `GET /{self.model_plural}/{{id}}/extensions` - Get custom fields
- `POST /{self.model_plural}/{{id}}/extensions` - Set custom field
- `DELETE /{self.model_plural}/{{id}}/extensions/{{field}}` - Remove custom field
- `GET /{self.model_plural}/{{id}}/audit` - Get audit trail
- `POST /{self.model_plural}/bulk-create` - Bulk create {self.model_plural}
- `GET /{self.model_plural}/company/{{id}}/statistics` - {self.model_name} statistics

## Migration Process

### Phase 1: Review Generated Files
1. Review `app/framework_migration/{model}_schemas.py`
2. Review `app/framework_migration/{model}_service.py`
3. Review `app/framework_migration/{model}_router.py`
4. Customize business logic as needed

### Phase 2: Testing
1. Run integration tests: `pytest tests/test_{model}_migration_integration.py`
2. Test API endpoints manually
3. Verify custom field functionality
4. Test audit logging

### Phase 3: Deployment
1. Deploy framework files alongside existing implementation
2. Use different API prefixes for testing
3. Switch main application routes when ready
4. Remove old implementation

## Customization Guidelines

### Adding Business Logic
Add {model}-specific methods to `{self.framework_service_class}`:

```python
async def find_active_{self.model_plural}(self, company_id: int) -> List[{self.model_name}]:
    \"\"\"Find all active {self.model_plural} for a company.\"\"\"
    return await self.get_list({{"company_id": company_id, "is_active": True}})
```

### Custom Validation
Add validators to `{self.model_name}FrameworkCreate` and `{self.model_name}FrameworkUpdate`:

```python
@validator('custom_field')
def validate_custom_field(cls, v):
    \"\"\"Validate custom field.\"\"\"
    # Add your validation logic
    return v
```

### Additional Endpoints
Add business-specific endpoints to the custom router:

```python
@router.get("/company/{{company_id}}/active")
async def get_active_{self.model_plural}(company_id: int):
    \"\"\"Get active {self.model_plural} for a company.\"\"\"
    # Implementation here
```

## Next Steps

1. **Review Generated Files**: Examine all framework files
2. **Customize Business Logic**: Add {model}-specific functionality
3. **Run Tests**: Execute integration test suite
4. **Deploy to Staging**: Test in staging environment
5. **Production Migration**: Deploy when ready

---

*Migration completed successfully! The {self.model_name} service now benefits from the Business Object Framework.*
'''
        
        self._write_migration_file(f"docs/{self.model_name.upper()}_MIGRATION_GUIDE.md", migration_guide_content)
    
    def _write_migration_file(self, relative_path: str, content: str):
        """Write migration file with proper directory creation."""
        file_path = self.service_root / relative_path
        
        if not self.dry_run:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content.strip())
            print(f"  ✓ Created {relative_path}")
        else:
            print(f"  [DRY RUN] Would create {relative_path}")


def main():
    """Main migration script entry point."""
    parser = argparse.ArgumentParser(description="Migrate {self.model_name} service to Business Object Framework")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without making changes")
    parser.add_argument("--backup", action="store_true", help="Create backup of existing files before migration")
    parser.add_argument("--service-root", default=".", help="Root directory of the service")
    
    args = parser.parse_args()
    
    try:
        migration = {Service}FrameworkMigration(
            service_root=args.service_root,
            dry_run=args.dry_run,
            backup=args.backup
        )
        migration.run_migration()
        
    except Exception as e:
        print(f"\\n❌ Migration failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())