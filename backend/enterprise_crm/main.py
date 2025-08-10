"""
Main FastAPI application for Enterprise CRM
"""
from fastapi import FastAPI, Request, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import traceback

from .config import settings
from .database import create_tables
from .routers import masters
# from .routers import dashboard, leads, opportunities
from .redis_client import redis_client
from .minio_client import minio_client

# Create FastAPI app
app = FastAPI(
    title="Enterprise CRM API",
    description="Comprehensive Enterprise Sales and Product Management Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": False,
            "message": exc.detail,
            "data": None,
            "error": {
                "code": exc.status_code,
                "detail": exc.detail
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "Internal server error",
            "data": None,
            "error": {
                "code": 500,
                "detail": str(exc),
                "traceback": traceback.format_exc() if settings.DATABASE_URL.startswith("sqlite") else None
            }
        }
    )

# Include routers
app.include_router(masters.router)
# app.include_router(dashboard.router)
# app.include_router(leads.router)
# app.include_router(opportunities.router)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        if redis_client.available:
            redis_client.redis.ping()
            redis_status = "connected"
        else:
            redis_status = "disabled (using mock)"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    try:
        # Check MinIO connection
        if minio_client.available:
            minio_client.client.bucket_exists(settings.MINIO_BUCKET)
            minio_status = "connected"
        else:
            minio_status = "disabled (using mock)"
    except Exception as e:
        minio_status = f"error: {str(e)}"
    
    return {
        "status": True,
        "message": "Enterprise CRM API is running",
        "data": {
            "version": "1.0.0",
            "services": {
                "redis": redis_status,
                "minio": minio_status
            }
        }
    }

# Session endpoints
@app.post("/api/auth/login")
async def login():
    """Login endpoint - placeholder for now"""
    # This would typically validate credentials and create session
    session_id = redis_client.create_session(
        user_id=1,
        user_data={
            "name": "Admin User",
            "email": "admin@example.com",
            "role_id": 1
        }
    )
    
    return {
        "status": True,
        "message": "Login successful",
        "data": {
            "session_id": session_id,
            "user": {
                "name": "Admin User",
                "email": "admin@example.com"
            }
        }
    }

@app.post("/api/auth/logout")
async def logout(request: Request):
    """Logout endpoint"""
    session_id = request.headers.get("x-session-id")
    if session_id:
        redis_client.delete_session(session_id)
    
    return {
        "status": True,
        "message": "Logout successful",
        "data": None
    }

# File upload endpoint
@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...), folder: str = "uploads"):
    """Upload file to MinIO"""
    try:
        file_path = minio_client.upload_file(file, folder)
        if file_path:
            return {
                "status": True,
                "message": "File uploaded successfully",
                "data": {
                    "file_path": file_path,
                    "original_filename": file.filename
                }
            }
        else:
            raise HTTPException(status_code=500, detail="File upload failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("Starting Enterprise CRM API...")
    
    # Create database tables
    create_tables()
    print("Database tables created")
    
    # Test services and show status
    print(f"Redis status: {'available' if redis_client.available else 'disabled'}")
    print(f"MinIO status: {'available' if minio_client.available else 'disabled'}")
    
    print("Enterprise CRM API startup complete")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)