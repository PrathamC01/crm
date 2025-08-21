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
    ValidationResult,
    CompanyDropdownItem,
    GeographicData
)
from ...schemas.auth import StandardResponse
from ...dependencies.rbac import require_companies_read, require_companies_write
from ...services.company_service import CompanyService
from ...dependencies.database import get_postgres_db
from ...utils.minio_client import minio_client
from ...models.geographic import Country, State, City
from ...services.geographic_service import GeographicService

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


@router.get("/masters/countries", response_model=StandardResponse)
async def get_countries_master():
    """Get comprehensive list of all countries with ISO codes"""
    
    countries = [
        {"code": "AD", "name": "Andorra"},
        {"code": "AE", "name": "United Arab Emirates"},
        {"code": "AF", "name": "Afghanistan"},
        {"code": "AG", "name": "Antigua and Barbuda"},
        {"code": "AI", "name": "Anguilla"},
        {"code": "AL", "name": "Albania"},
        {"code": "AM", "name": "Armenia"},
        {"code": "AO", "name": "Angola"},
        {"code": "AQ", "name": "Antarctica"},
        {"code": "AR", "name": "Argentina"},
        {"code": "AS", "name": "American Samoa"},
        {"code": "AT", "name": "Austria"},
        {"code": "AU", "name": "Australia"},
        {"code": "AW", "name": "Aruba"},
        {"code": "AX", "name": "Åland Islands"},
        {"code": "AZ", "name": "Azerbaijan"},
        {"code": "BA", "name": "Bosnia and Herzegovina"},
        {"code": "BB", "name": "Barbados"},
        {"code": "BD", "name": "Bangladesh"},
        {"code": "BE", "name": "Belgium"},
        {"code": "BF", "name": "Burkina Faso"},
        {"code": "BG", "name": "Bulgaria"},
        {"code": "BH", "name": "Bahrain"},
        {"code": "BI", "name": "Burundi"},
        {"code": "BJ", "name": "Benin"},
        {"code": "BL", "name": "Saint Barthélemy"},
        {"code": "BM", "name": "Bermuda"},
        {"code": "BN", "name": "Brunei Darussalam"},
        {"code": "BO", "name": "Bolivia"},
        {"code": "BQ", "name": "Bonaire, Sint Eustatius and Saba"},
        {"code": "BR", "name": "Brazil"},
        {"code": "BS", "name": "Bahamas"},
        {"code": "BT", "name": "Bhutan"},
        {"code": "BV", "name": "Bouvet Island"},
        {"code": "BW", "name": "Botswana"},
        {"code": "BY", "name": "Belarus"},
        {"code": "BZ", "name": "Belize"},
        {"code": "CA", "name": "Canada"},
        {"code": "CC", "name": "Cocos (Keeling) Islands"},
        {"code": "CD", "name": "Congo, Democratic Republic of the"},
        {"code": "CF", "name": "Central African Republic"},
        {"code": "CG", "name": "Congo"},
        {"code": "CH", "name": "Switzerland"},
        {"code": "CI", "name": "Côte d'Ivoire"},
        {"code": "CK", "name": "Cook Islands"},
        {"code": "CL", "name": "Chile"},
        {"code": "CM", "name": "Cameroon"},
        {"code": "CN", "name": "China"},
        {"code": "CO", "name": "Colombia"},
        {"code": "CR", "name": "Costa Rica"},
        {"code": "CU", "name": "Cuba"},
        {"code": "CV", "name": "Cabo Verde"},
        {"code": "CW", "name": "Curaçao"},
        {"code": "CX", "name": "Christmas Island"},
        {"code": "CY", "name": "Cyprus"},
        {"code": "CZ", "name": "Czech Republic"},
        {"code": "DE", "name": "Germany"},
        {"code": "DJ", "name": "Djibouti"},
        {"code": "DK", "name": "Denmark"},
        {"code": "DM", "name": "Dominica"},
        {"code": "DO", "name": "Dominican Republic"},
        {"code": "DZ", "name": "Algeria"},
        {"code": "EC", "name": "Ecuador"},
        {"code": "EE", "name": "Estonia"},
        {"code": "EG", "name": "Egypt"},
        {"code": "EH", "name": "Western Sahara"},
        {"code": "ER", "name": "Eritrea"},
        {"code": "ES", "name": "Spain"},
        {"code": "ET", "name": "Ethiopia"},
        {"code": "FI", "name": "Finland"},
        {"code": "FJ", "name": "Fiji"},
        {"code": "FK", "name": "Falkland Islands (Malvinas)"},
        {"code": "FM", "name": "Micronesia, Federated States of"},
        {"code": "FO", "name": "Faroe Islands"},
        {"code": "FR", "name": "France"},
        {"code": "GA", "name": "Gabon"},
        {"code": "GB", "name": "United Kingdom"},
        {"code": "GD", "name": "Grenada"},
        {"code": "GE", "name": "Georgia"},
        {"code": "GF", "name": "French Guiana"},
        {"code": "GG", "name": "Guernsey"},
        {"code": "GH", "name": "Ghana"},
        {"code": "GI", "name": "Gibraltar"},
        {"code": "GL", "name": "Greenland"},
        {"code": "GM", "name": "Gambia"},
        {"code": "GN", "name": "Guinea"},
        {"code": "GP", "name": "Guadeloupe"},
        {"code": "GQ", "name": "Equatorial Guinea"},
        {"code": "GR", "name": "Greece"},
        {"code": "GS", "name": "South Georgia and the South Sandwich Islands"},
        {"code": "GT", "name": "Guatemala"},
        {"code": "GU", "name": "Guam"},
        {"code": "GW", "name": "Guinea-Bissau"},
        {"code": "GY", "name": "Guyana"},
        {"code": "HK", "name": "Hong Kong"},
        {"code": "HM", "name": "Heard Island and McDonald Islands"},
        {"code": "HN", "name": "Honduras"},
        {"code": "HR", "name": "Croatia"},
        {"code": "HT", "name": "Haiti"},
        {"code": "HU", "name": "Hungary"},
        {"code": "ID", "name": "Indonesia"},
        {"code": "IE", "name": "Ireland"},
        {"code": "IL", "name": "Israel"},
        {"code": "IM", "name": "Isle of Man"},
        {"code": "IN", "name": "India"},
        {"code": "IO", "name": "British Indian Ocean Territory"},
        {"code": "IQ", "name": "Iraq"},
        {"code": "IR", "name": "Iran, Islamic Republic of"},
        {"code": "IS", "name": "Iceland"},
        {"code": "IT", "name": "Italy"},
        {"code": "JE", "name": "Jersey"},
        {"code": "JM", "name": "Jamaica"},
        {"code": "JO", "name": "Jordan"},
        {"code": "JP", "name": "Japan"},
        {"code": "KE", "name": "Kenya"},
        {"code": "KG", "name": "Kyrgyzstan"},
        {"code": "KH", "name": "Cambodia"},
        {"code": "KI", "name": "Kiribati"},
        {"code": "KM", "name": "Comoros"},
        {"code": "KN", "name": "Saint Kitts and Nevis"},
        {"code": "KP", "name": "Korea, Democratic People's Republic of"},
        {"code": "KR", "name": "Korea, Republic of"},
        {"code": "KW", "name": "Kuwait"},
        {"code": "KY", "name": "Cayman Islands"},
        {"code": "KZ", "name": "Kazakhstan"},
        {"code": "LA", "name": "Lao People's Democratic Republic"},
        {"code": "LB", "name": "Lebanon"},
        {"code": "LC", "name": "Saint Lucia"},
        {"code": "LI", "name": "Liechtenstein"},
        {"code": "LK", "name": "Sri Lanka"},
        {"code": "LR", "name": "Liberia"},
        {"code": "LS", "name": "Lesotho"},
        {"code": "LT", "name": "Lithuania"},
        {"code": "LU", "name": "Luxembourg"},
        {"code": "LV", "name": "Latvia"},
        {"code": "LY", "name": "Libya"},
        {"code": "MA", "name": "Morocco"},
        {"code": "MC", "name": "Monaco"},
        {"code": "MD", "name": "Moldova, Republic of"},
        {"code": "ME", "name": "Montenegro"},
        {"code": "MF", "name": "Saint Martin (French part)"},
        {"code": "MG", "name": "Madagascar"},
        {"code": "MH", "name": "Marshall Islands"},
        {"code": "MK", "name": "North Macedonia"},
        {"code": "ML", "name": "Mali"},
        {"code": "MM", "name": "Myanmar"},
        {"code": "MN", "name": "Mongolia"},
        {"code": "MO", "name": "Macao"},
        {"code": "MP", "name": "Northern Mariana Islands"},
        {"code": "MQ", "name": "Martinique"},
        {"code": "MR", "name": "Mauritania"},
        {"code": "MS", "name": "Montserrat"},
        {"code": "MT", "name": "Malta"},
        {"code": "MU", "name": "Mauritius"},
        {"code": "MV", "name": "Maldives"},
        {"code": "MW", "name": "Malawi"},
        {"code": "MX", "name": "Mexico"},
        {"code": "MY", "name": "Malaysia"},
        {"code": "MZ", "name": "Mozambique"},
        {"code": "NA", "name": "Namibia"},
        {"code": "NC", "name": "New Caledonia"},
        {"code": "NE", "name": "Niger"},
        {"code": "NF", "name": "Norfolk Island"},
        {"code": "NG", "name": "Nigeria"},
        {"code": "NI", "name": "Nicaragua"},
        {"code": "NL", "name": "Netherlands"},
        {"code": "NO", "name": "Norway"},
        {"code": "NP", "name": "Nepal"},
        {"code": "NR", "name": "Nauru"},
        {"code": "NU", "name": "Niue"},
        {"code": "NZ", "name": "New Zealand"},
        {"code": "OM", "name": "Oman"},
        {"code": "PA", "name": "Panama"},
        {"code": "PE", "name": "Peru"},
        {"code": "PF", "name": "French Polynesia"},
        {"code": "PG", "name": "Papua New Guinea"},
        {"code": "PH", "name": "Philippines"},
        {"code": "PK", "name": "Pakistan"},
        {"code": "PL", "name": "Poland"},
        {"code": "PM", "name": "Saint Pierre and Miquelon"},
        {"code": "PN", "name": "Pitcairn"},
        {"code": "PR", "name": "Puerto Rico"},
        {"code": "PS", "name": "Palestine, State of"},
        {"code": "PT", "name": "Portugal"},
        {"code": "PW", "name": "Palau"},
        {"code": "PY", "name": "Paraguay"},
        {"code": "QA", "name": "Qatar"},
        {"code": "RE", "name": "Réunion"},
        {"code": "RO", "name": "Romania"},
        {"code": "RS", "name": "Serbia"},
        {"code": "RU", "name": "Russian Federation"},
        {"code": "RW", "name": "Rwanda"},
        {"code": "SA", "name": "Saudi Arabia"},
        {"code": "SB", "name": "Solomon Islands"},
        {"code": "SC", "name": "Seychelles"},
        {"code": "SD", "name": "Sudan"},
        {"code": "SE", "name": "Sweden"},
        {"code": "SG", "name": "Singapore"},
        {"code": "SH", "name": "Saint Helena, Ascension and Tristan da Cunha"},
        {"code": "SI", "name": "Slovenia"},
        {"code": "SJ", "name": "Svalbard and Jan Mayen"},
        {"code": "SK", "name": "Slovakia"},
        {"code": "SL", "name": "Sierra Leone"},
        {"code": "SM", "name": "San Marino"},
        {"code": "SN", "name": "Senegal"},
        {"code": "SO", "name": "Somalia"},
        {"code": "SR", "name": "Suriname"},
        {"code": "SS", "name": "South Sudan"},
        {"code": "ST", "name": "Sao Tome and Principe"},
        {"code": "SV", "name": "El Salvador"},
        {"code": "SX", "name": "Sint Maarten (Dutch part)"},
        {"code": "SY", "name": "Syrian Arab Republic"},
        {"code": "SZ", "name": "Eswatini"},
        {"code": "TC", "name": "Turks and Caicos Islands"},
        {"code": "TD", "name": "Chad"},
        {"code": "TF", "name": "French Southern Territories"},
        {"code": "TG", "name": "Togo"},
        {"code": "TH", "name": "Thailand"},
        {"code": "TJ", "name": "Tajikistan"},
        {"code": "TK", "name": "Tokelau"},
        {"code": "TL", "name": "Timor-Leste"},
        {"code": "TM", "name": "Turkmenistan"},
        {"code": "TN", "name": "Tunisia"},
        {"code": "TO", "name": "Tonga"},
        {"code": "TR", "name": "Turkey"},
        {"code": "TT", "name": "Trinidad and Tobago"},
        {"code": "TV", "name": "Tuvalu"},
        {"code": "TW", "name": "Taiwan, Province of China"},
        {"code": "TZ", "name": "Tanzania, United Republic of"},
        {"code": "UA", "name": "Ukraine"},
        {"code": "UG", "name": "Uganda"},
        {"code": "UM", "name": "United States Minor Outlying Islands"},
        {"code": "US", "name": "United States"},
        {"code": "UY", "name": "Uruguay"},
        {"code": "UZ", "name": "Uzbekistan"},
        {"code": "VA", "name": "Holy See (Vatican City State)"},
        {"code": "VC", "name": "Saint Vincent and the Grenadines"},
        {"code": "VE", "name": "Venezuela, Bolivarian Republic of"},
        {"code": "VG", "name": "Virgin Islands, British"},
        {"code": "VI", "name": "Virgin Islands, U.S."},
        {"code": "VN", "name": "Viet Nam"},
        {"code": "VU", "name": "Vanuatu"},
        {"code": "WF", "name": "Wallis and Futuna"},
        {"code": "WS", "name": "Samoa"},
        {"code": "YE", "name": "Yemen"},
        {"code": "YT", "name": "Mayotte"},
        {"code": "ZA", "name": "South Africa"},
        {"code": "ZM", "name": "Zambia"},
        {"code": "ZW", "name": "Zimbabwe"}
    ]
    
    # Sort alphabetically by name
    countries_sorted = sorted(countries, key=lambda x: x["name"])
    
    return StandardResponse(
        status=True,
        message="Countries list retrieved successfully",
        data=countries_sorted
    )


