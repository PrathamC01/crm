"""
Authentication and authorization dependencies
"""
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..database import get_db
from ..redis_client import redis_client
from ..models.masters import UserMaster, RolesMaster, PermissionMaster

async def get_session_id(x_session_id: Optional[str] = Header(None)) -> str:
    """Extract session ID from headers"""
    if not x_session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session ID header missing"
        )
    return x_session_id

async def get_current_user(
    session_id: str = Depends(get_session_id),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current authenticated user from session"""
    # Get session data from Redis
    session_data = redis_client.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid"
        )
    
    # Get user details from database
    user = db.query(UserMaster).filter(
        UserMaster.id == session_data["user_id"],
        UserMaster.status == "active"
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Refresh session
    redis_client.refresh_session(session_id)
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role_id": user.role_id,
        "department_id": user.department_id,
        "designation_id": user.designation_id,
        "session_id": session_id
    }

def require_permission(module: str, access_type: str):
    """Dependency factory for permission checking"""
    async def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        # Get user's role and permissions
        role = db.query(RolesMaster).filter(RolesMaster.id == current_user["role_id"]).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not found"
            )
        
        # Check if user has required permission
        required_permission = db.query(PermissionMaster).filter(
            PermissionMaster.module == module,
            PermissionMaster.access_type == access_type
        ).first()
        
        if not required_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission not defined for {module}:{access_type}"
            )
        
        if role.permissions and required_permission.id not in role.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for {module}:{access_type}"
            )
        
        return current_user
    
    return permission_checker