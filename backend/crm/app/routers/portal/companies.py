"""
Company Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from ...schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyListResponse,
    CompanyResponse,
)
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_companies_read, require_companies_write
from ...services.company_service import CompanyService
from ...dependencies.database import get_postgres_db

router = APIRouter(prefix="/api/companies", tags=["Company Management"])


async def get_company_service(postgres_pool=Depends(get_postgres_db)) -> CompanyService:
    return CompanyService(postgres_pool)


@router.get("/", response_model=StandardResponse)
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service),
):
    """Get all companies with pagination and search"""
    if limit is not None and limit > 500:
        from ...exceptions.custom_exceptions import ValidationError
        raise ValidationError("Limit cannot be greater than 500", {"limit": "Maximum allowed value is 500"})
    
    companies = company_service.get_companies(skip, limit, search)
    total = company_service.get_company_count(search)
    company_response_list = [
        CompanyResponse.model_validate(company) for company in companies
    ]
    return StandardResponse(
        status=True,
        message="Companies retrieved successfully",
        data=CompanyListResponse(
            companies=company_response_list, total=total, skip=skip, limit=limit
        ),
    )


@router.get("/{company_id}", response_model=StandardResponse)
async def get_company(
    company_id: int,
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service),
):
    """Get company by ID"""
    company = company_service.get_company_by_id(company_id)
    if not company:
        from ...exceptions.custom_exceptions import NotFoundError
        raise NotFoundError("Company", company_id)

    company_response = CompanyResponse.model_validate(company)
    return StandardResponse(
        status=True, message="Company retrieved successfully", data=company_response
    )


@router.post("/", response_model=StandardResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Create new company"""
    try:
        company = company_service.create_company(company_data, current_user["id"])
        company_response = CompanyResponse.model_validate(company)

        return StandardResponse(
            status=True, message="Company created successfully", data=company_response
        )
    except Exception as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Company name already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{company_id}", response_model=StandardResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Update company information"""
    try:
        company = company_service.update_company(
            company_id, company_data, current_user["id"]
        )
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        return StandardResponse(status=True, message="Company updated successfully")
    except HTTPException as he:
        print(he)
        raise he
    except Exception as e:
        print(e)


@router.delete("/{company_id}", response_model=StandardResponse)
async def delete_company(
    company_id: int,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Soft delete company"""
    try:
        deleted = company_service.delete_company(company_id, current_user["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Company not found")

        return StandardResponse(status=True, message="Company deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        print(e)
