"""
FastAPI main application with SQLAlchemy
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

# Import routers
from .routers.sso import auth, dashboard
from .routers.portal import companies, contacts, leads, opportunities, users
from .routers.portal import quotations
from .routers.front import health

# Import database
from .database.init_db import init_database
from .dependencies.database import init_mongodb, close_mongodb
from .middlewares.error_handler import ErrorHandlerMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        print("🚀 Starting CRM Application...")

        # Initialize databases
        init_database()
        init_mongodb()

        print("✅ CRM Application started successfully!")

    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        raise

    yield

    # Shutdown
    try:
        close_mongodb()
        print("📴 CRM Application shutdown completed")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="CRM Management System",
    description="Comprehensive CRM system with SQLAlchemy ORM",
    version="2.0.0",
    lifespan=lifespan,
)
app.add_middleware(ErrorHandlerMiddleware)
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "Internal server error",
            "data": None,
            "error": str(exc),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for err in exc.errors():
        loc = err["loc"]
        field = loc[-1]  # last part of the location (e.g., "company_id")
        message = err["msg"]
        errors[field] = message

    return JSONResponse(
        status_code=422,
        content={"status": False, "message": "Validation Failed", "error": errors},
    )


# Include routers
app.include_router(health.router)
app.include_router(auth.router)
# app.include_router(dashboard.router)
app.include_router(companies.router)
app.include_router(contacts.router)
app.include_router(leads.router)
app.include_router(opportunities.router)
app.include_router(quotations.router)
app.include_router(users.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": True,
        "message": "CRM Management System API",
        "version": "2.0.0",
        "data": {
            "endpoints": [
                "/api/health",
                "/api/login",
                "/api/dashboard",
                "/api/companies",
                "/api/contacts",
                "/api/leads",
                "/api/opportunities",
                "/api/users",
            ]
        },
    }
