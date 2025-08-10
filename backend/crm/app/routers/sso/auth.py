"""
Authentication endpoints with Redis Session Management
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from ...schemas.auth import LoginRequest, StandardResponse, UserResponse
from ...services.auth_service import AuthService
from ...dependencies.auth import get_current_user, get_optional_user, get_auth_service
from ...dependencies.database import get_postgres_db, get_mongo_db
from ...utils.redis_client import redis_client
from ...utils.minio_client import minio_client
from ...models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api", tags=["authentication"])


@router.post("/login", response_model=StandardResponse)
async def login(
    login_request: LoginRequest,
    request: Request,
    db: Session = Depends(get_postgres_db),
    mongo_db = Depends(get_mongo_db),
):
    """Authenticate user and return JWT token"""
    auth_service = AuthService(db, mongo_db)
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
async def logout(current_user: dict = Depends(get_optional_user)):
    """Logout endpoint with Redis session cleanup"""
    try:
        if current_user and current_user.get("session_id"):
            redis_client.delete_session(current_user["session_id"])
        
        return StandardResponse(
            status=True, message="Logout successful", data=None, error=None
        )
    except Exception as e:
        return StandardResponse(
            status=False, message="Logout failed", data=None, error={"details": str(e)}
        )

# Session Management Endpoints
@router.post("/session/create", response_model=StandardResponse)
async def create_session(
    user_id: int,
    user_data: dict,
    db: Session = Depends(get_postgres_db)
):
    """Create a new session (for testing/admin use)"""
    try:
        session_id = redis_client.create_session(user_id, user_data)
        return StandardResponse(
            status=True,
            message="Session created successfully",
            data={"session_id": session_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/info", response_model=StandardResponse)
async def get_session_info(current_user: dict = Depends(get_current_user)):
    """Get current session information"""
    return StandardResponse(
        status=True,
        message="Session information retrieved",
        data=current_user
    )

@router.post("/session/refresh", response_model=StandardResponse)
async def refresh_session(current_user: dict = Depends(get_current_user)):
    """Refresh current session"""
    try:
        if redis_client.refresh_session(current_user["session_id"]):
            return StandardResponse(
                status=True,
                message="Session refreshed successfully",
                data={"session_id": current_user["session_id"]}
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to refresh session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File Upload Endpoints
@router.post("/files/upload", response_model=StandardResponse)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "uploads",
    current_user: dict = Depends(get_current_user)
):
    """Upload file to MinIO storage"""
    try:
        file_path = minio_client.upload_file(file, folder)
        if file_path:
            return StandardResponse(
                status=True,
                message="File uploaded successfully",
                data={
                    "file_path": file_path,
                    "original_filename": file.filename,
                    "uploaded_by": current_user["name"]
                }
            )
        else:
            raise HTTPException(status_code=500, detail="File upload failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@router.get("/files/{file_path:path}", response_model=StandardResponse)
async def get_file_url(
    file_path: str,
    expires_in_minutes: int = 60,
    current_user: dict = Depends(get_current_user)
):
    """Get presigned URL for file access"""
    try:
        file_url = minio_client.get_file_url(file_path, expires_in_minutes)
        if file_url:
            return StandardResponse(
                status=True,
                message="File URL generated successfully",
                data={
                    "file_url": file_url,
                    "expires_in_minutes": expires_in_minutes
                }
            )
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/files/{file_path:path}", response_model=StandardResponse)
async def delete_file(
    file_path: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete file from MinIO storage"""
    try:
        if minio_client.delete_file(file_path):
            return StandardResponse(
                status=True,
                message="File deleted successfully",
                data={"deleted_file": file_path}
            )
        else:
            raise HTTPException(status_code=404, detail="File not found or delete failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
