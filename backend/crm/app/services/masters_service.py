"""
Masters Service - Business logic for master data operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import Depends

from ..database.base import get_db
from ..models.masters import (
    ProductMaster, UOMMaster, ProductUOMMap, PriceListMaster, 
    ProductPricingMaster, GroupMaster, ProductGroupingMaster,
    UserMaster, RolesMaster, DepartmentMaster, DesignationMaster,
    StateMaster, CityMaster, IndustryCategoryMaster, TaxMaster,
    PermissionMaster, DiscountMaster, ProductCalculationMaster,
    ApprovalStatusEnum
)
from ..schemas.masters import (
    ProductMasterCreate, ProductMasterUpdate, UOMCreate,
    PriceListCreate, ProductPricingCreate, UserMasterCreate,
    UserMasterUpdate, PaginatedResponse, BaseFilter, ApprovalRequest
)

class MastersService:
    def __init__(self, db: Session):
        self.db = db
    
    # Product Master operations
    async def get_products(self, filters: BaseFilter, cat1_type: Optional[str] = None, cat2_category: Optional[str] = None):
        """Get paginated products with filters"""
        query = self.db.query(ProductMaster).filter(ProductMaster.is_active == filters.is_active)
        
        # Apply filters
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    ProductMaster.name.ilike(search_term),
                    ProductMaster.sku_code.ilike(search_term),
                    ProductMaster.cat2_category.ilike(search_term)
                )
            )
        
        if cat1_type:
            query = query.filter(ProductMaster.cat1_type == cat1_type)
        
        if cat2_category:
            query = query.filter(ProductMaster.cat2_category.ilike(f"%{cat2_category}%"))
        
        # Apply sorting
        if hasattr(ProductMaster, filters.sort_by):
            order_by = getattr(ProductMaster, filters.sort_by)
            if filters.sort_order == "desc":
                order_by = order_by.desc()
            query = query.order_by(order_by)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        products = query.offset((filters.page - 1) * filters.per_page).limit(filters.per_page).all()
        
        return PaginatedResponse(
            items=[self._product_to_dict(p) for p in products],
            total=total,
            page=filters.page,
            per_page=filters.per_page,
            pages=(total + filters.per_page - 1) // filters.per_page
        )
    
    async def create_product(self, product_data: ProductMasterCreate, created_by: int):
        """Create new product"""
        # Auto-generate name if not provided
        if not product_data.name:
            name_parts = [product_data.cat2_category, product_data.cat3_sub_category]
            if product_data.cat4_oem:
                name_parts.append(product_data.cat4_oem)
            product_data.name = " - ".join(name_parts)
        
        product = ProductMaster(
            name=product_data.name,
            cat1_type=product_data.cat1_type,
            cat2_category=product_data.cat2_category,
            cat3_sub_category=product_data.cat3_sub_category,
            cat4_oem=product_data.cat4_oem,
            cat5_configuration=product_data.cat5_configuration,
            description=product_data.description,
            created_by=created_by
        )
        
        # Generate SKU code
        product.generate_sku_code()
        
        self.db.add(product)
        self.db.flush()  # Get the ID
        
        # Add UOM mappings
        for i, uom_id in enumerate(product_data.uom_ids):
            uom_map = ProductUOMMap(
                product_id=product.id,
                uom_id=uom_id,
                is_primary=(i == 0)  # First UOM is primary
            )
            self.db.add(uom_map)
        
        self.db.commit()
        self.db.refresh(product)
        
        return self._product_to_dict(product)
    
    async def get_product_by_id(self, product_id: int):
        """Get product by ID"""
        product = self.db.query(ProductMaster).filter(ProductMaster.id == product_id).first()
        if product:
            return self._product_to_dict(product)
        return None
    
    async def update_product(self, product_id: int, product_data: ProductMasterUpdate, updated_by: int):
        """Update product"""
        product = self.db.query(ProductMaster).filter(ProductMaster.id == product_id).first()
        if not product:
            return None
        
        # Update fields
        for field, value in product_data.dict(exclude_unset=True).items():
            if field != "uom_ids":
                setattr(product, field, value)
        
        product.updated_by = updated_by
        
        # Update UOM mappings if provided
        if product_data.uom_ids is not None:
            # Remove existing mappings
            self.db.query(ProductUOMMap).filter(ProductUOMMap.product_id == product_id).delete()
            
            # Add new mappings
            for i, uom_id in enumerate(product_data.uom_ids):
                uom_map = ProductUOMMap(
                    product_id=product.id,
                    uom_id=uom_id,
                    is_primary=(i == 0)
                )
                self.db.add(uom_map)
        
        self.db.commit()
        self.db.refresh(product)
        
        return self._product_to_dict(product)
    
    # UOM operations
    async def get_uoms(self, filters: BaseFilter):
        """Get paginated UOMs"""
        query = self.db.query(UOMMaster).filter(UOMMaster.is_active == filters.is_active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    UOMMaster.uom_name.ilike(search_term),
                    UOMMaster.uom_code.ilike(search_term)
                )
            )
        
        total = query.count()
        uoms = query.offset((filters.page - 1) * filters.per_page).limit(filters.per_page).all()
        
        return PaginatedResponse(
            items=[self._uom_to_dict(u) for u in uoms],
            total=total,
            page=filters.page,
            per_page=filters.per_page,
            pages=(total + filters.per_page - 1) // filters.per_page
        )
    
    async def create_uom(self, uom_data: UOMCreate, created_by: int):
        """Create new UOM"""
        uom = UOMMaster(**uom_data.dict(), created_by=created_by)
        self.db.add(uom)
        self.db.commit()
        self.db.refresh(uom)
        return self._uom_to_dict(uom)
    
    # Price List operations
    async def get_price_lists(self, filters: BaseFilter):
        """Get paginated price lists"""
        query = self.db.query(PriceListMaster).filter(PriceListMaster.is_active == filters.is_active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(PriceListMaster.price_list_name.ilike(search_term))
        
        total = query.count()
        price_lists = query.offset((filters.page - 1) * filters.per_page).limit(filters.per_page).all()
        
        return PaginatedResponse(
            items=[self._price_list_to_dict(pl) for pl in price_lists],
            total=total,
            page=filters.page,
            per_page=filters.per_page,
            pages=(total + filters.per_page - 1) // filters.per_page
        )
    
    async def create_price_list(self, price_list_data: PriceListCreate, created_by: int):
        """Create new price list"""
        price_list = PriceListMaster(**price_list_data.dict(), created_by=created_by)
        self.db.add(price_list)
        self.db.commit()
        self.db.refresh(price_list)
        return self._price_list_to_dict(price_list)
    
    async def approve_price_list(self, price_list_id: int, approval_data: ApprovalRequest, approved_by: int):
        """Approve or reject price list"""
        price_list = self.db.query(PriceListMaster).filter(PriceListMaster.id == price_list_id).first()
        if not price_list:
            return None
        
        if approval_data.decision == "approved":
            price_list.approval_status = ApprovalStatusEnum.APPROVED
            price_list.approved_by = approved_by
            price_list.approved_at = datetime.utcnow().date()
        else:
            price_list.approval_status = ApprovalStatusEnum.REJECTED
            price_list.rejection_reason = approval_data.comments
        
        self.db.commit()
        return self._price_list_to_dict(price_list)
    
    # Product Pricing operations
    async def get_product_pricing(self, product_id: int, price_list_id: Optional[int] = None, uom_id: Optional[int] = None):
        """Get product pricing"""
        query = self.db.query(ProductPricingMaster).filter(ProductPricingMaster.product_id == product_id)
        
        if price_list_id:
            query = query.filter(ProductPricingMaster.price_list_id == price_list_id)
        if uom_id:
            query = query.filter(ProductPricingMaster.uom_id == uom_id)
        
        pricing_records = query.all()
        return [self._product_pricing_to_dict(pr) for pr in pricing_records]
    
    async def create_product_pricing(self, product_id: int, pricing_data: ProductPricingCreate, created_by: int):
        """Create product pricing"""
        pricing = ProductPricingMaster(
            product_id=product_id,
            **pricing_data.dict(),
            created_by=created_by
        )
        self.db.add(pricing)
        self.db.commit()
        self.db.refresh(pricing)
        return self._product_pricing_to_dict(pricing)
    
    # User Management operations
    async def get_users(self, filters: BaseFilter, department_id: Optional[int] = None, role_id: Optional[int] = None):
        """Get paginated users"""
        query = self.db.query(UserMaster).filter(UserMaster.is_active == filters.is_active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    UserMaster.name.ilike(search_term),
                    UserMaster.email.ilike(search_term)
                )
            )
        
        if department_id:
            query = query.filter(UserMaster.department_id == department_id)
        if role_id:
            query = query.filter(UserMaster.role_id == role_id)
        
        total = query.count()
        users = query.offset((filters.page - 1) * filters.per_page).limit(filters.per_page).all()
        
        return PaginatedResponse(
            items=[self._user_to_dict(u) for u in users],
            total=total,
            page=filters.page,
            per_page=filters.per_page,
            pages=(total + filters.per_page - 1) // filters.per_page
        )
    
    async def create_user(self, user_data: UserMasterCreate, created_by: int):
        """Create new user"""
        user = UserMaster(**user_data.dict(), created_by=created_by)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._user_to_dict(user)
    
    # Lookup operations
    async def get_all_departments(self):
        """Get all departments for dropdowns"""
        departments = self.db.query(DepartmentMaster).filter(DepartmentMaster.is_active == True).all()
        return [{"id": d.id, "department_name": d.department_name, "description": d.description} for d in departments]
    
    async def get_all_roles(self):
        """Get all roles for dropdowns"""
        roles = self.db.query(RolesMaster).filter(RolesMaster.is_active == True).all()
        return [{"id": r.id, "role_name": r.role_name, "description": r.description, "permissions": r.permissions} for r in roles]
    
    # Helper methods
    def _product_to_dict(self, product: ProductMaster) -> dict:
        """Convert product model to dict"""
        uoms = []
        for uom_map in product.uom_mappings:
            uoms.append({
                "uom_id": uom_map.uom_id,
                "uom_name": uom_map.uom.uom_name,
                "uom_code": uom_map.uom.uom_code,
                "conversion_factor": uom_map.conversion_factor,
                "is_primary": uom_map.is_primary
            })
        
        return {
            "id": product.id,
            "name": product.name,
            "cat1_type": product.cat1_type.value if product.cat1_type else None,
            "cat2_category": product.cat2_category,
            "cat3_sub_category": product.cat3_sub_category,
            "cat4_oem": product.cat4_oem,
            "cat5_configuration": product.cat5_configuration,
            "sku_code": product.sku_code,
            "description": product.description,
            "created_at": product.created_at,
            "updated_at": product.updated_at,
            "is_active": product.is_active,
            "uoms": uoms
        }
    
    def _uom_to_dict(self, uom: UOMMaster) -> dict:
        """Convert UOM model to dict"""
        return {
            "id": uom.id,
            "uom_name": uom.uom_name,
            "uom_code": uom.uom_code,
            "description": uom.description,
            "base_unit": uom.base_unit,
            "conversion_factor_to_base": uom.conversion_factor_to_base,
            "created_at": uom.created_at,
            "updated_at": uom.updated_at,
            "is_active": uom.is_active
        }
    
    def _price_list_to_dict(self, price_list: PriceListMaster) -> dict:
        """Convert price list model to dict"""
        return {
            "id": price_list.id,
            "price_list_name": price_list.price_list_name,
            "valid_upto": price_list.valid_upto,
            "approval_status": price_list.approval_status.value if price_list.approval_status else None,
            "approved_by": price_list.approved_by,
            "approved_at": price_list.approved_at,
            "created_at": price_list.created_at,
            "updated_at": price_list.updated_at,
            "is_active": price_list.is_active
        }
    
    def _product_pricing_to_dict(self, pricing: ProductPricingMaster) -> dict:
        """Convert product pricing model to dict"""
        return {
            "id": pricing.id,
            "price_list_id": pricing.price_list_id,
            "product_id": pricing.product_id,
            "uom_id": pricing.uom_id,
            "group_id": pricing.group_id,
            "recurring_input_price": pricing.recurring_input_price,
            "recurring_selling_price": pricing.recurring_selling_price,
            "otc_input_price": pricing.otc_input_price,
            "otc_selling_price": pricing.otc_selling_price,
            "margin_percent": pricing.margin_percent,
            "margin_value": pricing.margin_value,
            "discount_upto_percent": pricing.discount_upto_percent,
            "approval_status": pricing.approval_status.value if pricing.approval_status else None,
            "approved_by": pricing.approved_by,
            "created_at": pricing.created_at,
            "updated_at": pricing.updated_at,
            "is_active": pricing.is_active
        }
    
    def _user_to_dict(self, user: UserMaster) -> dict:
        """Convert user model to dict"""
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role_id": user.role_id,
            "role_name": user.role.role_name if user.role else None,
            "department_id": user.department_id,
            "department_name": user.department.department_name if user.department else None,
            "designation_id": user.designation_id,
            "designation_name": user.designation.designation_name if user.designation else None,
            "status": user.status.value if user.status else None,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active
        }


def get_masters_service(db: Session = Depends(get_db)) -> MastersService:
    """Dependency to get masters service"""
    return MastersService(db)