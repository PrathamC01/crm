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
    """Get comprehensive country and state/province masters for address"""

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
            "Delhi (NCT)",
            "Chandigarh",
            "Puducherry",
            "Jammu and Kashmir",
            "Andaman and Nicobar Islands",
            "Lakshadweep",
            "Dadra and Nagar Haveli and Daman and Diu"
        ],
        "United States": [
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
        "United Kingdom": [
            "England", "Scotland", "Wales", "Northern Ireland"
        ],
        "Canada": [
            "Alberta", "British Columbia", "Manitoba", "New Brunswick",
            "Newfoundland and Labrador", "Northwest Territories", "Nova Scotia",
            "Nunavut", "Ontario", "Prince Edward Island", "Quebec",
            "Saskatchewan", "Yukon"
        ],
        "Australia": [
            "New South Wales", "Victoria", "Queensland", "Western Australia",
            "South Australia", "Tasmania", "Northern Territory",
            "Australian Capital Territory"
        ],
        "Germany": [
            "Baden-Württemberg", "Bavaria", "Berlin", "Brandenburg", "Bremen",
            "Hamburg", "Hesse", "Lower Saxony", "Mecklenburg-Vorpommern",
            "North Rhine-Westphalia", "Rhineland-Palatinate", "Saarland",
            "Saxony", "Saxony-Anhalt", "Schleswig-Holstein", "Thuringia"
        ],
        "France": [
            "Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Brittany",
            "Centre-Val de Loire", "Corsica", "Grand Est", "Hauts-de-France",
            "Île-de-France", "Normandy", "Nouvelle-Aquitaine", "Occitanie",
            "Pays de la Loire", "Provence-Alpes-Côte d'Azur"
        ],
        "Italy": [
            "Abruzzo", "Basilicata", "Calabria", "Campania", "Emilia-Romagna",
            "Friuli-Venezia Giulia", "Lazio", "Liguria", "Lombardy", "Marche",
            "Molise", "Piedmont", "Apulia", "Sardinia", "Sicily", "Tuscany",
            "Trentino-Alto Adige", "Umbria", "Aosta Valley", "Veneto"
        ],
        "Spain": [
            "Andalusia", "Aragon", "Asturias", "Balearic Islands", "Basque Country",
            "Canary Islands", "Cantabria", "Castile and León", "Castile-La Mancha",
            "Catalonia", "Extremadura", "Galicia", "La Rioja", "Community of Madrid",
            "Region of Murcia", "Navarre", "Valencian Community", "Ceuta", "Melilla"
        ],
        "Netherlands": [
            "Drenthe", "Flevoland", "Friesland", "Gelderland", "Groningen",
            "Limburg", "North Brabant", "North Holland", "Overijssel",
            "South Holland", "Utrecht", "Zeeland"
        ],
        "Brazil": [
            "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará",
            "Distrito Federal", "Espírito Santo", "Goiás", "Maranhão",
            "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará",
            "Paraíba", "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro",
            "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia",
            "Roraima", "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"
        ],
        "China": [
            "Anhui", "Beijing", "Chongqing", "Fujian", "Gansu", "Guangdong",
            "Guangxi", "Guizhou", "Hainan", "Hebei", "Heilongjiang", "Henan",
            "Hubei", "Hunan", "Inner Mongolia", "Jiangsu", "Jiangxi", "Jilin",
            "Liaoning", "Ningxia", "Qinghai", "Shaanxi", "Shandong", "Shanghai",
            "Shanxi", "Sichuan", "Tianjin", "Tibet", "Xinjiang", "Yunnan", "Zhejiang"
        ],
        "Japan": [
            "Aichi", "Akita", "Aomori", "Chiba", "Ehime", "Fukui", "Fukuoka",
            "Fukushima", "Gifu", "Gunma", "Hiroshima", "Hokkaido", "Hyogo",
            "Ibaraki", "Ishikawa", "Iwate", "Kagawa", "Kagoshima", "Kanagawa",
            "Kochi", "Kumamoto", "Kyoto", "Mie", "Miyagi", "Miyazaki", "Nagano",
            "Nagasaki", "Nara", "Niigata", "Oita", "Okayama", "Okinawa", "Osaka",
            "Saga", "Saitama", "Shiga", "Shimane", "Shizuoka", "Tochigi", "Tokushima",
            "Tokyo", "Tottori", "Toyama", "Wakayama", "Yamagata", "Yamaguchi", "Yamanashi"
        ],
        "South Korea": [
            "Busan", "Chungcheongbuk-do", "Chungcheongnam-do", "Daegu", "Daejeon",
            "Gangwon-do", "Gwangju", "Gyeonggi-do", "Gyeongsangbuk-do",
            "Gyeongsangnam-do", "Incheon", "Jeju-do", "Jeollabuk-do",
            "Jeollanam-do", "Sejong", "Seoul", "Ulsan"
        ],
        "Mexico": [
            "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
            "Chiapas", "Chihuahua", "Coahuila", "Colima", "Durango", "Guanajuato",
            "Guerrero", "Hidalgo", "Jalisco", "Mexico", "Michoacán", "Morelos",
            "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", "Quintana Roo",
            "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas",
            "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas", "Mexico City"
        ],
        "Russia": [
            "Adygea", "Altai Krai", "Altai Republic", "Amur Oblast", "Arkhangelsk Oblast",
            "Astrakhan Oblast", "Bashkortostan", "Belgorod Oblast", "Bryansk Oblast",
            "Buryatia", "Chechen Republic", "Chelyabinsk Oblast", "Chukotka",
            "Chuvash Republic", "Dagestan", "Ingushetia", "Irkutsk Oblast",
            "Ivanovo Oblast", "Jewish Autonomous Oblast", "Kabardino-Balkaria",
            "Kaliningrad Oblast", "Kalmykia", "Kaluga Oblast", "Kamchatka Krai",
            "Karachay-Cherkessia", "Karelia", "Kemerovo Oblast", "Khabarovsk Krai",
            "Khakassia", "Khanty-Mansi", "Kirov Oblast", "Komi Republic",
            "Kostroma Oblast", "Krasnodar Krai", "Krasnoyarsk Krai", "Kurgan Oblast",
            "Kursk Oblast", "Leningrad Oblast", "Lipetsk Oblast", "Magadan Oblast",
            "Mari El", "Mordovia", "Moscow", "Moscow Oblast", "Murmansk Oblast",
            "Nenets", "Nizhny Novgorod Oblast", "North Ossetia-Alania",
            "Novgorod Oblast", "Novosibirsk Oblast", "Omsk Oblast", "Orenburg Oblast",
            "Oryol Oblast", "Penza Oblast", "Perm Krai", "Primorsky Krai",
            "Pskov Oblast", "Rostov Oblast", "Ryazan Oblast", "Saint Petersburg",
            "Sakha Republic", "Sakhalin Oblast", "Samara Oblast", "Saratov Oblast",
            "Smolensk Oblast", "Stavropol Krai", "Sverdlovsk Oblast",
            "Tambov Oblast", "Tatarstan", "Tomsk Oblast", "Tula Oblast",
            "Tuva Republic", "Tver Oblast", "Tyumen Oblast", "Udmurt Republic",
            "Ulyanovsk Oblast", "Vladimir Oblast", "Volgograd Oblast",
            "Vologda Oblast", "Voronezh Oblast", "Yamalo-Nenets", "Yaroslavl Oblast",
            "Zabaykalsky Krai"
        ],
        "Argentina": [
            "Buenos Aires", "Catamarca", "Chaco", "Chubut", "Córdoba", "Corrientes",
            "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja", "Mendoza",
            "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan", "San Luis",
            "Santa Cruz", "Santa Fe", "Santiago del Estero", "Tierra del Fuego",
            "Tucumán"
        ],
        "South Africa": [
            "Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo",
            "Mpumalanga", "Northern Cape", "North West", "Western Cape"
        ],
        "Nigeria": [
            "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
            "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
            "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina", "Kebbi", "Kogi",
            "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo",
            "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara", "FCT Abuja"
        ],
        "Egypt": [
            "Alexandria", "Aswan", "Asyut", "Beheira", "Beni Suef", "Cairo",
            "Dakahlia", "Damietta", "Fayyum", "Gharbia", "Giza", "Ismailia",
            "Kafr el-Sheikh", "Luxor", "Matrouh", "Minya", "Monufia", "New Valley",
            "North Sinai", "Port Said", "Qalyubia", "Qena", "Red Sea", "Sharqia",
            "Sohag", "South Sinai", "Suez"
        ],
        "Turkey": [
            "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya",
            "Ankara", "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir",
            "Bartın", "Batman", "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu",
            "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
            "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum",
            "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkâri", "Hatay",
            "Iğdır", "Isparta", "Istanbul", "İzmir", "Kahramanmaraş", "Karabük",
            "Karaman", "Kars", "Kastamonu", "Kayseri", "Kırıkkale", "Kırklareli",
            "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa",
            "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu",
            "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas",
            "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli",
            "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
        ],
        "Indonesia": [
            "Aceh", "North Sumatra", "West Sumatra", "Riau", "Riau Islands",
            "Jambi", "South Sumatra", "Bangka Belitung Islands", "Bengkulu",
            "Lampung", "Jakarta", "West Java", "Banten", "Central Java",
            "Yogyakarta", "East Java", "Bali", "West Nusa Tenggara",
            "East Nusa Tenggara", "West Kalimantan", "Central Kalimantan",
            "South Kalimantan", "East Kalimantan", "North Kalimantan",
            "North Sulawesi", "Central Sulawesi", "South Sulawesi",
            "Southeast Sulawesi", "Gorontalo", "West Sulawesi", "Maluku",
            "North Maluku", "Papua", "West Papua"
        ],
        "Thailand": [
            "Amnat Charoen", "Ang Thong", "Bangkok", "Bueng Kan", "Buri Ram",
            "Chachoengsao", "Chai Nat", "Chaiyaphum", "Chanthaburi", "Chiang Mai",
            "Chiang Rai", "Chon Buri", "Chumphon", "Kalasin", "Kamphaeng Phet",
            "Kanchanaburi", "Khon Kaen", "Krabi", "Lampang", "Lamphun", "Loei",
            "Lop Buri", "Mae Hong Son", "Maha Sarakham", "Mukdahan", "Nakhon Nayok",
            "Nakhon Pathom", "Nakhon Phanom", "Nakhon Ratchasima", "Nakhon Sawan",
            "Nakhon Si Thammarat", "Nan", "Narathiwat", "Nong Bua Lam Phu",
            "Nong Khai", "Nonthaburi", "Pathum Thani", "Pattani", "Phang Nga",
            "Phatthalung", "Phayao", "Phetchabun", "Phetchaburi", "Phichit",
            "Phitsanulok", "Phra Nakhon Si Ayutthaya", "Phrae", "Phuket",
            "Prachin Buri", "Prachuap Khiri Khan", "Ranong", "Ratchaburi",
            "Rayong", "Roi Et", "Sa Kaeo", "Sakon Nakhon", "Samut Prakan",
            "Samut Sakhon", "Samut Songkhram", "Saraburi", "Satun", "Sing Buri",
            "Sisaket", "Songkhla", "Sukhothai", "Suphan Buri", "Surat Thani",
            "Surin", "Tak", "Trang", "Trat", "Ubon Ratchathani", "Udon Thani",
            "Uthai Thani", "Uttaradit", "Yala", "Yasothon"
        ],
        "Malaysia": [
            "Johor", "Kedah", "Kelantan", "Malacca", "Negeri Sembilan", "Pahang",
            "Penang", "Perak", "Perlis", "Sabah", "Sarawak", "Selangor",
            "Terengganu", "Federal Territory of Kuala Lumpur",
            "Federal Territory of Labuan", "Federal Territory of Putrajaya"
        ],
        "Philippines": [
            "Abra", "Agusan del Norte", "Agusan del Sur", "Aklan", "Albay",
            "Antique", "Apayao", "Aurora", "Basilan", "Bataan", "Batanes",
            "Batangas", "Benguet", "Biliran", "Bohol", "Bukidnon", "Bulacan",
            "Cagayan", "Camarines Norte", "Camarines Sur", "Camiguin", "Capiz",
            "Catanduanes", "Cavite", "Cebu", "Compostela Valley", "Cotabato",
            "Davao del Norte", "Davao del Sur", "Davao Occidental", "Davao Oriental",
            "Dinagat Islands", "Eastern Samar", "Guimaras", "Ifugao", "Ilocos Norte",
            "Ilocos Sur", "Iloilo", "Isabela", "Kalinga", "La Union", "Laguna",
            "Lanao del Norte", "Lanao del Sur", "Leyte", "Maguindanao", "Marinduque",
            "Masbate", "Metro Manila", "Misamis Occidental", "Misamis Oriental",
            "Mountain Province", "Negros Occidental", "Negros Oriental",
            "Northern Samar", "Nueva Ecija", "Nueva Vizcaya", "Occidental Mindoro",
            "Oriental Mindoro", "Palawan", "Pampanga", "Pangasinan", "Quezon",
            "Quirino", "Rizal", "Romblon", "Samar", "Sarangani", "Siquijor",
            "Sorsogon", "South Cotabato", "Southern Leyte", "Sultan Kudarat",
            "Sulu", "Surigao del Norte", "Surigao del Sur", "Tarlac", "Tawi-Tawi",
            "Zambales", "Zamboanga del Norte", "Zamboanga del Sur", "Zamboanga Sibugay"
        ],
        "Vietnam": [
            "An Giang", "Bà Rịa–Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu",
            "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước",
            "Bình Thuận", "Cà Mau", "Cao Bằng", "Đắk Lắk", "Đắk Nông", "Điện Biên",
            "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Tĩnh",
            "Hải Dương", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa",
            "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai",
            "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ",
            "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh",
            "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình",
            "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh",
            "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái", "Hanoi",
            "Ho Chi Minh City", "Haiphong", "Da Nang", "Can Tho"
        ],
        "Bangladesh": [
            "Barisal", "Chittagong", "Dhaka", "Khulna", "Mymensingh",
            "Rajshahi", "Rangpur", "Sylhet"
        ],
        "Pakistan": [
            "Balochistan", "Khyber Pakhtunkhwa", "Punjab", "Sindh",
            "Islamabad Capital Territory", "Azad Kashmir", "Gilgit-Baltistan"
        ],
        "Sri Lanka": [
            "Central Province", "Eastern Province", "North Central Province",
            "North Western Province", "Northern Province", "Sabaragamuwa Province",
            "Southern Province", "Uva Province", "Western Province"
        ],
        "Other": [
            "Not Listed / Other"
        ]
    }

    return StandardResponse(
        status=True,
        message="Country-state masters retrieved successfully",
        data=country_state_data,
    )