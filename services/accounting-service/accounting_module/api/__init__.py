"""
Accounting Module API Package
"""

from fastapi import APIRouter

# Create API routers for different modules
accounts_router = APIRouter(prefix="/accounts", tags=["accounts"])
journal_entries_router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])
bank_router = APIRouter(prefix="/bank", tags=["bank"])
reports_router = APIRouter(prefix="/reports", tags=["reports"])