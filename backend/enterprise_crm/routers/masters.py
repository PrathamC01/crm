"""
Masters Module API Routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session

from ..schemas.common import StandardResponse, PaginatedResponse, BaseFilter, ApprovalRequest
from ..schemas.masters import *
from ..dependencies.auth import get_current_user, require_permission
from ..services.masters_service import get_masters_service, MastersService
from ..database import get_db

router = APIRouter(prefix="/api/masters", tags=["masters"])

# Product Master Routes
@router.get("/products", response_model=StandardResponse)
async def list_products(
    filters: BaseFilter = Depends(),
    cat1_type: Optional[str] = Query(None),
    cat2_category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(require_permission("masters", "write")),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create new product"""
    try:
        product = await masters_service.create_product(product_data, current_user["id"])
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(require_permission("masters", "write")),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Update product"""
    try:
        product = await masters_service.update_product(product_id, product_data, current_user["id"])
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(require_permission("masters", "write")),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create new UOM"""
    try:
        uom = await masters_service.create_uom(uom_data, current_user["id"])
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(require_permission("masters", "write")),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create new price list"""
    try:
        price_list = await masters_service.create_price_list(price_list_data, current_user["id"])
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
    current_user: dict = Depends(require_permission("masters", "approve")),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Approve or reject price list"""
    try:
        result = await masters_service.approve_price_list(
            price_list_id, approval_data, current_user["id"]
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(require_permission("masters", "write")),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create product pricing"""
    try:
        pricing = await masters_service.create_product_pricing(
            product_id, pricing_data, current_user["id"]
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(require_permission("masters", "write")),
    masters_service: MastersService = Depends(get_masters_service)
):
    """Create new user"""
    try:
        user = await masters_service.create_user(user_data, current_user["id"])
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
    current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(get_current_user),
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