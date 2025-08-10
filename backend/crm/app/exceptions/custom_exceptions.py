"""
Custom application exceptions for the CRM system.
These exceptions are designed to map to specific HTTP status codes
and provide structured error responses.
"""

from fastapi import HTTPException
from typing import Optional, Dict, Any, Union


class CRMBaseException(Exception):
    """Base exception class for CRM application"""
    
    def __init__(self, message: str = "Application error", status_code: int = 422, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationError(CRMBaseException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, details)


class NotFoundError(CRMBaseException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource: str = "Resource", resource_id: Union[str, int] = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(message, 404)


class DuplicateError(CRMBaseException):
    """Raised when trying to create a duplicate resource"""
    
    def __init__(self, resource: str = "Resource", field: str = "identifier"):
        message = f"{resource} with this {field} already exists"
        super().__init__(message, 409, {"field": field, "error": f"Duplicate {field}"})


class ConflictError(CRMBaseException):
    """Raised when there's a business logic conflict"""
    
    def __init__(self, message: str = "Conflict in business logic"):
        super().__init__(message, 409)


class UnauthorizedError(CRMBaseException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, action: str = "perform this action"):
        message = f"You are not authorized to {action}"
        super().__init__(message, 403)


class BusinessLogicError(CRMBaseException):
    """Raised when business rules are violated"""
    
    def __init__(self, message: str = "Business rule violation"):
        super().__init__(message, 422)


class DatabaseIntegrityError(CRMBaseException):
    """Raised when database integrity constraints are violated"""
    
    def __init__(self, message: str = "Database integrity constraint violated", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, details)


class ExternalServiceError(CRMBaseException):
    """Raised when external service calls fail"""
    
    def __init__(self, service: str = "External service", message: str = "unavailable"):
        super().__init__(f"{service} {message}", 503)


class RateLimitError(CRMBaseException):
    """Raised when rate limits are exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, 429)


class FileProcessingError(CRMBaseException):
    """Raised when file upload or processing fails"""
    
    def __init__(self, message: str = "File processing failed"):
        super().__init__(message, 422)