@router.get("/masters/states/{country_code}", response_model=StandardResponse)
async def get_states_by_country(country_code: str):
    """Get states/provinces for a specific country by ISO code"""
    
    # Comprehensive state/province data for major countries
    states_data = {
        "IN": [  # India
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Delhi (NCT)", "Chandigarh", "Puducherry", "Jammu and Kashmir",
            "Andaman and Nicobar Islands", "Lakshadweep", "Dadra and Nagar Haveli and Daman and Diu"
        ],
        "US": [  # United States
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
            "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
            "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
            "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
            "New Hampshire", "New Jersey", "New Mexico", "New York",
            "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
            "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
            "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
            "West Virginia", "Wisconsin", "Wyoming", "Washington D.C."
        ],
        "CA": [  # Canada
            "Alberta", "British Columbia", "Manitoba", "New Brunswick",
            "Newfoundland and Labrador", "Northwest Territories", "Nova Scotia",
            "Nunavut", "Ontario", "Prince Edward Island", "Quebec",
            "Saskatchewan", "Yukon"
        ],
        "AU": [  # Australia
            "New South Wales", "Victoria", "Queensland", "Western Australia",
            "South Australia", "Tasmania", "Northern Territory",
            "Australian Capital Territory"
        ],
        "DE": [  # Germany
            "Baden-Württemberg", "Bavaria", "Berlin", "Brandenburg", "Bremen",
            "Hamburg", "Hesse", "Lower Saxony", "Mecklenburg-Vorpommern",
            "North Rhine-Westphalia", "Rhineland-Palatinate", "Saarland",
            "Saxony", "Saxony-Anhalt", "Schleswig-Holstein", "Thuringia"
        ],
        "FR": [  # France
            "Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Brittany",
            "Centre-Val de Loire", "Corsica", "Grand Est", "Hauts-de-France",
            "Île-de-France", "Normandy", "Nouvelle-Aquitaine", "Occitanie",
            "Pays de la Loire", "Provence-Alpes-Côte d'Azur"
        ],
        "BR": [  # Brazil
            "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará",
            "Distrito Federal", "Espírito Santo", "Goiás", "Maranhão",
            "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará",
            "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
            "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia",
            "Roraima", "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"
        ],
        "CN": [  # China
            "Anhui", "Beijing", "Chongqing", "Fujian", "Gansu", "Guangdong",
            "Guangxi", "Guizhou", "Hainan", "Hebei", "Heilongjiang", "Henan",
            "Hubei", "Hunan", "Inner Mongolia", "Jiangsu", "Jiangxi", "Jilin",
            "Liaoning", "Ningxia", "Qinghai", "Shaanxi", "Shandong", "Shanghai",
            "Shanxi", "Sichuan", "Tianjin", "Tibet", "Xinjiang", "Yunnan", "Zhejiang"
        ],
        "JP": [  # Japan
            "Aichi", "Akita", "Aomori", "Chiba", "Ehime", "Fukui", "Fukuoka",
            "Fukushima", "Gifu", "Gunma", "Hiroshima", "Hokkaido", "Hyogo",
            "Ibaraki", "Ishikawa", "Iwate", "Kagawa", "Kagoshima", "Kanagawa",
            "Kochi", "Kumamoto", "Kyoto", "Mie", "Miyagi", "Miyazaki", "Nagano",
            "Nagasaki", "Nara", "Niigata", "Oita", "Okayama", "Okinawa", "Osaka",
            "Saga", "Saitama", "Shiga", "Shimane", "Shizuoka", "Tochigi", "Tokushima",
            "Tokyo", "Tottori", "Toyama", "Wakayama", "Yamagata", "Yamaguchi", "Yamanashi"
        ],
        "GB": [  # United Kingdom
            "England", "Scotland", "Wales", "Northern Ireland"
        ],
        "IT": [  # Italy
            "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
            "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardy", "Marche",
            "Molise", "Piedmont", "Apulia", "Sardinia", "Sicily", "Tuscany",
            "Trentino-Alto Adige", "Umbria", "Aosta Valley", "Veneto"
        ],
        "ES": [  # Spain
            "Andalusia", "Aragon", "Asturias", "Balearic Islands", "Basque Country",
            "Canary Islands", "Cantabria", "Castile and León", "Castile-La Mancha",
            "Catalonia", "Extremadura", "Galicia", "La Rioja", "Community of Madrid",
            "Region of Murcia", "Navarre", "Valencian Community", "Ceuta", "Melilla"
        ],
        "RU": [  # Russia (major federal subjects)
            "Moscow", "Saint Petersburg", "Moscow Oblast", "Krasnodar Krai",
            "Rostov Oblast", "Tatarstan", "Bashkortostan", "Sverdlovsk Oblast",
            "Nizhny Novgorod Oblast", "Samara Oblast", "Chelyabinsk Oblast",
            "Volgograd Oblast", "Novosibirsk Oblast", "Krasnoyarsk Krai",
            "Perm Krai", "Voronezh Oblast", "Saratov Oblast", "Kemerovo Oblast"
        ],
        "MX": [  # Mexico
            "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
            "Chiapas", "Chihuahua", "Coahuila", "Colima", "Durango", "Guanajuato",
            "Guerrero", "Hidalgo", "Jalisco", "Mexico", "Michoacán", "Morelos",
            "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
            "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas",
            "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas", "Mexico City"
        ],
        "AR": [  # Argentina
            "Buenos Aires", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes",
            "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza",
            "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis",
            "Santa Cruz", "Santa Fe", "Santiago del Estero", "Tierra del Fuego",
            "Tucumán"
        ],
        "ZA": [  # South Africa
            "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo",
            "Mpumalanga", "Northern Cape", "North West", "Western Cape"
        ],
        "NG": [  # Nigeria
            "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
            "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
            "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi",
            "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo",
            "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara", "FCT Abuja"
        ],
        "ID": [  # Indonesia
            "Aceh", "North Sumatra", "West Sumatra", "Riau", "Riau Islands",
            "Jambi", "South Sumatra", "Bangka Belitung Islands", "Bengkulu",
            "Lampung", "Jakarta", "West Java", "Banten", "Central Java",
            "Yogyakarta", "East Java", "Bali", "West Nusa Tenggara",
            "East Nusa Tenggara", "West Kalimantan", "Central Kalimantan",
            "South Kalimantan", "East Kalimantan", "North Kalimantan"
        ],
        "TH": [  # Thailand
            "Bangkok", "Krung Thep Maha Nakhon", "Chiang Mai", "Chiang Rai",
            "Nakhon Ratchasima", "Khon Kaen", "Ubon Ratchathani", "Udon Thani",
            "Surat Thani", "Phuket", "Songkhla", "Chon Buri", "Rayong",
            "Nakhon Si Thammarat", "Phitsanulok", "Nakhon Sawan"
        ]
    }
    
    country_code = country_code.upper()
    states = states_data.get(country_code, [])
    
    if not states:
        return StandardResponse(
            status=True,
            message=f"No states/provinces available for this country",
            data={"states": [], "message": "This country does not have subdivisions or data is not available"}
        )
    
    # Sort alphabetically
    states_sorted = sorted(states)
    
    return StandardResponse(
        status=True,
        message=f"States/provinces retrieved successfully",
        data={"states": states_sorted}
    )


