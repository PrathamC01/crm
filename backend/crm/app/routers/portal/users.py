"""
User Management API endpoints with SQLAlchemy
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ...schemas.user import UserCreate, UserUpdate
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_users_read, require_users_write, require_admin_role
from ...dependencies.database import get_postgres_db
from ...services.user_service import UserService
from ...models import Role, Department

router = APIRouter(prefix="/api/users", tags=["User Management"])

def get_user_service(db: Session = Depends(get_postgres_db)) -> UserService:
    return UserService(db)

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
        users = user_service.get_users(skip, limit, search)
        total = user_service.get_user_count(search)
        
        # Convert SQLAlchemy objects to dict
        users_data = []
        for user in users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "username": user.username,
                "role_name": user.role.name if user.role else None,
                "department_name": user.department.name if user.department else None,
                "is_active": user.is_active,
                "created_on": user.created_on.isoformat() if user.created_on else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            users_data.append(user_dict)
        
        return StandardResponse(
            status=True,
            message="Users retrieved successfully",
            data={
                "users": users_data,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=StandardResponse)
async def get_user(
    user_id: int,
    current_user: dict = Depends(require_users_read),
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID"""
    try:
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "role_id": user.role_id if user.role_id else None,
            "role_name": user.role.name if user.role else None,
            "department_id": user.department_id if user.department_id else None,
            "department_name": user.department.name if user.department else None,
            "is_active": user.is_active,
            "created_on": user.created_on.isoformat() if user.created_on else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        return StandardResponse(
            status=True,
            message="User retrieved successfully",
            data=user_data
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
        user = user_service.create_user(user_data, current_user["id"])
        
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "role_id": user.role_id if user.role_id else None,
            "department_id": user.department_id if user.department_id else None,
            "is_active": user.is_active,
            "created_on": user.created_on.isoformat() if user.created_on else None
        }
        
        return StandardResponse(
            status=True,
            message="User created successfully",
            data=user_dict
        )
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Email or username already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=StandardResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: dict = Depends(require_users_write),
    user_service: UserService = Depends(get_user_service)
):
    """Update user information"""
    try:
        user = user_service.update_user(user_id, user_data, current_user["id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "role_id": user.role_id if user.role_id else None,
            "department_id": user.department_id if user.department_id else None,
            "is_active": user.is_active,
            "updated_on": user.updated_on.isoformat() if user.updated_on else None
        }
        
        return StandardResponse(
            status=True,
            message="User updated successfully",
            data=user_dict
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}", response_model=StandardResponse)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(require_admin_role),
    user_service: UserService = Depends(get_user_service)
):
    """Soft delete user"""
    try:
        deleted = user_service.delete_user(user_id, current_user["id"])
        if not deleted:
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
    db: Session = Depends(get_postgres_db)
):
    """Get all roles"""
    try:
        roles = db.query(Role).filter(Role.is_active == True).all()
        roles_data = [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": role.permissions
            }
            for role in roles
        ]
        
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
    db: Session = Depends(get_postgres_db)
):
    """Get all departments"""
    try:
        departments = db.query(Department).filter(Department.is_active == True).all()
        departments_data = [
            {
                "id": dept.id,
                "name": dept.name,
                "description": dept.description
            }
            for dept in departments
        ]
        
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
    user_service: UserService = Depends(get_user_service)
):
    """Get all sales people for lead assignment"""
    try:
        sales_people = user_service.get_sales_people()
        sales_data = [
            {
                "id": str(person.id),
                "name": person.name,
                "email": person.email,
                "role_name": person.role.name if person.role else None
            }
            for person in sales_people
        ]
        
        return StandardResponse(
            status=True,
            message="Sales people retrieved successfully",
            data={"sales_people": sales_data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))