"""
Company Management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from typing import Optional
import os
from ...schemas.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyListResponse,
    CompanyResponse,
    DocumentUploadResponse,
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
    try:
        if limit is not None and limit > 500:
            raise HTTPException(
                status_code=422, detail="Limit cannot be greater than 500"
            )
        companies = company_service.get_companies(skip, limit, search)
        total = company_service.get_company_count(search)
        company_response_list = [
            CompanyResponse.from_orm(company) for company in companies
        ]
        return StandardResponse(
            status=True,
            message="Companies retrieved successfully",
            data=CompanyListResponse(
                companies=company_response_list, total=total, skip=skip, limit=limit
            ),
        )
    except Exception as e:
        print(e)


@router.get("/{company_id}", response_model=StandardResponse)
async def get_company(
    company_id: int,
    include_documents: bool = Query(False),
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service),
):
    """Get company by ID"""
    try:
        company = company_service.get_company_by_id(company_id, include_documents)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        return StandardResponse(
            status=True, message="Company retrieved successfully", data=company
        )
    except HTTPException:
        raise
    except Exception as e:
        print(e)


@router.post("/", response_model=StandardResponse)
async def create_company(
    company_data: CompanyCreate,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Create new company"""
    try:
        company = company_service.create_company(company_data, current_user["id"])
        
        # Convert to response model
        company_response = CompanyResponse.from_orm(company)

        return StandardResponse(
            status=True, 
            message="Company created successfully", 
            data=company_response
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

        # Convert to response model
        company_response = CompanyResponse.from_orm(company)

        return StandardResponse(
            status=True, 
            message="Company updated successfully", 
            data=company_response
        )
    except HTTPException as he:
        print(he)
        raise he
    except Exception as e:
        print(f"Error updating company: {e}")
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=400, detail="Company name already exists")
        raise HTTPException(status_code=500, detail=str(e))


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


@router.post("/{company_id}/upload", response_model=StandardResponse)
async def upload_company_document(
    company_id: int,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Upload a document for a company"""
    try:
        # Validate file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 
                        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Allowed: PDF, JPG, PNG, DOC, DOCX"
            )

        # Validate file size (10MB max)
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large. Maximum 10MB allowed")

        # Validate document type
        valid_doc_types = ['GST_CERTIFICATE', 'PAN_CARD', 'INCORPORATION_CERTIFICATE', 
                          'TAX_DOCUMENT', 'BANK_STATEMENT', 'OTHER']
        
        if document_type not in valid_doc_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid document type. Allowed: {', '.join(valid_doc_types)}"
            )

        document = await company_service.upload_document(
            company_id, file, document_type, current_user["id"]
        )

        response_data = DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            document_type=document.document_type,
            file_size=document.file_size,
            message="Document uploaded successfully"
        )

        return StandardResponse(
            status=True,
            message="Document uploaded successfully",
            data=response_data
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_id}/documents", response_model=StandardResponse)
async def get_company_documents(
    company_id: int,
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service),
):
    """Get all documents for a company"""
    try:
        # Verify company exists
        company = company_service.get_company_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        documents = company_service.get_company_documents(company_id)
        
        return StandardResponse(
            status=True,
            message="Documents retrieved successfully",
            data={"documents": documents}
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{company_id}/documents/{document_id}", response_model=StandardResponse)
async def delete_company_document(
    company_id: int,
    document_id: int,
    current_user: dict = Depends(require_companies_write),
    company_service: CompanyService = Depends(get_company_service),
):
    """Delete a company document"""
    try:
        deleted = company_service.delete_document(document_id, company_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")

        return StandardResponse(
            status=True,
            message="Document deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{company_id}/documents/{document_id}/download")
async def download_company_document(
    company_id: int,
    document_id: int,
    current_user: dict = Depends(require_companies_read),
    company_service: CompanyService = Depends(get_company_service),
):
    """Download a company document"""
    try:
        documents = company_service.get_company_documents(company_id)
        document = next((doc for doc in documents if doc.id == document_id), None)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if not os.path.exists(document.file_path):
            raise HTTPException(status_code=404, detail="File not found on server")

        return FileResponse(
            path=document.file_path,
            filename=document.original_filename,
            media_type=document.mime_type
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error downloading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
