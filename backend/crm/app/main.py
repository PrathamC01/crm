"""
FastAPI main application with SQLAlchemy and centralized error handling
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

# Import routers
from .routers.sso import auth
from .routers.portal import companies, contacts, leads, opportunities, users, masters, dashboard
from .routers.portal import quotations
from .routers.front import health

# Import database
from .database.init_db import init_database
from .dependencies.database import init_mongodb, close_mongodb

# Import Redis and MinIO clients
from .utils.redis_client import redis_client
from .utils.minio_client import minio_client

# Import centralized error handlers
from .exceptions.handlers import (
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    pydantic_validation_exception_handler,
    sqlalchemy_exception_handler,
    database_exception_handler,
    generic_exception_handler
)
from .exceptions.custom_exceptions import CRMBaseException

# SQLAlchemy imports for error handling
from sqlalchemy.exc import IntegrityError, DBAPIError
from pydantic import ValidationError as PydanticValidationError


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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register centralized exception handlers
app.add_exception_handler(CRMBaseException, custom_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PydanticValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(IntegrityError, sqlalchemy_exception_handler)
app.add_exception_handler(DBAPIError, database_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(companies.router)
app.include_router(contacts.router)
app.include_router(leads.router)
app.include_router(opportunities.router)
app.include_router(quotations.router)
app.include_router(users.router)
app.include_router(masters.router)


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
                "/api/quotations",
                "/api/users",
                "/api/masters",
            ]
        },
    }
