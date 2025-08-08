"""
Event and Message Type definitions for XERPIUM messaging system.
"""
from enum import Enum


class MessageType(str, Enum):
    """Types of messages in the system."""
    EVENT = "event"           # Business events (user created, company updated, etc.)
    COMMAND = "command"       # Service commands (create user, update partner, etc.)
    NOTIFICATION = "notification"  # UI notifications and real-time updates


class EventType(str, Enum):
    """Business event types for event-driven architecture."""
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated" 
    USER_DELETED = "user.deleted"
    USER_LOGGED_IN = "user.logged_in"
    USER_LOGGED_OUT = "user.logged_out"
    USER_PASSWORD_CHANGED = "user.password_changed"
    USER_LOCKED = "user.locked"
    USER_UNLOCKED = "user.unlocked"
    
    # Company events
    COMPANY_CREATED = "company.created"
    COMPANY_UPDATED = "company.updated"
    COMPANY_DELETED = "company.deleted"
    COMPANY_ACTIVATED = "company.activated"
    COMPANY_DEACTIVATED = "company.deactivated"
    
    # Partner events
    PARTNER_CREATED = "partner.created"
    PARTNER_UPDATED = "partner.updated"
    PARTNER_DELETED = "partner.deleted"
    PARTNER_ADDRESS_ADDED = "partner.address_added"
    PARTNER_CONTACT_ADDED = "partner.contact_added"
    
    # Currency events
    CURRENCY_CREATED = "currency.created"
    CURRENCY_UPDATED = "currency.updated"
    CURRENCY_RATE_UPDATED = "currency.rate_updated"
    
    # System events
    SERVICE_STARTED = "service.started"
    SERVICE_STOPPED = "service.stopped"
    SERVICE_HEALTH_CHECK = "service.health_check"
    
    # Audit events
    SECURITY_VIOLATION = "security.violation"
    AUDIT_LOG_CREATED = "audit.log_created"
    
    # Menu/Access events  
    ROLE_CREATED = "role.created"
    ROLE_UPDATED = "role.updated"
    ROLE_DELETED = "role.deleted"
    PERMISSION_GRANTED = "permission.granted"
    PERMISSION_REVOKED = "permission.revoked"


class CommandType(str, Enum):
    """Command types for inter-service communication."""
    
    # User commands
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    VALIDATE_TOKEN = "validate_token"
    
    # Company commands  
    CREATE_COMPANY = "create_company"
    UPDATE_COMPANY = "update_company"
    DELETE_COMPANY = "delete_company"
    
    # Partner commands
    CREATE_PARTNER = "create_partner"
    UPDATE_PARTNER = "update_partner"
    DELETE_PARTNER = "delete_partner"
    
    # System commands
    HEALTH_CHECK = "health_check"
    RELOAD_CONFIG = "reload_config"


class NotificationType(str, Enum):
    """Notification types for UI updates."""
    
    # Success notifications
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    
    # Real-time updates
    DATA_UPDATED = "data_updated"
    USER_ACTIVITY = "user_activity"
    SYSTEM_ALERT = "system_alert"