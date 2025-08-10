"""
Authentication endpoints with Redis Session Management
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from ...schemas.auth import LoginRequest, StandardResponse, UserResponse
from ...services.auth_service import AuthService
from ...dependencies.auth import get_current_user, get_optional_user, get_auth_service
from ...dependencies.database import get_postgres_db
from ...utils.redis_client import redis_client
from ...utils.minio_client import minio_client
from ...models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/login", response_model=StandardResponse)
async def login(
    login_request: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticate user and return JWT token"""
    try:
        token_data = await auth_service.authenticate_user(
            login_request.email_or_username, login_request.password, request
        )

        return StandardResponse(
            status=True, message="Login successful", data=token_data, error=None
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": False,
                "message": "Invalid credentials",
                "data": None,
                "error": {"details": e.detail},
            },
        )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={
                "status": False,
                "message": "Login failed",
                "data": None,
                "error": {"details": str(e)},
            },
        )


@router.get("/dashboard", response_model=StandardResponse)
async def dashboard(
    request: Request,
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Get user dashboard information"""
    try:
        user_data = await auth_service.get_user_info(str(current_user["id"]), request)

        return StandardResponse(
            status=True,
            message="Dashboard data retrieved successfully",
            data=user_data.dict(),
            error=None,
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": False,
                "message": "Failed to retrieve dashboard data",
                "data": None,
                "error": {"details": e.detail},
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": False,
                "message": "Failed to retrieve dashboard data",
                "data": None,
                "error": {"details": str(e)},
            },
        )


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token removal)"""
    return StandardResponse(
        status=True, message="Logout successful", data=None, error=None
    )
