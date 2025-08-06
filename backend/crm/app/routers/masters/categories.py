"""
Category Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...dependencies.database import get_db
from ...dependencies.auth import get_current_user
from ...models.category import Category
from ...models.user import User
from ...schemas.category import (
    CategoryCreate, 
    CategoryUpdate, 
    CategoryResponse,
    CategoryListResponse,
    CategoryDetailResponse
)
from ...utils.product_utils import generate_abbreviation

router = APIRouter(prefix="/api/masters/categories", tags=["Categories"])


@router.post("", response_model=CategoryDetailResponse)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new category"""
    try:
        # Check if name already exists
        existing = db.query(Category).filter(Category.name == category_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        
        # Generate abbreviation if not provided
        if not category_data.abbreviation:
            existing_abbrevs = db.query(Category.abbreviation).all()
            existing_abbrevs = [abbrev[0] for abbrev in existing_abbrevs if abbrev[0]]
            category_data.abbreviation = generate_abbreviation(category_data.name, existing_abbrevs)
        
        # Check if abbreviation already exists
        existing_abbrev = db.query(Category).filter(Category.abbreviation == category_data.abbreviation).first()
        if existing_abbrev:
            raise HTTPException(status_code=400, detail="Category with this abbreviation already exists")
        
        # Create category
        db_category = Category(
            name=category_data.name,
            abbreviation=category_data.abbreviation,
            description=category_data.description,
            created_by=current_user.id
        )
        
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        
        return CategoryDetailResponse(
            data=CategoryResponse.from_orm(db_category),
            message="Category created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create category: {str(e)}")


@router.get("", response_model=CategoryListResponse)
async def list_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of categories with pagination and filtering"""
    try:
        # Build query
        query = db.query(Category)
        
        # Apply filters
        if search:
            query = query.filter(Category.name.ilike(f"%{search}%"))
        
        if is_active is not None:
            query = query.filter(Category.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        categories = query.offset(offset).limit(limit).all()
        
        return CategoryListResponse(
            data=[CategoryResponse.from_orm(cat) for cat in categories],
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve categories: {str(e)}")


@router.get("/{category_id}", response_model=CategoryDetailResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get category by ID"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return CategoryDetailResponse(
            data=CategoryResponse.from_orm(category)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve category: {str(e)}")


@router.put("/{category_id}", response_model=CategoryDetailResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update category"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check for name uniqueness if name is being updated
        if category_data.name and category_data.name != category.name:
            existing = db.query(Category).filter(
                Category.name == category_data.name,
                Category.id != category_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Category with this name already exists")
        
        # Check for abbreviation uniqueness if abbreviation is being updated
        if category_data.abbreviation and category_data.abbreviation != category.abbreviation:
            existing = db.query(Category).filter(
                Category.abbreviation == category_data.abbreviation,
                Category.id != category_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Category with this abbreviation already exists")
        
        # Update fields
        for field, value in category_data.dict(exclude_unset=True).items():
            setattr(category, field, value)
        
        category.updated_by = current_user.id
        
        db.commit()
        db.refresh(category)
        
        return CategoryDetailResponse(
            data=CategoryResponse.from_orm(category),
            message="Category updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update category: {str(e)}")


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete category"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Soft delete
        category.is_active = False
        category.deleted_by = current_user.id
        from datetime import datetime
        category.deleted_on = datetime.utcnow()
        
        db.commit()
        
        return {"status": True, "message": "Category deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete category: {str(e)}")