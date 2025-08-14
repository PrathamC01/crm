"""
Enhanced Company Management API endpoints for Swayatta 4.0 - Simplified without approval workflow
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import Optional, List, Dict
from ...schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyListResponse,
    CompanyResponse,
    CompanyStats,
    DuplicateCheckResult,
)
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_companies_read, require_companies_write
from ...services.company_service import CompanyService
from ...dependencies.database import get_postgres_db
from ...utils.minio_client import minio_client

router = APIRouter(prefix="/api/companies", tags=["Company Management"])


async def get_company_service(postgres_pool=Depends(get_postgres_db)) -> CompanyService:
    return CompanyService(postgres_pool)


@router.get("/", response_model=StandardResponse)
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: Optional[int] = Query(20, le=500),
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    company_type: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    is_high_revenue: Optional[bool] = Query(None),
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service),
):
    """Get all companies with advanced filtering and role-based access"""

    # Build filters dict
    filters = {}
    if status:
        filters["status"] = status
    if company_type:
        filters["company_type"] = company_type
    if industry:
        filters["industry"] = industry
    if is_high_revenue is not None:
        filters["is_high_revenue"] = is_high_revenue

    companies = company_service.get_companies(
        skip=skip,
        limit=limit,
        search=search,
        filters=filters,
        user_role=current_user.get("role", "SALESPERSON"),
        user_id=current_user["id"],
    )

    total = company_service.get_company_count(
        search=search,
        filters=filters,
        user_role=current_user.get("role", "SALESPERSON"),
        user_id=current_user["id"],
    )

    company_response_list = [
        CompanyResponse.from_db_model(company) for company in companies
    ]

    return StandardResponse(
        status=True,
        message="Companies retrieved successfully",
        data=CompanyListResponse(
            companies=company_response_list, total=total, skip=skip, limit=limit
        ),
    )


@router.get("/stats", response_model=StandardResponse)
async def get_company_stats(
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service),
):
    """Get company statistics for dashboard"""
    stats = company_service.get_company_stats()
    return StandardResponse(
        status=True,
        message="Company statistics retrieved successfully",
        data=CompanyStats(**stats),
    )


@router.get("/{company_id}", response_model=StandardResponse)
async def get_company(
    company_id: int,
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service),
):
    """Get company by ID with full details"""
    company = company_service.get_company_by_id(company_id)
    if not company:
        from ...exceptions.custom_exceptions import NotFoundError

        raise NotFoundError("Company", company_id)

    company_response = CompanyResponse.from_db_model(company)
    return StandardResponse(
        status=True, message="Company retrieved successfully", data=company_response
    )


@router.post("/check-duplicates", response_model=StandardResponse)
async def check_duplicates(
    company_data: CompanyCreate,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Check for duplicate companies before creation"""
    result = company_service.check_duplicates(company_data)
    return StandardResponse(
        status=True, message="Duplicate check completed", data=result
    )


