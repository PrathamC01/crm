"""
User Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from ...schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, 
    UserPasswordUpdate, RoleResponse, DepartmentResponse
)
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_users_read, require_users_write, require_admin_role
from ...dependencies.auth import get_user_service
from ...services.user_service import UserService
from ...models.role import Role
from ...models.department import Department
from ...dependencies.database import get_postgres_pool

router = APIRouter(prefix="/api/users", tags=["User Management"])

@router.get("/", response_model=StandardResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_users_read),
    user_service: UserService = Depends(get_user_service)
):
    """Get all users with pagination and search"""
    try:
        users = await user_service.get_all_users(skip, limit, search)
        total = len(users)  # For now, we'll get actual count later
        
        return StandardResponse(
            status=True,
            message="Users retrieved successfully",
            data={
                "users": users,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=StandardResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(require_users_read),
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return StandardResponse(
            status=True,
            message="User retrieved successfully",
            data=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=StandardResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_users_write),
    user_service: UserService = Depends(get_user_service)
):
    """Create new user"""
    try:
        user = await user_service.create_user(user_data, current_user["id"])
        
        return StandardResponse(
            status=True,
            message="User created successfully",
            data=user
        )
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email or username already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=StandardResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(require_users_write),
    user_service: UserService = Depends(get_user_service)
):
    """Update user information"""
    try:
        user = await user_service.update_user(user_id, user_data, current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return StandardResponse(
            status=True,
            message="User updated successfully",
            data=user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}", response_model=StandardResponse)
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_admin_role),
    postgres_pool = Depends(get_postgres_pool)
):
    """Soft delete user"""
    try:
        async with postgres_pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE users 
                SET is_active = false, deleted_on = CURRENT_TIMESTAMP, deleted_by = $1
                WHERE id = $2 AND is_active = true
            """, current_user["id"], user_id)
            
            if result != "UPDATE 1":
                raise HTTPException(status_code=404, detail="User not found")
        
        return StandardResponse(
            status=True,
            message="User deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roles/list", response_model=StandardResponse)
async def get_roles(
    current_user: dict = Depends(require_users_read),
    postgres_pool = Depends(get_postgres_pool)
):
    """Get all roles"""
    try:
        async with postgres_pool.acquire() as conn:
            roles = await Role.get_all(conn)
            roles_data = [dict(role) for role in roles]
        
        return StandardResponse(
            status=True,
            message="Roles retrieved successfully",
            data={"roles": roles_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/departments/list", response_model=StandardResponse)
async def get_departments(
    current_user: dict = Depends(require_users_read),
    postgres_pool = Depends(get_postgres_pool)
):
    """Get all departments"""
    try:
        async with postgres_pool.acquire() as conn:
            departments = await Department.get_all(conn)
            departments_data = [dict(dept) for dept in departments]
        
        return StandardResponse(
            status=True,
            message="Departments retrieved successfully",
            data={"departments": departments_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sales-people/list", response_model=StandardResponse)
async def get_sales_people(
    current_user: dict = Depends(require_users_read),
    postgres_pool = Depends(get_postgres_pool)
):
    """Get all sales people for lead assignment"""
    try:
        from ...models.user import User
        async with postgres_pool.acquire() as conn:
            sales_people = await User.get_sales_people(conn)
            sales_data = [dict(person) for person in sales_people]
        
        return StandardResponse(
            status=True,
            message="Sales people retrieved successfully",
            data={"sales_people": sales_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))