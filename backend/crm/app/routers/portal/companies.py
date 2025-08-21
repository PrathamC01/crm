"""
Enhanced Company Management API endpoints for Swayatta 4.0 - Simplified without approval workflow
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
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
from ...database import get_db
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
async def get_countries_master(db: Session = Depends(get_db)):
    """Get all countries from database"""
    try:
        countries = GeographicService.get_all_countries(db)
        return StandardResponse(
            status=True,
            message="Countries retrieved successfully",
            data=countries
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve countries")


@router.get("/masters/states/{country_code}", response_model=StandardResponse)
async def get_states_by_country(country_code: str, db: Session = Depends(get_db)):
    """Get states/provinces for a specific country by ISO code"""
    try:
        # Find country by code
        country = db.query(Country).filter(Country.code == country_code.upper()).first()
        if not country:
            return StandardResponse(
                status=False,
                message=f"Country with code {country_code} not found",
                data=[]
            )
        
        states = GeographicService.get_states_by_country(db, country.id)
        return StandardResponse(
            status=True,
            message="States retrieved successfully",
            data=states
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve states")


@router.get("/masters/cities/{country_code}/{state_name}", response_model=StandardResponse)
async def get_cities_by_state(country_code: str, state_name: str, db: Session = Depends(get_db)):
    """Get cities for a specific state/province"""
    try:
        cities = GeographicService.get_cities_by_state_name(db, country_code, state_name)
        
        return StandardResponse(
            status=True,
            message="Cities retrieved successfully",
            data={
                "cities": [city["name"] for city in cities],
                "allow_custom": True
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve cities")
    
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