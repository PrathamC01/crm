"""
Centralized error handlers for the CRM FastAPI application.
Provides consistent error response format and handles various exception types.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, DBAPIError
from pydantic import ValidationError as PydanticValidationError
import traceback
import re
import logging
from typing import Dict, Any

from .custom_exceptions import CRMBaseException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_database_error(detail: str) -> Dict[str, Any]:
    """
    Parse database error details to extract field-specific information.
    Handles PostgreSQL-specific error messages.
    """
    error_details = {}
    
    # PostgreSQL unique constraint violation
    unique_match = re.search(r'duplicate key value violates unique constraint "([^"]+)"', detail, re.IGNORECASE)
    if unique_match:
        constraint_name = unique_match.group(1)
        # Try to extract field name from constraint
        field_match = re.search(r'Key \(([^)]+)\)=\(([^)]+)\)', detail)
        if field_match:
            field_name, field_value = field_match.groups()
            error_details[field_name] = f"Value '{field_value}' already exists"
        else:
            error_details["constraint"] = f"Duplicate value for constraint '{constraint_name}'"
        return error_details
    
    # PostgreSQL foreign key constraint violation
    foreign_key_match = re.search(r'violates foreign key constraint "([^"]+)"', detail, re.IGNORECASE)
    if foreign_key_match:
        constraint_name = foreign_key_match.group(1)
        # Try to extract referenced table/field
        key_match = re.search(r'Key \(([^)]+)\)=\(([^)]+)\)', detail)
        if key_match:
            field_name, field_value = key_match.groups()
            error_details[field_name] = f"Referenced record with value '{field_value}' does not exist"
        else:
            error_details["reference"] = f"Foreign key constraint '{constraint_name}' violation"
        return error_details
    
    # PostgreSQL check constraint violation
    check_match = re.search(r'violates check constraint "([^"]+)"', detail, re.IGNORECASE)
    if check_match:
        constraint_name = check_match.group(1)
        error_details["constraint"] = f"Check constraint '{constraint_name}' violation"
        return error_details
    
    # PostgreSQL enum value error
    enum_match = re.search(r'invalid input value for enum ([^:]+): "([^"]+)"', detail, re.IGNORECASE)
    if enum_match:
        enum_type, invalid_value = enum_match.groups()
        error_details["enum_value"] = f"Invalid value '{invalid_value}' for enum type '{enum_type}'"
        return error_details
    
    # PostgreSQL not-null constraint
    not_null_match = re.search(r'null value in column "([^"]+)" violates not-null constraint', detail, re.IGNORECASE)
    if not_null_match:
        field_name = not_null_match.group(1)
        error_details[field_name] = "This field is required"
        return error_details
    
    # Generic error
    error_details["detail"] = detail
    return error_details


async def custom_exception_handler(request: Request, exc: CRMBaseException):
    """Handle custom CRM exceptions"""
    logger.warning(f"CRM Exception: {exc.message} - Status: {exc.status_code}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": exc.message,
            "error": exc.details
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI/Starlette HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.detail} - Status: {exc.status_code}")
    
    # Handle cases where detail might be a dict or string
    if isinstance(exc.detail, dict):
        message = exc.detail.get("message", "HTTP error occurred")
        error = exc.detail.get("error", {})
    else:
        message = str(exc.detail) if exc.detail else "HTTP error occurred"
        error = {}
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": message,
            "error": error
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation Error: {exc.errors()}")
    
    errors = {}
    for err in exc.errors():
        # Build field path (e.g., "body.company_id" or "query.limit")
        loc = err['loc']
        field_path = ".".join(str(x) for x in loc if isinstance(x, (str, int)) and x not in ['body', 'query', 'path'])
        
        # Clean up field path
        if not field_path:
            field_path = str(loc[-1]) if loc else "unknown_field"
        
        # Get error message
        error_msg = err['msg']
        error_type = err.get('type', '')
        
        # Customize error messages for better UX
        if error_type == 'missing':
            error_msg = "This field is required"
        elif error_type == 'type_error':
            if 'int' in error_type:
                error_msg = "Must be a valid integer"
            elif 'float' in error_type:
                error_msg = "Must be a valid number"
            elif 'str' in error_type:
                error_msg = "Must be a valid string"
        elif error_type.startswith('value_error'):
            # Keep original message for value errors as they're usually descriptive
            pass
        
        errors[field_path] = error_msg
    
    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "message": "Validation failed",
            "error": errors
        }
    )


async def pydantic_validation_exception_handler(request: Request, exc: PydanticValidationError):
    """Handle Pydantic model validation errors"""
    logger.warning(f"Pydantic Validation Error: {exc.errors()}")
    
    errors = {}
    for err in exc.errors():
        loc = err['loc']
        field_path = ".".join(str(x) for x in loc)
        errors[field_path] = err['msg']
    
    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "message": "Data validation failed",
            "error": errors
        }
    )


async def sqlalchemy_exception_handler(request: Request, exc: IntegrityError):
    """Handle SQLAlchemy integrity errors"""
    detail = str(exc.orig) if exc.orig else str(exc)
    logger.error(f"Database Integrity Error: {detail}")
    
    error_details = parse_database_error(detail)
    
    # Determine appropriate status code and message based on error type
    if any(keyword in detail.lower() for keyword in ['duplicate', 'unique constraint']):
        status_code = 409
        message = "Duplicate entry detected"
    elif 'foreign key' in detail.lower():
        status_code = 422
        message = "Referenced record does not exist"
    elif any(keyword in detail.lower() for keyword in ['check constraint', 'enum']):
        status_code = 422
        message = "Invalid data value"
    elif 'not-null constraint' in detail.lower():
        status_code = 422
        message = "Required field is missing"
    else:
        status_code = 422
        message = "Database constraint violation"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": False,
            "message": message,
            "error": error_details
        }
    )


async def database_exception_handler(request: Request, exc: DBAPIError):
    """Handle general database API errors"""
    detail = str(exc.orig) if exc.orig else str(exc)
    logger.error(f"Database API Error: {detail}")
    
    error_details = parse_database_error(detail)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "Database operation failed",
            "error": error_details
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions"""
    # Log the full traceback for debugging
    logger.error(f"Unhandled Exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Print to console for development (remove in production)
    print(f"❌ Unhandled Exception: {str(exc)}")
    traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "Internal Server Error",
            "error": {}
        }
    )