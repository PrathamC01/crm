"""
User management service using SQLAlchemy ORM
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from ..models import User, Role, Department
from ..utils.auth import hash_password
from ..schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate, created_by: Optional[int] = None) -> User:
        """Create a new user"""
        password_hash = hash_password(user_data.password)
        
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            username=user_data.username,
            password_hash=password_hash,
            role_id=user_data.role_id,
            department_id=user_data.department_id,
            created_by=created_by
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with role and department"""
        return self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.department)
        ).filter(
            and_(
                User.id == user_id,
                User.is_active == True,
                User.deleted_on.is_(None)
            )
        ).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email with role and department"""
        return self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.department)
        ).filter(
            and_(
                User.email == email,
                User.is_active == True,
                User.deleted_on.is_(None)
            )
        ).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username with role and department"""
        return self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.department)
        ).filter(
            and_(
                User.username == username,
                User.is_active == True,
                User.deleted_on.is_(None)
            )
        ).first()
    
    def update_user(self, user_id: int, user_data: UserUpdate, updated_by: Optional[int] = None) -> Optional[User]:
        """Update user information"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        if updated_by:
            db_user.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete_user(self, user_id: int, deleted_by: Optional[int] = None) -> bool:
        """Soft delete user"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        db_user.is_active = False
        db_user.deleted_on = datetime.utcnow()
        if deleted_by:
            db_user.deleted_by = deleted_by
        
        self.db.commit()
        return True
    
    def get_users(self, skip: int = 0, limit: int = 100, search: str = None) -> List[User]:
        """Get all users with pagination and search"""
        query = self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.department)
        ).filter(
            and_(
                User.is_active == True,
                User.deleted_on.is_(None)
            )
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.username.ilike(search_term)
                )
            )
        
        return query.order_by(User.name).offset(skip).limit(limit).all()
    
    def get_user_count(self, search: str = None) -> int:
        """Get total count of users"""
        query = self.db.query(User).filter(
            and_(
                User.is_active == True,
                User.deleted_on.is_(None)
            )
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.username.ilike(search_term)
                )
            )
        
        return query.count()
    
    def get_sales_people(self) -> List[User]:
        """Get all users with sales roles"""
        return self.db.query(User).join(Role).filter(
            and_(
                User.is_active == True,
                User.deleted_on.is_(None),
                Role.name.in_(['sales_manager', 'sales_executive'])
            )
        ).order_by(User.name).all()
    
    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        db_user = self.get_user_by_id(user_id)
        if db_user:
            db_user.last_login = datetime.utcnow()
            db_user.failed_login_attempts = 0
            self.db.commit()
    
    def increment_failed_login(self, user_id: str):
        """Increment failed login attempts"""
        db_user = self.get_user_by_id(user_id)
        if db_user:
            db_user.failed_login_attempts += 1
            self.db.commit()