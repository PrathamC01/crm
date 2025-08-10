"""
Example of how to use the centralized error handling system in route handlers.

This file demonstrates how to replace inline exception handling with 
custom exceptions that are handled by the centralized error handlers.
"""

from fastapi import APIRouter, Depends
from ..schemas.auth import StandardResponse
from ..exceptions.custom_exceptions import (
    NotFoundError,
    ValidationError,
    DuplicateError,
    BusinessLogicError,
    UnauthorizedError
)

# Example route handlers showing proper error handling

async def example_get_resource(resource_id: int):
    """Example of handling Not Found errors"""
    # Instead of: raise HTTPException(status_code=404, detail="Resource not found")
    # Use this:
    resource = None  # Simulate database lookup
    if not resource:
        raise NotFoundError("Resource", resource_id)
    
    return StandardResponse(
        status=True,
        message="Resource retrieved successfully", 
        data=resource
    )


async def example_create_resource(data):
    """Example of handling validation and duplicate errors"""
    # Business logic validation
    if not data.name or len(data.name) < 2:
        raise ValidationError(
            "Invalid resource data",
            {"name": "Name must be at least 2 characters"}
        )
    
    # Check for duplicates
    existing = None  # Simulate database check
    if existing:
        raise DuplicateError("Resource", "name")
    
    # Business rule validation
    if data.price < 0:
        raise BusinessLogicError("Price cannot be negative")
    
    return StandardResponse(
        status=True,
        message="Resource created successfully",
        data={"id": 1, "name": data.name}
    )


async def example_admin_only_action(current_user):
    """Example of handling authorization errors"""
    if current_user.role != "admin":
        raise UnauthorizedError("access admin features")
    
    return StandardResponse(
        status=True,
        message="Admin action completed successfully"
    )


# Database service layer examples
class ExampleService:
    """Example service showing how to let database errors bubble up"""
    
    def create_user(self, user_data):
        """
        Let SQLAlchemy IntegrityError bubble up to be caught by 
        the centralized sqlalchemy_exception_handler
        """
        # Instead of catching and re-raising, just let it bubble up:
        # try:
        #     db.add(user)
        #     db.commit()
        # except IntegrityError:
        #     raise HTTPException(...)
        
        # Just do the operation - centralized handler will catch any IntegrityError
        # db.add(user)  
        # db.commit()
        pass
    
    def validate_business_rules(self, data):
        """Use custom exceptions for business logic validation"""
        if data.age < 18:
            raise BusinessLogicError("User must be at least 18 years old")
        
        if data.email in ["admin@system.com"]:
            raise ValidationError(
                "Invalid email address", 
                {"email": "This email is reserved"}
            )


# Benefits of this approach:
"""
1. **Consistent Error Responses**: All errors follow the same format
2. **Cleaner Route Handlers**: No try/catch blocks cluttering the logic  
3. **Centralized Logic**: Error handling logic is in one place
4. **Better Debugging**: Centralized logging and error tracking
5. **Type Safety**: Custom exceptions are more specific than generic HTTPException
6. **Maintainability**: Easy to modify error behavior across the entire app
7. **Database Error Parsing**: Intelligent parsing of PostgreSQL errors
8. **Field-Level Errors**: Detailed field-specific error messages

Before (with inline handling):
    try:
        user = get_user(id) 
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

After (with centralized handling):
    user = get_user(id)
    if not user:
        raise NotFoundError("User", id)
    return user
"""