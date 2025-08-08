"""
Configuration settings for CRM application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    # Database settings
    POSTGRES_URL: str = os.getenv(
        "POSTGRES_URL", "postgresql://crm:Test@localhost:5432/crm_db"
    )
    print(POSTGRES_URL)
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/crm_logs")
    print(MONGO_URL)
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", 1))

    # Application settings
    APP_NAME: str = "CRM Authentication API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://45ef8d04-cd5e-471a-9a5d-2989f488e28b.preview.emergentagent.com",
        "http://30ac7fac-5c43-4846-ac99-edfa626ede7e.preview.emergentagent.com",
    ]


settings = Settings()
