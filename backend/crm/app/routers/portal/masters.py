"""
Masters Module API Routes for CRM
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session

from ...schemas.auth import StandardResponse
from ...schemas.masters import (
    PaginatedResponse, BaseFilter, ApprovalRequest,
    UOMCreate, ProductMasterCreate, ProductMasterUpdate, PriceListCreate,
    ProductPricingCreate, UserMasterCreate, UserMasterUpdate
)
from ...services.masters_service import MastersService
from ...dependencies.database import get_postgres_db

router = APIRouter(prefix="/api/masters", tags=["masters"])

def get_masters_service(db: Session = Depends(get_postgres_db)) -> MastersService:
    """Dependency to get masters service"""
    return MastersService(db)

# Product Master Routes
@router.get("/products", response_model=StandardResponse)
async def list_products(
    filters: BaseFilter = Depends(),
    cat1_type: Optional[str] = Query(None),
    cat2_category: Optional[str] = Query(None),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Get paginated list of products"""
    try:
        products = await masters_service.get_products(filters, cat1_type, cat2_category)
        return StandardResponse(
            status=True,
            message="Products retrieved successfully",
            data=products
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products", response_model=StandardResponse)
async def create_product(
    product_data: ProductMasterCreate,
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create new product"""
    try:
        # For now, use a default created_by value. In real implementation, get from auth
        product = await masters_service.create_product(product_data, created_by=1)
        return StandardResponse(
            status=True,
            message="Product created successfully",
            data=product
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/{product_id}", response_model=StandardResponse)
async def get_product(
    product_id: int,
    masters_service: MastersService = Depends(get_masters_service)
):
    """Get product by ID"""
    try:
        product = await masters_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return StandardResponse(
            status=True,
            message="Product retrieved successfully", 
            data=product
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{product_id}", response_model=StandardResponse)
async def update_product(
    product_id: int,
    product_data: ProductMasterUpdate,
    masters_service: MastersService = Depends(get_masters_service)
):
    """Update product"""
    try:
        # For now, use a default updated_by value. In real implementation, get from auth
        product = await masters_service.update_product(product_id, product_data, updated_by=1)
        return StandardResponse(
            status=True,
            message="Product updated successfully",
            data=product
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# UOM Master Routes
@router.get("/uoms", response_model=StandardResponse)
async def list_uoms(
    filters: BaseFilter = Depends(),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Get paginated list of UOMs"""
    try:
        uoms = await masters_service.get_uoms(filters)
        return StandardResponse(
            status=True,
            message="UOMs retrieved successfully",
            data=uoms
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/uoms", response_model=StandardResponse)
async def create_uom(
    uom_data: UOMCreate,
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create new UOM"""
    try:
        # For now, use a default created_by value. In real implementation, get from auth
        uom = await masters_service.create_uom(uom_data, created_by=1)
        return StandardResponse(
            status=True,
            message="UOM created successfully",
            data=uom
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Price List Routes
@router.get("/pricelists", response_model=StandardResponse)
async def list_price_lists(
    filters: BaseFilter = Depends(),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Get paginated list of price lists"""
    try:
        price_lists = await masters_service.get_price_lists(filters)
        return StandardResponse(
            status=True,
            message="Price lists retrieved successfully",
            data=price_lists
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pricelists", response_model=StandardResponse)
async def create_price_list(
    price_list_data: PriceListCreate,
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create new price list"""
    try:
        # For now, use a default created_by value. In real implementation, get from auth
        price_list = await masters_service.create_price_list(price_list_data, created_by=1)
        return StandardResponse(
            status=True,
            message="Price list created successfully",
            data=price_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pricelists/{price_list_id}/approve", response_model=StandardResponse)
async def approve_price_list(
    price_list_id: int,
    approval_data: ApprovalRequest,
    masters_service: MastersService = Depends(get_masters_service)
):
    """Approve or reject price list"""
    try:
        # For now, use a default approved_by value. In real implementation, get from auth
        result = await masters_service.approve_price_list(
            price_list_id, approval_data, approved_by=1
        )
        return StandardResponse(
            status=True,
            message=f"Price list {approval_data.decision} successfully",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Product Pricing Routes
@router.get("/products/{product_id}/pricing", response_model=StandardResponse)
async def get_product_pricing(
    product_id: int,
    price_list_id: Optional[int] = Query(None),
    uom_id: Optional[int] = Query(None),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Get product pricing for specific price list and UOM"""
    try:
        pricing = await masters_service.get_product_pricing(
            product_id, price_list_id, uom_id
        )
        return StandardResponse(
            status=True,
            message="Product pricing retrieved successfully",
            data=pricing
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{product_id}/pricing", response_model=StandardResponse)
async def create_product_pricing(
    product_id: int,
    pricing_data: ProductPricingCreate,
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create product pricing"""
    try:
        # For now, use a default created_by value. In real implementation, get from auth
        pricing = await masters_service.create_product_pricing(
            product_id, pricing_data, created_by=1
        )
        return StandardResponse(
            status=True,
            message="Product pricing created successfully",
            data=pricing
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User Management Routes
@router.get("/users", response_model=StandardResponse)
async def list_users(
    filters: BaseFilter = Depends(),
    department_id: Optional[int] = Query(None),
    role_id: Optional[int] = Query(None),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Get paginated list of users"""
    try:
        users = await masters_service.get_users(filters, department_id, role_id)
        return StandardResponse(
            status=True,
            message="Users retrieved successfully",
            data=users
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=StandardResponse)
async def create_user(
    user_data: UserMasterCreate,
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create new user"""
    try:
        # For now, use a default created_by value. In real implementation, get from auth
        user = await masters_service.create_user(user_data, created_by=1)
        return StandardResponse(
            status=True,
            message="User created successfully",
            data=user
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lookup Routes
@router.get("/departments", response_model=StandardResponse)
async def list_departments(
    masters_service: MastersService = Depends(get_masters_service)
):
    """Get all departments for dropdowns"""
    try:
        departments = await masters_service.get_all_departments()
        return StandardResponse(
            status=True,
            message="Departments retrieved successfully",
            data=departments
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/roles", response_model=StandardResponse)
async def list_roles(
    masters_service: MastersService = Depends(get_masters_service)
):
    """Get all roles for dropdowns"""
    try:
        roles = await masters_service.get_all_roles()
        return StandardResponse(
            status=True,
            message="Roles retrieved successfully",
            data=roles
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))