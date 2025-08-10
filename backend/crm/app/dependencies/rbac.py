"""
Role-Based Access Control dependencies
"""

from fastapi import Depends, HTTPException, status
from functools import wraps
from typing import List, Optional
from .auth import get_current_user


def check_permissions(required_permissions: List[str], require_all: bool = False):
    """
    Decorator to check user permissions for endpoints

    Args:
        required_permissions: List of required permissions
        require_all: If True, user must have ALL permissions. If False, user needs ANY permission.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependencies
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, dict) and "id" in value and "permissions" in value:
                    current_user = value
                    break

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check if user has required permissions
            user_permissions = current_user.get("permissions", [])

            # Super admin has all permissions
            if "all" in user_permissions:
                return await func(*args, **kwargs)

            # Check specific permissions
            if require_all:
                # User must have ALL required permissions
                has_permission = all(
                    perm in user_permissions for perm in required_permissions
                )
            else:
                # User must have ANY of the required permissions
                has_permission = any(
                    perm in user_permissions for perm in required_permissions
                )

            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {required_permissions}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def require_permission(
    permission: str, current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to require a specific permission
    """
    user_permissions = current_user.get("permissions", [])

    # Super admin has all permissions  
    if "all" in user_permissions or "*" in user_permissions:
        return current_user

    if permission not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission required: {permission}",
        )

    return current_user


async def require_any_permission(
    permissions: List[str], current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to require any of the specified permissions
    """
    user_permissions = current_user.get("permissions", [])
    required_permissions = permissions + ["*"]  # Don't modify the original list
    
    # Super admin has all permissions
    if "all" in user_permissions or "*" in user_permissions:
        return current_user

    print(f"User permissions: {user_permissions}")
    print(f"Required permissions: {required_permissions}")
    has_permission = any(perm in user_permissions for perm in required_permissions)
    print(f"Has permission: {has_permission}")
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"One of these permissions required: {required_permissions}",
        )

    return current_user


async def require_all_permissions(
    permissions: List[str], current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to require all of the specified permissions
    """
    required_permissions = permissions + ["*"]  # Don't modify the original list
    user_permissions = current_user.get("permissions", [])

    # Super admin has all permissions
    if "all" in user_permissions or "*" in user_permissions:
        return current_user

    if not all(perm in user_permissions for perm in required_permissions):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"All of these permissions required: {required_permissions}",
        )

    return current_user


# Specific permission dependencies
async def require_users_read(current_user: dict = Depends(get_current_user)) -> dict:
    return await require_any_permission(["users:read"], current_user)


async def require_users_write(current_user: dict = Depends(get_current_user)) -> dict:
    return await require_any_permission(["users:write", "users:all"], current_user)


async def require_companies_read(
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await require_any_permission(
        ["companies:read", "companies:all"], current_user
    )


async def require_companies_write(
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await require_any_permission(
        ["companies:write", "companies:all"], current_user
    )


async def require_contacts_read(current_user: dict = Depends(get_current_user)) -> dict:
    return await require_any_permission(["contacts:read", "contacts:all"], current_user)


async def require_contacts_write(
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await require_any_permission(
        ["contacts:write", "contacts:all"], current_user
    )


async def require_leads_read(current_user: dict = Depends(get_current_user)) -> dict:
    return await require_any_permission(["leads:read", "leads:all"], current_user)


async def require_leads_write(current_user: dict = Depends(get_current_user)) -> dict:
    return await require_any_permission(["leads:write", "leads:all"], current_user)


async def require_opportunities_read(
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await require_any_permission(
        ["opportunities:read", "opportunities:all"], current_user
    )


async def require_opportunities_write(
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await require_any_permission(
        ["opportunities:write", "opportunities:all"], current_user
    )


# Role-based dependencies
async def require_admin_role(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin or super_admin role"""
    role_name = current_user.get("role", "")
    print(current_user)
    if role_name not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required"
        )
    return current_user


async def require_sales_role(current_user: dict = Depends(get_current_user)) -> dict:
    """Require sales manager or sales executive role"""
    role_name = current_user.get("role_name", "")
    if role_name not in ["sales_manager", "sales_executive", "admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sales role required"
        )
    return current_user


async def require_marketing_or_sales_role(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Require marketing, sales, or admin role"""
    role_name = current_user.get("role_name", "")
    if role_name not in [
        "marketing",
        "sales_manager",
        "sales_executive",
        "admin",
        "super_admin",
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Marketing or Sales role required",
        )
    return current_user


def get_user_permissions(user: dict) -> List[str]:
    """Extract user permissions from user object"""
    permissions = user.get("permissions", [])
    if isinstance(permissions, str):
        # Handle case where permissions is stored as JSON string
        import json

        try:
            permissions = json.loads(permissions)
        except:
            permissions = []
    return permissions if isinstance(permissions, list) else []


def has_permission(user: dict, permission: str) -> bool:
    """Check if user has a specific permission"""
    permissions = get_user_permissions(user)
    return "all" in permissions or permission in permissions


def has_any_permission(user: dict, required_permissions: List[str]) -> bool:
    """Check if user has any of the required permissions"""
    permissions = get_user_permissions(user)
    if "all" in permissions:
        return True
    return any(perm in permissions for perm in required_permissions)


def has_all_permissions(user: dict, required_permissions: List[str]) -> bool:
    """Check if user has all of the required permissions"""
    permissions = get_user_permissions(user)
    if "all" in permissions:
        return True
    return all(perm in permissions for perm in required_permissions)
