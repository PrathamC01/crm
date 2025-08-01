# CRM Authentication API

A modern, scalable FastAPI-based authentication system for CRM applications.

## 🏗️ Architecture

This application follows a clean, modular architecture pattern:

```
crm/
├── app/                        # Core application code
│   ├── dependencies/           # Dependency injection modules
│   ├── helpers/                # Helper utilities
│   ├── locales/                # Internationalization files
│   ├── models/                 # Database models
│   ├── routers/                # API route handlers
│   │   ├── front/              # Frontend-related routes
│   │   ├── portal/             # Portal routes
│   │   └── sso/                # Authentication routes
│   ├── schemas/                # Pydantic schemas
│   ├── services/               # Business logic services
│   ├── tests/                  # Test files
│   ├── utils/                  # Utility functions
│   ├── config.py               # Configuration settings
│   └── main.py                 # FastAPI application entry point
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
└── alembic.ini                 # Database migration configuration
```

## 🚀 Features

- **JWT Authentication** with configurable expiration
- **Dual Login Support** - Email or Username
- **PostgreSQL** for user data storage
- **MongoDB** for comprehensive activity logging
- **Modular Architecture** with clean separation of concerns
- **Dependency Injection** for better testability
- **Comprehensive Error Handling** with structured responses
- **Request/Response Logging** for monitoring and debugging
- **CORS Support** for cross-origin requests

## 🔧 Installation

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables:**
   Copy `.env.example` to `.env` and configure:
   ```env
   POSTGRES_URL=postgresql://postgres:password@localhost:5432/crm_db
   MONGO_URL=mongodb://localhost:27017/crm_logs
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=1
   ```

3. **Run the Application:**
   ```bash
   python index.py
   ```

## 📊 API Endpoints

### Health Check
- `GET /` - Root health check
- `GET /api/` - API health check
- `GET /health` - Detailed health information

### Authentication
- `POST /api/login` - User authentication
- `GET /api/dashboard` - Protected user information
- `POST /api/logout` - User logout

## 🔐 Authentication Flow

1. **Login:** POST to `/api/login` with email/username and password
2. **Token:** Receive JWT token in response
3. **Protected Access:** Include `Authorization: Bearer <token>` header
4. **Dashboard:** Access user information via `/api/dashboard`

## 🧪 Testing

Test credentials for development:
- **Email:** admin@crm.com
- **Username:** admin  
- **Password:** admin123

## 📝 Response Format

All API endpoints return a consistent response format:
```json
{
  "status": true,
  "message": "Success message",
  "data": { ... },
  "error": null
}
```

## 🛠️ Development

### Project Structure Benefits

- **Scalability:** Easy to add new features and modules
- **Maintainability:** Clear separation of concerns
- **Testability:** Isolated components for unit testing
- **Reusability:** Shared utilities and services
- **Documentation:** Self-documenting code structure

### Key Components

- **Models:** Database interaction layer
- **Schemas:** Data validation and serialization
- **Services:** Business logic implementation
- **Routers:** API endpoint definitions
- **Dependencies:** Dependency injection for clean architecture
- **Utils:** Shared utility functions

## 🔒 Security Features

- Password hashing with bcrypt
- JWT tokens with expiration
- Request rate limiting ready
- SQL injection prevention
- CORS configuration
- Comprehensive audit logging

## 📈 Monitoring & Logging

- **Activity Logs:** User actions tracked in MongoDB
- **Request Logs:** HTTP request/response logging
- **Error Logs:** Comprehensive error tracking
- **Performance Metrics:** Response time monitoring

## 🚀 Deployment

The application is containerized and ready for deployment with:
- Docker support
- Environment-based configuration
- Database migrations with Alembic
- Health checks for monitoring
- Structured logging for production

## 🤝 Contributing

1. Follow the established project structure
2. Add appropriate tests for new features
3. Update documentation as needed
4. Ensure all endpoints follow the standard response format