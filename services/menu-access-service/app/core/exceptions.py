"""Custom exceptions for the application."""

class BaseAppException(Exception):
    """Base exception for all application exceptions."""
    pass


class NotFoundException(BaseAppException):
    """Exception raised when a resource is not found."""
    pass


class BadRequestException(BaseAppException):
    """Exception raised for bad requests."""
    pass


class UnauthorizedException(BaseAppException):
    """Exception raised for unauthorized access."""
    pass


class ForbiddenException(BaseAppException):
    """Exception raised for forbidden access."""
    pass


class ConflictException(BaseAppException):
    """Exception raised for resource conflicts."""
    pass