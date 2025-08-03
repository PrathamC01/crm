"""
Company Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ...schemas.company import CompanyCreate, CompanyUpdate, CompanyListResponse
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_companies_read, require_companies_write
from ...services.company_service import CompanyService
from ...dependencies.database import get_postgres_db

router = APIRouter(prefix="/api/companies", tags=["Company Management"])

async def get_company_service(postgres_pool = Depends(get_postgres_db)) -> CompanyService:
    return CompanyService(postgres_pool)

@router.get("/", response_model=StandardResponse)
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service)
):
    """Get all companies with pagination and search"""
    try:
        companies = await company_service.get_companies(skip, limit, search)
        total = await company_service.get_company_count(search)
        
        return StandardResponse(
            status=True,
            message="Companies retrieved successfully",
            data={
                "companies": companies,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{company_id}", response_model=StandardResponse)
async def get_company(
    company_id: str,
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service)
):
    """Get company by ID"""
    try:
        company = await company_service.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return StandardResponse(
            status=True,
            message="Company retrieved successfully",
            data=company
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=StandardResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service)
):
    """Create new company"""
    try:
        company = await company_service.create_company(company_data, current_user["id"])
        
        return StandardResponse(
            status=True,
            message="Company created successfully",
            data=company
        )
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Company name already exists")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{company_id}", response_model=StandardResponse)
async def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service)
):
    """Update company information"""
    try:
        company = await company_service.update_company(company_id, company_data, current_user["id"])
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return StandardResponse(
            status=True,
            message="Company updated successfully",
            data=company
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{company_id}", response_model=StandardResponse)
async def delete_company(
    company_id: str,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service)
):
    """Soft delete company"""
    try:
        deleted = await company_service.delete_company(company_id, current_user["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return StandardResponse(
            status=True,
            message="Company deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))