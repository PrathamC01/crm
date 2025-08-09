"""
Response utility functions for standardized API responses
"""

from typing import Any, Dict, Optional, Union
from ..schemas.auth import StandardResponse


def create_response(
    success: bool,
    message: str,
    data: Optional[Union[Dict[str, Any], list, str, int, float]] = None,
    error: Optional[Union[str, Dict[str, Any]]] = None
) -> StandardResponse:
    """
    Create a standardized API response
    
    Args:
        success: Boolean indicating if the operation was successful
        message: Human-readable message describing the result
        data: Optional data payload
        error: Optional error information
        
    Returns:
        StandardResponse: Standardized response object
    """
    return StandardResponse(
        status=success,
        message=message,
        data=data,
        error=error
    )


def create_success_response(
    message: str,
    data: Optional[Union[Dict[str, Any], list, str, int, float]] = None
) -> StandardResponse:
    """
    Create a success response
    
    Args:
        message: Success message
        data: Optional data payload
        
    Returns:
        StandardResponse: Success response object
    """
    return create_response(success=True, message=message, data=data)


def create_error_response(
    message: str,
    error: Optional[Union[str, Dict[str, Any]]] = None
) -> StandardResponse:
    """
    Create an error response
    
    Args:
        message: Error message
        error: Optional detailed error information
        
    Returns:
        StandardResponse: Error response object
    """
    return create_response(success=False, message=message, error=error)