@router.post("/", response_model=StandardResponse)
async def create_company(
    company_data: CompanyCreate,
    override_duplicate: bool = Query(False),
    override_reason: Optional[str] = Query(None),
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Create new company - immediately active without approval"""

    user_role = current_user.get("role", "SALESPERSON")

    # Anyone can override duplicates now since no approval is needed
    if override_duplicate and not override_reason:
        raise HTTPException(status_code=400, detail="Override reason is required")

    try:
        company = company_service.create_company(
            company_data,
            current_user["id"],
            user_role=user_role,
            override_duplicate=override_duplicate,
            override_reason=override_reason,
        )

        company_response = CompanyResponse.from_db_model(company)

        return StandardResponse(
            status=True, message="Company created and activated successfully", data=company_response
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create company")


@router.put("/{company_id}", response_model=StandardResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Update company information"""

    user_role = current_user.get("role", "SALESPERSON")

    try:
        company = company_service.update_company(
            company_id, company_data, current_user["id"], user_role=user_role
        )

        if not company:
            from ...exceptions.custom_exceptions import NotFoundError

            raise NotFoundError("Company", company_id)

        return StandardResponse(status=True, message="Company updated successfully")

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to update company")


@router.post("/{company_id}/documents", response_model=StandardResponse)
async def upload_supporting_documents(
    company_id: int,
    files: Optional[List[UploadFile]] = File(...),
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Upload supporting documents for a company"""

    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    max_size = 10 * 1024 * 1024  # 10MB

    # ✅ Corrected length check
    if not files or len(files) < 1:
        return StandardResponse(
            status=True,
            message="No documents to upload",
        )

    uploaded_paths = []
    company = company_service.get_company_by_id(company_id)
    if not company:
        from ...exceptions.custom_exceptions import NotFoundError

        raise NotFoundError("Company", company_id)

    for file in files:
        # Validate type
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Allowed: PDF, JPEG, PNG",
            )

        # Validate size
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400, detail=f"File {file.filename} exceeds 10MB limit"
            )

        await file.seek(0)  # Reset pointer

        object_name = minio_client.upload_file(
            file, folder=f"documents/company/{company.name}"
        )

        if not object_name:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload file {file.filename}"
            )

        uploaded_paths.append(object_name)

    # ✅ Update documents
    existing_docs = company.supporting_documents or []
    company.supporting_documents = existing_docs + uploaded_paths
    company_service.db.commit()

    return StandardResponse(
        status=True,
        message="Documents uploaded successfully",
        data={"uploaded_files": uploaded_paths},
    )


@router.delete("/{company_id}", response_model=StandardResponse)
async def delete_company(
    company_id: int,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Soft delete company (Admin only)"""

    user_role = current_user.get("role", "SALESPERSON")

    try:
        deleted = company_service.delete_company(
            company_id, current_user["id"], user_role=user_role
        )

        if not deleted:
            from ...exceptions.custom_exceptions import NotFoundError

            raise NotFoundError("Company", company_id)

        return StandardResponse(status=True, message="Company deleted successfully")

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete company")


@router.get("/masters/industries", response_model=StandardResponse)
async def get_industry_masters():
    """Get predefined industry and sub-industry masters"""

    industry_masters = {
        "BFSI": [
            "Banking",
            "Insurance",
            "Financial Services",
            "Investment Banking",
            "Asset Management",
            "Fintech",
            "Credit & Lending",
        ],
        "Government": [
            "Central Government",
            "State Government",
            "Local Bodies",
            "PSUs",
            "Defense",
            "Public Services",
        ],
        "IT_ITeS": [
            "Software Development",
            "IT Services",
            "Product Engineering",
            "Data Analytics",
            "Cloud Services",
            "Cybersecurity",
            "BPO/KPO",
        ],
        "Manufacturing": [
            "Automotive",
            "Textiles",
            "Steel & Metals",
            "Chemicals",
            "Pharmaceuticals",
            "Electronics",
            "Heavy Machinery",
        ],
        "Healthcare": [
            "Hospitals",
            "Pharmaceuticals",
            "Medical Devices",
            "Diagnostics",
            "Telemedicine",
            "Healthcare IT",
        ],
        "Education": [
            "K-12 Schools",
            "Higher Education",
            "Vocational Training",
            "EdTech",
            "Online Learning",
            "Corporate Training",
        ],
        "Telecom": [
            "Mobile Services",
            "Internet Services",
            "Infrastructure",
            "Satellite Communications",
            "Network Equipment",
        ],
        "Energy_Utilities": [
            "Power Generation",
            "Oil & Gas",
            "Renewable Energy",
            "Utilities",
            "Mining",
            "Solar/Wind",
        ],
        "Retail_CPG": [
            "E-commerce",
            "Fashion & Apparel",
            "FMCG",
            "Consumer Electronics",
            "Food & Beverage",
            "Grocery Retail",
        ],
        "Logistics": [
            "Transportation",
            "Warehousing",
            "Supply Chain",
            "Last Mile Delivery",
            "Freight Services",
            "3PL Services",
        ],
        "Media_Entertainment": [
            "Broadcasting",
            "Digital Media",
            "Gaming",
            "Advertising",
            "Publishing",
            "Entertainment Production",
        ],
    }

    return StandardResponse(
        status=True,
        message="Industry masters retrieved successfully",
        data=industry_masters,
    )


@router.get("/masters/countries-states", response_model=StandardResponse)
async def get_country_state_masters():
    """Get country and state masters for address"""

    country_state_data = {
        "India": [
            "Andhra Pradesh",
            "Arunachal Pradesh",
            "Assam",
            "Bihar",
            "Chhattisgarh",
            "Goa",
            "Gujarat",
            "Haryana",
            "Himachal Pradesh",
            "Jharkhand",
            "Karnataka",
            "Kerala",
            "Madhya Pradesh",
            "Maharashtra",
            "Manipur",
            "Meghalaya",
            "Mizoram",
            "Nagaland",
            "Odisha",
            "Punjab",
            "Rajasthan",
            "Sikkim",
            "Tamil Nadu",
            "Telangana",
            "Tripura",
            "Uttar Pradesh",
            "Uttarakhand",
            "West Bengal",
        ],
        "USA": [
            "Alabama",
            "Alaska",
            "Arizona",
            "Arkansas",
            "California",
            "Colorado",
            "Connecticut",
            "Delaware",
            "Florida",
            "Georgia",
            "Hawaii",
            "Idaho",
        ],
        "UK": ["England", "Scotland", "Wales", "Northern Ireland"],
        "Canada": [
            "Alberta",
            "British Columbia",
            "Manitoba",
            "New Brunswick",
            "Newfoundland and Labrador",
            "Northwest Territories",
            "Nova Scotia",
            "Nunavut",
            "Ontario",
            "Prince Edward Island",
            "Quebec",
            "Saskatchewan",
            "Yukon",
        ],
        # Add more countries as needed
    }

    return StandardResponse(
        status=True,
        message="Country-state masters retrieved successfully",
        data=country_state_data,
    )