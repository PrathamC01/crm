"""
Product Type Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...dependencies.database import get_db
from ...dependencies.auth import get_current_user
from ...models.product_type import ProductType
from ...models.user import User
from ...schemas.product_type import (
    ProductTypeCreate, 
    ProductTypeUpdate, 
    ProductTypeResponse,
    ProductTypeListResponse,
    ProductTypeDetailResponse
)
from ...utils.product_utils import generate_abbreviation

router = APIRouter(prefix="/api/masters/product-types", tags=["Product Types"])


@router.post("", response_model=ProductTypeDetailResponse)
async def create_product_type(
    product_type_data: ProductTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product type"""
    try:
        # Check if name already exists
        existing = db.query(ProductType).filter(ProductType.name == product_type_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Product type with this name already exists")
        
        # Generate abbreviation if not provided
        if not product_type_data.abbreviation:
            existing_abbrevs = db.query(ProductType.abbreviation).all()
            existing_abbrevs = [abbrev[0] for abbrev in existing_abbrevs if abbrev[0]]
            product_type_data.abbreviation = generate_abbreviation(product_type_data.name, existing_abbrevs)
        
        # Check if abbreviation already exists
        existing_abbrev = db.query(ProductType).filter(ProductType.abbreviation == product_type_data.abbreviation).first()
        if existing_abbrev:
            raise HTTPException(status_code=400, detail="Product type with this abbreviation already exists")
        
        # Create product type
        db_product_type = ProductType(
            name=product_type_data.name,
            abbreviation=product_type_data.abbreviation,
            description=product_type_data.description,
            created_by=current_user.id
        )
        
        db.add(db_product_type)
        db.commit()
        db.refresh(db_product_type)
        
        return ProductTypeDetailResponse(
            data=ProductTypeResponse.from_orm(db_product_type),
            message="Product type created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create product type: {str(e)}")


@router.get("", response_model=ProductTypeListResponse)
async def list_product_types(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of product types with pagination and filtering"""
    try:
        # Build query
        query = db.query(ProductType)
        
        # Apply filters
        if search:
            query = query.filter(ProductType.name.ilike(f"%{search}%"))
        
        if is_active is not None:
            query = query.filter(ProductType.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        product_types = query.offset(offset).limit(limit).all()
        
        return ProductTypeListResponse(
            data=[ProductTypeResponse.from_orm(pt) for pt in product_types],
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product types: {str(e)}")


@router.get("/{product_type_id}", response_model=ProductTypeDetailResponse)
async def get_product_type(
    product_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get product type by ID"""
    try:
        product_type = db.query(ProductType).filter(ProductType.id == product_type_id).first()
        if not product_type:
            raise HTTPException(status_code=404, detail="Product type not found")
        
        return ProductTypeDetailResponse(
            data=ProductTypeResponse.from_orm(product_type)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product type: {str(e)}")


@router.put("/{product_type_id}", response_model=ProductTypeDetailResponse)
async def update_product_type(
    product_type_id: int,
    product_type_data: ProductTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update product type"""
    try:
        product_type = db.query(ProductType).filter(ProductType.id == product_type_id).first()
        if not product_type:
            raise HTTPException(status_code=404, detail="Product type not found")
        
        # Check for name uniqueness if name is being updated
        if product_type_data.name and product_type_data.name != product_type.name:
            existing = db.query(ProductType).filter(
                ProductType.name == product_type_data.name,
                ProductType.id != product_type_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Product type with this name already exists")
        
        # Check for abbreviation uniqueness if abbreviation is being updated
        if product_type_data.abbreviation and product_type_data.abbreviation != product_type.abbreviation:
            existing = db.query(ProductType).filter(
                ProductType.abbreviation == product_type_data.abbreviation,
                ProductType.id != product_type_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Product type with this abbreviation already exists")
        
        # Update fields
        for field, value in product_type_data.dict(exclude_unset=True).items():
            setattr(product_type, field, value)
        
        product_type.updated_by = current_user.id
        
        db.commit()
        db.refresh(product_type)
        
        return ProductTypeDetailResponse(
            data=ProductTypeResponse.from_orm(product_type),
            message="Product type updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update product type: {str(e)}")


@router.delete("/{product_type_id}")
async def delete_product_type(
    product_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete product type"""
    try:
        product_type = db.query(ProductType).filter(ProductType.id == product_type_id).first()
        if not product_type:
            raise HTTPException(status_code=404, detail="Product type not found")
        
        # Soft delete
        product_type.is_active = False
        product_type.deleted_by = current_user.id
        from datetime import datetime
        product_type.deleted_on = datetime.utcnow()
        
        db.commit()
        
        return {"status": True, "message": "Product type deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete product type: {str(e)}")