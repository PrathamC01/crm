"""
Seed data for CRM Master Data
"""
from sqlalchemy.orm import Session
from .app.database.base import SessionLocal
from .app.models.masters import (
    DepartmentMaster, RolesMaster, DesignationMaster, 
    PermissionMaster, UserMaster, UOMMaster, 
    StateMaster, CityMaster, IndustryCategoryMaster,
    AccessTypeEnum
)

def seed_master_data():
    """Seed basic master data"""
    db = SessionLocal()
    
    try:
        print("Starting to seed master data...")
        
        # Seed Departments
        if not db.query(DepartmentMaster).first():
            departments = [
                {"department_name": "Sales", "description": "Sales Department"},
                {"department_name": "Marketing", "description": "Marketing Department"},
                {"department_name": "Operations", "description": "Operations Department"},
                {"department_name": "Finance", "description": "Finance Department"},
                {"department_name": "HR", "description": "Human Resources Department"},
                {"department_name": "IT", "description": "Information Technology Department"}
            ]
            
            for dept_data in departments:
                dept = DepartmentMaster(**dept_data)
                db.add(dept)
            
            print("Seeded departments")
        
        # Seed Designations
        if not db.query(DesignationMaster).first():
            designations = [
                {"designation_name": "Manager", "description": "Department Manager"},
                {"designation_name": "Assistant Manager", "description": "Assistant Manager"},
                {"designation_name": "Team Lead", "description": "Team Leader"},
                {"designation_name": "Senior Executive", "description": "Senior Executive"},
                {"designation_name": "Executive", "description": "Executive"},
                {"designation_name": "Associate", "description": "Associate"}
            ]
            
            for desig_data in designations:
                desig = DesignationMaster(**desig_data)
                db.add(desig)
            
            print("Seeded designations")
        
        # Seed Permissions
        if not db.query(PermissionMaster).first():
            modules = ["masters", "leads", "opportunities", "dashboard", "reports"]
            access_types = [AccessTypeEnum.READ, AccessTypeEnum.WRITE, AccessTypeEnum.APPROVE]
            
            for module in modules:
                for access_type in access_types:
                    permission = PermissionMaster(
                        permission_name=f"{module}_{access_type.value}",
                        module=module,
                        access_type=access_type,
                        description=f"{access_type.value.title()} access for {module}"
                    )
                    db.add(permission)
            
            print("Seeded permissions")
        
        # Commit after adding permissions to get IDs
        db.commit()
        
        # Seed Roles
        if not db.query(RolesMaster).first():
            # Get all permission IDs
            permissions = db.query(PermissionMaster).all()
            all_permission_ids = [p.id for p in permissions]
            
            # Admin role with all permissions
            admin_role = RolesMaster(
                role_name="Admin",
                description="Full system access",
                permissions=all_permission_ids
            )
            db.add(admin_role)
            
            # Manager role with read/write permissions
            manager_permissions = [p.id for p in permissions if p.access_type in [AccessTypeEnum.READ, AccessTypeEnum.WRITE]]
            manager_role = RolesMaster(
                role_name="Manager", 
                description="Manager access",
                permissions=manager_permissions
            )
            db.add(manager_role)
            
            # User role with read permissions only
            user_permissions = [p.id for p in permissions if p.access_type == AccessTypeEnum.READ]
            user_role = RolesMaster(
                role_name="User",
                description="Read-only access",
                permissions=user_permissions
            )
            db.add(user_role)
            
            print("Seeded roles")
        
        # Seed UOMs
        if not db.query(UOMMaster).first():
            uoms = [
                {"uom_name": "Pieces", "uom_code": "PCS", "description": "Individual pieces"},
                {"uom_name": "Kilograms", "uom_code": "KG", "description": "Weight in kilograms"},
                {"uom_name": "Meters", "uom_code": "M", "description": "Length in meters"},
                {"uom_name": "Liters", "uom_code": "L", "description": "Volume in liters"},
                {"uom_name": "Hours", "uom_code": "HR", "description": "Time in hours"},
                {"uom_name": "Days", "uom_code": "DAY", "description": "Time in days"}
            ]
            
            for uom_data in uoms:
                uom = UOMMaster(**uom_data)
                db.add(uom)
            
            print("Seeded UOMs")
        
        # Seed States (India)
        if not db.query(StateMaster).first():
            states = [
                {"state_name": "Maharashtra", "state_code": "MH"},
                {"state_name": "Karnataka", "state_code": "KA"},
                {"state_name": "Tamil Nadu", "state_code": "TN"},
                {"state_name": "Delhi", "state_code": "DL"},
                {"state_name": "Gujarat", "state_code": "GJ"},
                {"state_name": "Rajasthan", "state_code": "RJ"},
                {"state_name": "Uttar Pradesh", "state_code": "UP"},
                {"state_name": "West Bengal", "state_code": "WB"}
            ]
            
            for state_data in states:
                state = StateMaster(**state_data)
                db.add(state)
            
            print("Seeded states")
        
        # Commit to get state IDs
        db.commit()
        
        # Seed Cities
        if not db.query(CityMaster).first():
            # Get state IDs
            states = {s.state_name: s.id for s in db.query(StateMaster).all()}
            
            cities = [
                {"city_name": "Mumbai", "state_id": states.get("Maharashtra")},
                {"city_name": "Pune", "state_id": states.get("Maharashtra")},
                {"city_name": "Bangalore", "state_id": states.get("Karnataka")},
                {"city_name": "Chennai", "state_id": states.get("Tamil Nadu")},
                {"city_name": "New Delhi", "state_id": states.get("Delhi")},
                {"city_name": "Ahmedabad", "state_id": states.get("Gujarat")},
                {"city_name": "Jaipur", "state_id": states.get("Rajasthan")},
                {"city_name": "Kolkata", "state_id": states.get("West Bengal")}
            ]
            
            for city_data in cities:
                if city_data["state_id"]:
                    city = CityMaster(**city_data)
                    db.add(city)
            
            print("Seeded cities")
        
        # Seed Industry Categories
        if not db.query(IndustryCategoryMaster).first():
            industries = [
                {"industry_name": "Information Technology", "description": "IT and Software services"},
                {"industry_name": "Manufacturing", "description": "Manufacturing and Production"},
                {"industry_name": "Healthcare", "description": "Healthcare and Medical services"},
                {"industry_name": "Education", "description": "Education and Training"},
                {"industry_name": "Finance", "description": "Banking and Financial services"},
                {"industry_name": "Retail", "description": "Retail and E-commerce"},
                {"industry_name": "Real Estate", "description": "Real Estate and Construction"}
            ]
            
            for industry_data in industries:
                industry = IndustryCategoryMaster(**industry_data)
                db.add(industry)
            
            print("Seeded industries")
        
        # Final commit
        db.commit()
        print("✅ Master data seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding master data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_data()