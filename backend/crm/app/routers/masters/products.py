"""
Product Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...dependencies.database import get_db
from ...dependencies.auth import get_current_user
from ...models.product import Product
from ...models.product_type import ProductType
from ...models.category import Category
from ...models.sub_category import SubCategory
from ...models.oem_vendor import OEMVendor
from ...models.configuration import Configuration
from ...models.user import User
from ...schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    ProductResponse,
    ProductListResponse,
    ProductDetailResponse,
    InlineCategoryCreate
)
from ...utils.product_utils import generate_sku_code, generate_abbreviation

router = APIRouter(prefix="/api/masters/products", tags=["Products"])


@router.post("/inline-category/{category_type}")
async def create_inline_category(
    category_type: str,  # product-type, category, sub-category, oem-vendor, configuration
    category_data: InlineCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create category inline during product creation"""
    try:
        if category_type == "product-type":
            model_class = ProductType
        elif category_type == "category":
            model_class = Category
        elif category_type == "sub-category":
            model_class = SubCategory
        elif category_type == "oem-vendor":
            model_class = OEMVendor
        elif category_type == "configuration":
            model_class = Configuration
        else:
            raise HTTPException(status_code=400, detail="Invalid category type")
        
        # Check if name already exists
        existing = db.query(model_class).filter(model_class.name == category_data.name).first()
        if existing:
            return {
                "status": True,
                "message": f"{category_type.replace('-', ' ').title()} already exists",
                "data": {"id": existing.id, "name": existing.name, "abbreviation": existing.abbreviation}
            }
        
        # Generate abbreviation
        existing_abbrevs = db.query(model_class.abbreviation).all()
        existing_abbrevs = [abbrev[0] for abbrev in existing_abbrevs if abbrev[0]]
        abbreviation = generate_abbreviation(category_data.name, existing_abbrevs)
        
        # Create new category
        new_category = model_class(
            name=category_data.name,
            abbreviation=abbreviation,
            description=category_data.description,
            created_by=current_user.id
        )
        
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        
        return {
            "status": True,
            "message": f"{category_type.replace('-', ' ').title()} created successfully",
            "data": {"id": new_category.id, "name": new_category.name, "abbreviation": new_category.abbreviation}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create {category_type}: {str(e)}")


@router.post("", response_model=ProductDetailResponse)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new product"""
    try:
        # Validate foreign keys exist
        product_type = db.query(ProductType).filter(ProductType.id == product_data.product_type_id).first()
        if not product_type:
            raise HTTPException(status_code=400, detail="Product type not found")
        
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
        
        sub_category = None
        if product_data.sub_category_id:
            sub_category = db.query(SubCategory).filter(SubCategory.id == product_data.sub_category_id).first()
            if not sub_category:
                raise HTTPException(status_code=400, detail="Sub category not found")
        
        oem_vendor = None
        if product_data.oem_vendor_id:
            oem_vendor = db.query(OEMVendor).filter(OEMVendor.id == product_data.oem_vendor_id).first()
            if not oem_vendor:
                raise HTTPException(status_code=400, detail="OEM/Vendor not found")
        
        configuration = None
        if product_data.configuration_id:
            configuration = db.query(Configuration).filter(Configuration.id == product_data.configuration_id).first()
            if not configuration:
                raise HTTPException(status_code=400, detail="Configuration not found")
        
        # Generate SKU code
        existing_skus = db.query(Product.sku_code).all()
        existing_skus = [sku[0] for sku in existing_skus]
        
        sku_code = generate_sku_code(
            product_type_abbrev=product_type.abbreviation,
            category_abbrev=category.abbreviation,
            sub_category_abbrev=sub_category.abbreviation if sub_category else None,
            oem_abbrev=oem_vendor.abbreviation if oem_vendor else None,
            config_abbrev=configuration.abbreviation if configuration else None,
            existing_skus=existing_skus
        )
        
        # Create product
        db_product = Product(
            name=product_data.name,
            sku_code=sku_code,
            description=product_data.description,
            product_type_id=product_data.product_type_id,
            category_id=product_data.category_id,
            sub_category_id=product_data.sub_category_id,
            oem_vendor_id=product_data.oem_vendor_id,
            configuration_id=product_data.configuration_id,
            product_config=product_data.product_config,
            specifications=product_data.specifications,
            warranty_period=product_data.warranty_period,
            unit_of_measure=product_data.unit_of_measure,
            created_by=current_user.id
        )
        
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        
        return ProductDetailResponse(
            data=ProductResponse.from_orm(db_product),
            message="Product created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")


@router.get("", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    product_type_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of products with pagination and filtering"""
    try:
        # Build query with joins for related data
        query = db.query(Product).join(ProductType).join(Category)
        
        # Apply filters
        if search:
            query = query.filter(
                Product.name.ilike(f"%{search}%") |
                Product.sku_code.ilike(f"%{search}%") |
                Product.description.ilike(f"%{search}%")
            )
        
        if product_type_id:
            query = query.filter(Product.product_type_id == product_type_id)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        products = query.offset(offset).limit(limit).all()
        
        return ProductListResponse(
            data=[ProductResponse.from_orm(product) for product in products],
            total=total,
            page=page,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve products: {str(e)}")


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get product by ID"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return ProductDetailResponse(
            data=ProductResponse.from_orm(product)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product: {str(e)}")


@router.get("/sku/{sku_code}", response_model=ProductDetailResponse)
async def get_product_by_sku(
    sku_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get product by SKU code"""
    try:
        product = db.query(Product).filter(Product.sku_code == sku_code).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return ProductDetailResponse(
            data=ProductResponse.from_orm(product)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product: {str(e)}")


@router.put("/{product_id}", response_model=ProductDetailResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update product"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Validate foreign keys if being updated
        if product_data.product_type_id:
            product_type = db.query(ProductType).filter(ProductType.id == product_data.product_type_id).first()
            if not product_type:
                raise HTTPException(status_code=400, detail="Product type not found")
        
        if product_data.category_id:
            category = db.query(Category).filter(Category.id == product_data.category_id).first()
            if not category:
                raise HTTPException(status_code=400, detail="Category not found")
        
        # Update fields
        for field, value in product_data.dict(exclude_unset=True).items():
            setattr(product, field, value)
        
        product.updated_by = current_user.id
        
        db.commit()
        db.refresh(product)
        
        return ProductDetailResponse(
            data=ProductResponse.from_orm(product),
            message="Product updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete product"""
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Soft delete
        product.is_active = False
        product.deleted_by = current_user.id
        from datetime import datetime
        product.deleted_on = datetime.utcnow()
        
        db.commit()
        
        return {"status": True, "message": "Product deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")


@router.get("/masters/all")
async def get_all_masters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all master data for product form dropdowns"""
    try:
        product_types = db.query(ProductType).filter(ProductType.is_active == True).all()
        categories = db.query(Category).filter(Category.is_active == True).all()
        sub_categories = db.query(SubCategory).filter(SubCategory.is_active == True).all()
        oem_vendors = db.query(OEMVendor).filter(OEMVendor.is_active == True).all()
        configurations = db.query(Configuration).filter(Configuration.is_active == True).all()
        
        return {
            "status": True,
            "message": "Master data retrieved successfully",
            "data": {
                "product_types": [{"id": pt.id, "name": pt.name, "abbreviation": pt.abbreviation} for pt in product_types],
                "categories": [{"id": cat.id, "name": cat.name, "abbreviation": cat.abbreviation} for cat in categories],
                "sub_categories": [{"id": sc.id, "name": sc.name, "abbreviation": sc.abbreviation, "category_id": sc.category_id} for sc in sub_categories],
                "oem_vendors": [{"id": oem.id, "name": oem.name, "abbreviation": oem.abbreviation} for oem in oem_vendors],
                "configurations": [{"id": conf.id, "name": conf.name, "abbreviation": conf.abbreviation} for conf in configurations]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve master data: {str(e)}")