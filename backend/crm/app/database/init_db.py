"""
Database initialization script with sample data
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models import Base, User, Role, Department, Company, Contact, RoleType
from ..database.engine import engine
from ..utils.auth import hash_password  # Use the proper bcrypt hashing
from datetime import datetime


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def seed_initial_data():
    """Seed database with initial data"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Seeding initial data...")
        
        # Check if data already exists
        if db.query(Role).first():
            print("Data already exists, skipping seed...")
            return
        
        # Create roles
        admin_role = Role(name="admin", description="Administrator with full access", permissions=["all"])
        reviewer_role = Role(name="reviewer", description="Can review and approve lead conversions", permissions=["leads_review", "leads_approve"])
        sales_role = Role(name="sales", description="Sales team member", permissions=["leads_read", "leads_write", "opportunities_read", "opportunities_write"])
        
        db.add_all([admin_role, reviewer_role, sales_role])
        db.flush()  # To get IDs
        
        # Create departments
        sales_dept = Department(name="Sales", description="Sales Department")
        marketing_dept = Department(name="Marketing", description="Marketing Department")
        management_dept = Department(name="Management", description="Management Department")
        
        db.add_all([sales_dept, marketing_dept, management_dept])
        db.flush()
        
        # Create users
        admin_user = User(
            name="Admin User",
            username="admin",
            email="admin@company.com",
            password_hash=hash_password("admin123"),
            role_id=admin_role.id,
            department_id=management_dept.id
        )
        
        reviewer_user = User(
            name="Review Manager",
            username="reviewer",
            email="reviewer@company.com",
            password_hash=hash_password("reviewer123"),
            role_id=reviewer_role.id,
            department_id=management_dept.id
        )
        
        sales_user = User(
            name="Sales Rep",
            username="sales",
            email="sales@company.com",
            password_hash=hash_password("sales123"),
            role_id=sales_role.id,
            department_id=sales_dept.id
        )
        
        db.add_all([admin_user, reviewer_user, sales_user])
        db.flush()
        
        # Create sample companies
        company1 = Company(
            name="Tech Corp Ltd",
            gst_number="29ABCDE1234F1Z1",
            pan_number="ABCDE1234F",
            industry_category="Technology",
            address="123 Tech Street",
            city="Bangalore",
            state="Karnataka",
            country="India",
            postal_code="560001",
            website="www.techcorp.com",
            description="Leading technology company",
            created_by=admin_user.id
        )
        
        company2 = Company(
            name="Business Solutions Inc",
            gst_number="27FGHIJ5678K2L3",
            pan_number="FGHIJ5678K",
            industry_category="Consulting",
            address="456 Business Ave",
            city="Mumbai",
            state="Maharashtra",
            country="India",
            postal_code="400001",
            website="www.bizsolve.com",
            description="Business consulting services",
            created_by=admin_user.id
        )
        
        db.add_all([company1, company2])
        db.flush()
        
        # Create sample contacts
        contact1 = Contact(
            full_name="John Smith",
            designation="CTO",
            email="john.smith@techcorp.com",
            phone_number="+91-98765-43210",
            company_id=company1.id,
            role_type=RoleType.DECISION_MAKER,
            created_by=admin_user.id
        )
        
        contact2 = Contact(
            full_name="Jane Doe",
            designation="CEO",
            email="jane.doe@bizsolve.com",
            phone_number="+91-87654-32109",
            company_id=company2.id,
            role_type=RoleType.DECISION_MAKER,
            created_by=admin_user.id
        )
        
        db.add_all([contact1, contact2])
        
        db.commit()
        print("✅ Initial data seeded successfully")
        
        print("\n=== LOGIN CREDENTIALS ===")
        print("Admin: username=admin, password=admin123")
        print("Reviewer: username=reviewer, password=reviewer123")
        print("Sales: username=sales, password=sales123")
        print("==========================\n")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_database():
    """Initialize database with tables and data"""
    print("🔄 Initializing database...")
    create_tables()
    seed_initial_data()
    print("✅ Database initialization completed")


if __name__ == "__main__":
    init_database()