@router.get("/masters/cities/{country_code}/{state_name}", response_model=StandardResponse)
async def get_cities_by_state(country_code: str, state_name: str):
    """Get cities for a specific state/province"""
    
    # Major cities data for key states/provinces
    cities_data = {
        "IN": {  # India
            "Maharashtra": [
                "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", 
                "Kolhapur", "Sangli", "Ahmednagar", "Latur", "Jalgaon", "Akola",
                "Satara", "Chandrapur", "Parbhani", "Ichalkaranji", "Jalna", "Ambajogai"
            ],
            "Karnataka": [
                "Bangalore", "Mysore", "Hubli", "Dharwad", "Mangalore", "Belgaum",
                "Gulbarga", "Davanagere", "Bellary", "Bijapur", "Shimoga", "Tumkur",
                "Raichur", "Bidar", "Hospet", "Gadag", "Udupi", "Chikmagalur"
            ],
            "Tamil Nadu": [
                "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli",
                "Tiruppur", "Vellore", "Thoothukudi", "Nagercoil", "Thanjavur", "Dindigul",
                "Cuddalore", "Kanchipuram", "Erode", "Tiruvannamalai", "Pollachi", "Rajapalayam"
            ],
            "Delhi (NCT)": [
                "New Delhi", "Delhi Cantonment", "North Delhi", "South Delhi", 
                "East Delhi", "West Delhi", "Central Delhi", "North East Delhi",
                "North West Delhi", "South East Delhi", "South West Delhi"
            ],
            "Gujarat": [
                "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar",
                "Junagadh", "Gandhinagar", "Anand", "Navsari", "Morbi", "Mehsana",
                "Surendranagar", "Bharuch", "Vapi", "Veraval", "Porbandar", "Godhra"
            ],
            "Uttar Pradesh": [
                "Lucknow", "Kanpur", "Ghaziabad", "Agra", "Varanasi", "Meerut",
                "Allahabad", "Bareilly", "Aligarh", "Moradabad", "Saharanpur", "Gorakhpur",
                "Noida", "Firozabad", "Loni", "Muzaffarnagar", "Mathura", "Rampur"
            ],
            "West Bengal": [
                "Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Malda",
                "Bardhaman", "Baharampur", "Habra", "Kharagpur", "Shantipur", "Dankuni",
                "Dhulian", "Ranaghat", "Haldia", "Raiganj", "Krishnanagar", "Nabadwip"
            ]
        },
        "US": {  # United States
            "California": [
                "Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento",
                "Long Beach", "Oakland", "Bakersfield", "Anaheim", "Santa Ana", "Riverside",
                "Stockton", "Irvine", "Chula Vista", "Fremont", "San Bernardino", "Modesto"
            ],
            "Texas": [
                "Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso",
                "Arlington", "Corpus Christi", "Plano", "Laredo", "Lubbock", "Garland",
                "Irving", "Amarillo", "Grand Prairie", "Brownsville", "McKinney", "Frisco"
            ],
            "New York": [
                "New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany",
                "New Rochelle", "Mount Vernon", "Schenectady", "Utica", "White Plains",
                "Hempstead", "Troy", "Niagara Falls", "Binghamton", "Freeport", "Valley Stream"
            ],
            "Florida": [
                "Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg", "Hialeah",
                "Tallahassee", "Fort Lauderdale", "Port St. Lucie", "Cape Coral", "Pembroke Pines",
                "Hollywood", "Miramar", "Gainesville", "Coral Springs", "Miami Gardens", "Clearwater"
            ]
        },
        "CA": {  # Canada
            "Ontario": [
                "Toronto", "Ottawa", "Mississauga", "Brampton", "Hamilton", "London",
                "Markham", "Vaughan", "Kitchener", "Windsor", "Richmond Hill", "Oakville",
                "Burlington", "Sudbury", "Oshawa", "Barrie", "St. Catharines", "Cambridge"
            ],
            "Quebec": [
                "Montreal", "Quebec City", "Laval", "Gatineau", "Longueuil", "Sherbrooke",
                "Saguenay", "Lévis", "Trois-Rivières", "Terrebonne", "Saint-Jean-sur-Richelieu",
                "Repentigny", "Brossard", "Drummondville", "Saint-Jérôme", "Granby"
            ],
            "British Columbia": [
                "Vancouver", "Surrey", "Burnaby", "Richmond", "Abbotsford", "Coquitlam",
                "Victoria", "Saanich", "Delta", "Kelowna", "Langley", "Kamloops",
                "Nanaimo", "Prince George", "Chilliwack", "New Westminster", "White Rock"
            ]
        },
        "AU": {  # Australia
            "New South Wales": [
                "Sydney", "Newcastle", "Wollongong", "Central Coast", "Maitland", "Albury",
                "Wagga Wagga", "Port Macquarie", "Tamworth", "Orange", "Dubbo", "Queanbeyan",
                "Bathurst", "Nowra", "Warrnambool", "Grafton", "Lismore", "Armidale"
            ],
            "Victoria": [
                "Melbourne", "Geelong", "Ballarat", "Bendigo", "Frankston", "Casey",
                "Monash", "Knox", "Whitehorse", "Moreland", "Hume", "Whittlesea",
                "Manningham", "Boroondara", "Port Phillip", "Stonnington", "Glen Eira"
            ],
            "Queensland": [
                "Brisbane", "Gold Coast", "Townsville", "Cairns", "Toowoomba", "Mackay",
                "Rockhampton", "Bundaberg", "Hervey Bay", "Gladstone", "Sunshine Coast",
                "Ipswich", "Logan", "Redland", "Moreton Bay", "Scenic Rim", "Somerset"
            ]
        },
        "DE": {  # Germany
            "Bavaria": [
                "Munich", "Nuremberg", "Augsburg", "Würzburg", "Regensburg", "Ingolstadt",
                "Fürth", "Erlangen", "Bayreuth", "Bamberg", "Aschaffenburg", "Landshut",
                "Passau", "Freising", "Rosenheim", "Neu-Ulm", "Schweinfurt", "Coburg"
            ],
            "North Rhine-Westphalia": [
                "Cologne", "Düsseldorf", "Dortmund", "Essen", "Duisburg", "Bochum",
                "Wuppertal", "Bielefeld", "Bonn", "Münster", "Mönchengladbach", "Gelsenkirchen",
                "Aachen", "Krefeld", "Oberhausen", "Hagen", "Hamm", "Mülheim an der Ruhr"
            ]
        },
        "BR": {  # Brazil
            "São Paulo": [
                "São Paulo", "Guarulhos", "Campinas", "São Bernardo do Campo", "Santo André",
                "Osasco", "Ribeirão Preto", "Sorocaba", "Santos", "Mauá", "São José dos Campos",
                "Mogi das Cruzes", "Diadema", "Jundiaí", "Piracicaba", "Carapicuíba", "Bauru"
            ],
            "Rio de Janeiro": [
                "Rio de Janeiro", "São Gonçalo", "Duque de Caxias", "Nova Iguaçu", "Niterói",
                "Campos dos Goytacazes", "Belford Roxo", "São João de Meriti", "Petrópolis",
                "Volta Redonda", "Magé", "Itaboraí", "Mesquita", "Nova Friburgo", "Barra Mansa"
            ]
        },
        "CN": {  # China
            "Guangdong": [
                "Guangzhou", "Shenzhen", "Dongguan", "Foshan", "Zhuhai", "Zhongshan",
                "Jiangmen", "Huizhou", "Zhaoqing", "Maoming", "Shaoguan", "Zhanjiang",
                "Yangjiang", "Meizhou", "Qingyuan", "Chaozhou", "Jieyang", "Yunfu"
            ],
            "Beijing": [
                "Dongcheng", "Xicheng", "Chaoyang", "Fengtai", "Shijingshan", "Haidian",
                "Mentougou", "Fangshan", "Tongzhou", "Shunyi", "Changping", "Daxing",
                "Huairou", "Pinggu", "Miyun", "Yanqing"
            ],
            "Shanghai": [
                "Huangpu", "Xuhui", "Changning", "Jing'an", "Putuo", "Hongkou",
                "Yangpu", "Minhang", "Baoshan", "Jiading", "Pudong", "Jinshan",
                "Songjiang", "Qingpu", "Fengxian", "Chongming"
            ]
        }
    }
    
    country_code = country_code.upper()
    country_data = cities_data.get(country_code, {})
    cities = country_data.get(state_name, [])
    
    if not cities:
        return StandardResponse(
            status=True,
            message="Cities data not available for this state",
            data={
                "cities": [],
                "message": "Major cities data not available for this state. You can add custom cities.",
                "allow_custom": True
            }
        )
    
    # Sort alphabetically and add "Other/Custom" option
    cities_sorted = sorted(cities)
    cities_sorted.append("Other (Please specify)")
    
    return StandardResponse(
        status=True,
        message="Cities retrieved successfully",
        data={
            "cities": cities_sorted,
            "allow_custom": True
        }
    )


@router.get("/masters/countries-states", response_model=StandardResponse)
async def get_country_state_masters():
    """Get comprehensive country and state/province masters for address - DEPRECATED
    
    This endpoint is deprecated. Use /masters/countries, /masters/states/{country_code}, 
    and /masters/cities/{country_code}/{state_name} for better performance.
    """

    return StandardResponse(
        status=False,
        message="This endpoint is deprecated. Use the new country, states, and cities endpoints for better performance.",
        data={"deprecated": True, "alternatives": [
            "/api/companies/masters/countries",
            "/api/companies/masters/states/{country_code}",
            "/api/companies/masters/cities/{country_code}/{state_name}"
        ]}
    )