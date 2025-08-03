"""
Database initialization script
"""
from sqlalchemy.orm import Session
from ..models import Base, Role, Department, User
from ..database.engine import engine
from ..utils.auth import hash_password
import uuid

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ All database tables created successfully")

def seed_initial_data():
    """Seed initial data"""
    from ..database.base import SessionLocal
    
    db = SessionLocal()
    try:
        # Create default roles
        roles_data = [
            {"name": "admin", "description": "System Administrator", "permissions": ["*"]},
            {"name": "sales_manager", "description": "Sales Manager", "permissions": ["leads:*", "opportunities:*", "contacts:*", "companies:*"]},
            {"name": "sales_executive", "description": "Sales Executive", "permissions": ["leads:read", "leads:write", "contacts:read", "contacts:write"]},
            {"name": "user", "description": "Regular User", "permissions": ["leads:read", "contacts:read"]}
        ]
        
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
        
        # Create default departments
        departments_data = [
            {"name": "IT", "description": "Information Technology"},
            {"name": "Sales", "description": "Sales Department"},
            {"name": "Marketing", "description": "Marketing Department"},
            {"name": "Finance", "description": "Finance Department"},
            {"name": "HR", "description": "Human Resources"}
        ]
        
        for dept_data in departments_data:
            existing_dept = db.query(Department).filter(Department.name == dept_data["name"]).first()
            if not existing_dept:
                department = Department(**dept_data)
                db.add(department)
        
        db.commit()
        
        # Create admin user
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        it_dept = db.query(Department).filter(Department.name == "IT").first()
        
        existing_admin = db.query(User).filter(User.email == "admin@crm.com").first()
        if not existing_admin:
            admin_user = User(
                name="Admin User",
                email="admin@crm.com",
                username="admin",
                password_hash=hash_password("admin123"),
                role_id=admin_role.id if admin_role else None,
                department_id=it_dept.id if it_dept else None
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created: admin@crm.com / admin123")
        else:
            print("✅ Admin user already exists")
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

def init_database():
    """Initialize database with tables and seed data"""
    create_tables()
    seed_initial_data()
    print("✅ Database initialization completed")