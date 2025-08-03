"""
FastAPI application entry point
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import traceback
import uuid
from datetime import datetime

from .config import settings
from .dependencies.database import init_databases, close_databases, get_mongo_db
from .utils.logger import log_request, log_error
from .routers.front import health_router
from .routers.sso import auth_router

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME, version=settings.APP_VERSION, debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)

# Global variables for database connections
mongo_db = None


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    await init_databases()

    # Get MongoDB connection for logging
    global mongo_db
    try:
        mongo_db = await get_mongo_db()
    except Exception as e:
        print(f"⚠️ MongoDB not available for logging: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    await close_databases()


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log HTTP requests"""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    # Log request details
    try:
        if mongo_db is not None:
            await log_request(
                mongo_db,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", ""),
            )
    except Exception as e:
        print(f"Failed to log request: {e}")

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle global exceptions"""
    error_id = str(uuid.uuid4())
    error_details = {
        "error_id": error_id,
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
    }

    # Log error to MongoDB
    try:
        if mongo_db is not None:
            await log_error(
                mongo_db,
                error_id=error_id,
                url=str(request.url),
                method=request.method,
                error_details=error_details,
            )
    except Exception as e:
        print(f"Failed to log error: {e}")

    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "Internal server error",
            "data": None,
            "error": error_details,
        },
    )


# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "message": "Validation error",
            "data": None,
            "error": {"details": exc.errors(), "body": exc.body},
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
