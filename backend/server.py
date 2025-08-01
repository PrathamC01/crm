from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Union, Dict, Any
import asyncpg
import asyncio
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
import uuid
import traceback
import time

# Load environment variables
load_dotenv()

app = FastAPI(title="CRM Authentication API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration
POSTGRES_URL = os.getenv("POSTGRES_URL")
MONGO_URL = os.getenv("MONGO_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 1))

# Database connections
postgres_pool = None
mongo_client = None
mongo_db = None

# Pydantic models
class LoginRequest(BaseModel):
    email_or_username: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    username: str
    role: str
    department: str
    is_active: bool

class StandardResponse(BaseModel):
    status: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def log_activity(user_id: str, action: str, details: dict = None, request: Request = None):
    """Log user activity to MongoDB"""
    try:
        if mongo_db is not None:
            log_entry = {
                "user_id": user_id,
                "action": action,
                "details": details or {},
                "timestamp": datetime.utcnow(),
                "ip_address": request.client.host if request else None,
                "user_agent": request.headers.get("user-agent") if request else None
            }
            mongo_db.activity_logs.insert_one(log_entry)
    except Exception as e:
        print(f"Failed to log activity: {e}")

# Database initialization
async def init_db():
    global postgres_pool, mongo_client, mongo_db
    
    # PostgreSQL connection
    try:
        postgres_pool = await asyncpg.create_pool(POSTGRES_URL)
        print("✅ PostgreSQL connected successfully")
        
        # Create tables
        async with postgres_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(100) NOT NULL DEFAULT 'user',
                    department VARCHAR(100),
                    is_active BOOLEAN DEFAULT true,
                    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_on TIMESTAMP NULL,
                    created_by UUID,
                    updated_by UUID,
                    deleted_by UUID
                )
            """)
            
            # Create a default admin user for testing
            admin_password = hash_password("admin123")
            await conn.execute("""
                INSERT INTO users (name, email, username, password_hash, role, department)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (email) DO NOTHING
            """, "Admin User", "admin@crm.com", "admin", admin_password, "admin", "IT")
            
            print("✅ Database tables created and admin user seeded")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
    
    # MongoDB connection
    try:
        mongo_client = MongoClient(MONGO_URL)
        mongo_db = mongo_client.crm_logs
        # Test connection
        mongo_client.admin.command('ping')
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        async with postgres_pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1 AND is_active = true AND deleted_on IS NULL",
                uuid.UUID(user_id)
            )
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
        
        return dict(user)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Log request details
    try:
        if mongo_db is not None:            
            log_entry = {
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": process_time,
                "timestamp": datetime.utcnow(),
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent", "")
            }
            mongo_db.request_logs.insert_one(log_entry)
    except Exception as e:
        print(f"Failed to log request: {e}")
    
    return response

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = str(uuid.uuid4())
    error_details = {
        "error_id": error_id,
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc()
    }
    
    # Log error to MongoDB
    try:
        if mongo_db is not None:
            mongo_db.error_logs.insert_one({
                "error_id": error_id,
                "url": str(request.url),
                "method": request.method,
                "error_details": error_details,
                "timestamp": datetime.utcnow()
            })
    except Exception as e:
        print(f"Failed to log error: {e}")
    
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "message": "Internal server error",
            "data": None,
            "error": error_details
        }
    )

# Routes
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"status": True, "message": "CRM Authentication API is running", "data": None, "error": None}

@app.post("/api/login")
async def login(login_request: LoginRequest, request: Request):
    try:
        async with postgres_pool.acquire() as conn:
            # Check if login is email or username
            if "@" in login_request.email_or_username:
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE email = $1 AND is_active = true AND deleted_on IS NULL",
                    login_request.email_or_username
                )
            else:
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE username = $1 AND is_active = true AND deleted_on IS NULL",
                    login_request.email_or_username
                )
            
            if not user:
                await log_activity("unknown", "failed_login", {"email_or_username": login_request.email_or_username}, request)
                return JSONResponse(
                    status_code=401,
                    content={
                        "status": False,
                        "message": "Invalid credentials",
                        "data": None,
                        "error": {"details": "User not found"}
                    }
                )
            
            if not verify_password(login_request.password, user["password_hash"]):
                await log_activity(str(user["id"]), "failed_login", {"reason": "invalid_password"}, request)
                return JSONResponse(
                    status_code=401,
                    content={
                        "status": False,
                        "message": "Invalid credentials",
                        "data": None,
                        "error": {"details": "Invalid password"}
                    }
                )
            
            # Create JWT token
            token_data = {"sub": str(user["id"]), "username": user["username"], "email": user["email"]}
            access_token = create_access_token(token_data)
            
            # Log successful login
            await log_activity(str(user["id"]), "successful_login", {}, request)
            
            return {
                "status": True,
                "message": "Login successful",
                "data": {"token": access_token},
                "error": None
            }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": False,
                "message": "Login failed",
                "data": None,
                "error": {"details": str(e)}
            }
        )

@app.get("/api/dashboard")
async def dashboard(current_user: dict = Depends(get_current_user), request: Request = None):
    try:
        user_data = UserResponse(
            id=str(current_user["id"]),
            name=current_user["name"],
            email=current_user["email"],
            username=current_user["username"],
            role=current_user["role"],
            department=current_user["department"] or "N/A",
            is_active=current_user["is_active"]
        )
        
        # Log dashboard access
        await log_activity(str(current_user["id"]), "dashboard_access", {}, request)
        
        return {
            "status": True,
            "message": "Dashboard data retrieved successfully",
            "data": user_data.dict(),
            "error": None
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": False,
                "message": "Failed to retrieve dashboard data",
                "data": None,
                "error": {"details": str(e)}
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)