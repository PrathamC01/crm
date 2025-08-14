"""
Master Data Models for CRM
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, Float, JSON, ForeignKey, Enum as SQLEnum, UniqueConstraint, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .base import BaseModel
import enum
import uuid
import random
import string

def generate_code(prefix: str, length: int = 16) -> str:
    """Generate alphanumeric code with prefix"""
    remaining_length = length - len(prefix)
    if remaining_length <= 0:
        remaining_length = 6
    
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(random.choices(characters, k=remaining_length))
    return f"{prefix}{random_part}"

# Enums
class ProductTypeEnum(str, enum.Enum):
    PRODUCT = "product"
    SERVICE = "service" 
    OTHER = "other"

class StatusEnum(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class AccessTypeEnum(str, enum.Enum):
    READ = "read"
    WRITE = "write"
    APPROVE = "approve"

class ApprovalStatusEnum(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"

class LeadStatusEnum(str, enum.Enum):
    NEW = "New"
    ACTIVE = "Active"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    UNQUALIFIED = "Unqualified"
    CONVERTED = "Converted"
    REJECTED = "Rejected"

class LeadSourceEnum(str, enum.Enum):
    REFERRAL = "Referral"
    DIRECT_MARKETING = "Direct Marketing"
    ADVERTISEMENT = "Advertisement"
    WEBSITE = "Website"
    COLD_CALLING = "Cold Calling"
    TRADE_SHOW = "Trade Show"
    SOCIAL_MEDIA = "Social Media"

class PriorityEnum(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

# Unit of Measure (UOM) Master
class UOMMaster(BaseModel):
    __tablename__ = "uom_master"
    
    uom_name = Column(String(100), nullable=False, unique=True)
    uom_code = Column(String(20), nullable=False, unique=True)
    description = Column(Text)
    base_unit = Column(String(50), nullable=True)
    conversion_factor_to_base = Column(Float, nullable=True)
    
    def __repr__(self):
        return f"<UOMMaster(name='{self.uom_name}', code='{self.uom_code}')>"

# Product Master
class ProductMaster(BaseModel):
    __tablename__ = "product_master"
    
    name = Column(String(200), nullable=False)
    cat1_type = Column(SQLEnum(ProductTypeEnum), nullable=False)
    cat2_category = Column(String(100), nullable=False)
    cat3_sub_category = Column(String(100), nullable=False)
    cat4_oem = Column(String(100), nullable=True)
    cat5_configuration = Column(JSON, nullable=True)
    sku_code = Column(String(16), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    uom_mappings = relationship("ProductUOMMap", back_populates="product")
    pricing_records = relationship("ProductPricingMaster", back_populates="product")
    groupings = relationship("ProductGroupingMaster", back_populates="product")
    calculations = relationship("ProductCalculationMaster", back_populates="product")
    
    @hybrid_property
    def auto_generated_name(self):
        """Auto-generate product name from categories"""
        parts = [self.cat2_category, self.cat3_sub_category]
        if self.cat4_oem:
            parts.append(self.cat4_oem)
        return " - ".join(parts)
    
    def generate_sku_code(self):
        """Generate 16-digit alphanumeric SKU code"""
        prefix = f"{self.cat1_type[:1].upper()}{self.cat2_category[:2].upper()}"
        self.sku_code = generate_code(prefix, 16)
    
    def __repr__(self):
        return f"<ProductMaster(name='{self.name}', sku='{self.sku_code}')>"

# Join table for Product-UOM mapping
class ProductUOMMap(BaseModel):
    __tablename__ = "product_uom_map"
    
    product_id = Column(Integer, ForeignKey('product_master.id'), nullable=False)
    uom_id = Column(Integer, ForeignKey('uom_master.id'), nullable=False)
    conversion_factor = Column(Float, nullable=True, comment="Optional conversion factor")
    is_primary = Column(Boolean, default=False, comment="Primary UOM for this product")
    
    # Relationships
    product = relationship("ProductMaster", back_populates="uom_mappings")
    uom = relationship("UOMMaster")
    
    __table_args__ = (
        UniqueConstraint('product_id', 'uom_id', name='unique_product_uom'),
    )

# Roles Master
class RolesMaster(BaseModel):
    __tablename__ = "roles_master"
    
    role_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    permissions = Column(JSON, comment="Array of permission IDs")
    
    # Relationships
    users = relationship("UserMaster", back_populates="role")

# Department Master
class DepartmentMaster(BaseModel):
    __tablename__ = "department_master"
    
    department_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Relationships
    users = relationship("UserMaster", back_populates="department")

# Designation Master
class DesignationMaster(BaseModel):
    __tablename__ = "designation_master"
    
    designation_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Relationships
    users = relationship("UserMaster", back_populates="designation")

# User Master (Enhanced)
class UserMaster(BaseModel):
    __tablename__ = "user_master"
    
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    role_id = Column(Integer, ForeignKey('roles_master.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('department_master.id'), nullable=False)
    designation_id = Column(Integer, ForeignKey('designation_master.id'), nullable=False)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.ACTIVE)
    
    # Relationships
    role = relationship("RolesMaster", back_populates="users")
    department = relationship("DepartmentMaster", back_populates="users")
    designation = relationship("DesignationMaster", back_populates="users")
    discount_settings = relationship("DiscountMaster", back_populates="user")

# Permission Master
class PermissionMaster(BaseModel):
    __tablename__ = "permission_master"
    
    permission_name = Column(String(100), nullable=False, unique=True)
    module = Column(String(50), nullable=False)
    access_type = Column(SQLEnum(AccessTypeEnum), nullable=False)
    description = Column(Text)
    
    __table_args__ = (
        UniqueConstraint('permission_name', 'module', 'access_type', name='unique_permission'),
    )

# Price List Master
class PriceListMaster(BaseModel):
    __tablename__ = "price_list_master"
    
    price_list_name = Column(String(200), nullable=False, unique=True)
    valid_upto = Column(Date, nullable=False)
    approval_status = Column(SQLEnum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(Date, nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    # Relationships
    product_pricing = relationship("ProductPricingMaster", back_populates="price_list")

# Product Pricing Master
class ProductPricingMaster(BaseModel):
    __tablename__ = "product_pricing_master"
    
    price_list_id = Column(Integer, ForeignKey('price_list_master.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product_master.id'), nullable=False)
    uom_id = Column(Integer, ForeignKey('uom_master.id'), nullable=True)
    group_id = Column(Integer, ForeignKey('group_master.id'), nullable=True)
    
    recurring_input_price = Column(Float, nullable=True)
    recurring_selling_price = Column(Float, nullable=True)
    otc_input_price = Column(Float, nullable=True)
    otc_selling_price = Column(Float, nullable=True)
    margin_percent = Column(Float, nullable=True)
    margin_value = Column(Float, nullable=True)
    discount_upto_percent = Column(Float, nullable=True)
    
    approval_status = Column(SQLEnum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(Date, nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    # Relationships
    price_list = relationship("PriceListMaster", back_populates="product_pricing")
    product = relationship("ProductMaster", back_populates="pricing_records")
    uom = relationship("UOMMaster")
    group = relationship("GroupMaster")
    
    __table_args__ = (
        UniqueConstraint('price_list_id', 'product_id', 'uom_id', name='unique_price_list_product_uom'),
    )

# Group Master
class GroupMaster(BaseModel):
    __tablename__ = "group_master"
    
    group_name = Column(String(200), nullable=False, unique=True)
    group_code = Column(String(16), unique=True, nullable=False)
    product_grouping_id = Column(Integer, ForeignKey('product_grouping_master.id'), nullable=True)
    default_percent_per_product = Column(Float, nullable=False)
    
    approval_status = Column(SQLEnum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(Date, nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    # Relationships
    product_grouping = relationship("ProductGroupingMaster", foreign_keys=[product_grouping_id])
    
    def generate_group_code(self, product_sku: str):
        """Generate group code from product SKU"""
        prefix = "GRP"
        self.group_code = generate_code(prefix, 16)

# Product Grouping Master
class ProductGroupingMaster(BaseModel):
    __tablename__ = "product_grouping_master"
    
    product_id = Column(Integer, ForeignKey('product_master.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('group_master.id'), nullable=False)
    discount = Column(Float, nullable=False)
    
    approval_status = Column(SQLEnum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(Date, nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    # Relationships
    product = relationship("ProductMaster", back_populates="groupings")
    group = relationship("GroupMaster", foreign_keys=[group_id])
    
    __table_args__ = (
        UniqueConstraint('product_id', 'group_id', name='unique_product_group'),
    )

# Tax Master
class TaxMaster(BaseModel):
    __tablename__ = "tax_master"
    
    tax_name = Column(String(100), nullable=False)
    tax_code = Column(String(20), nullable=False)
    financial_year = Column(String(20), nullable=False)
    tax_rate = Column(Float, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('tax_code', 'financial_year', name='unique_tax_financial_year'),
    )

# Discount Master
class DiscountMaster(BaseModel):
    __tablename__ = "discount_master"
    
    user_id = Column(Integer, ForeignKey('user_master.id'), nullable=False)
    discount_threshold = Column(Float, nullable=False, comment="Max allowed % discount per user")
    
    # Relationships
    user = relationship("UserMaster", back_populates="discount_settings")

# Product Calculation Master
class ProductCalculationMaster(BaseModel):
    __tablename__ = "product_calculation_master"
    
    product_id = Column(Integer, ForeignKey('product_master.id'), nullable=False)
    formula = Column(Text, nullable=False, comment="Formula for calculating product quantities/prices")
    
    approval_status = Column(SQLEnum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(Date, nullable=True)
    rejection_reason = Column(String(500), nullable=True)
    
    # Relationships
    product = relationship("ProductMaster", back_populates="calculations")

# State Master
class StateMaster(BaseModel):
    __tablename__ = "state_master"
    
    state_name = Column(String(100), nullable=False, unique=True)
    state_code = Column(String(10), nullable=False, unique=True)
    
    # Relationships
    cities = relationship("CityMaster", back_populates="state")

# City Master
class CityMaster(BaseModel):
    __tablename__ = "city_master"
    
    city_name = Column(String(100), nullable=False)
    state_id = Column(Integer, ForeignKey('state_master.id'), nullable=False)
    
    # Relationships
    state = relationship("StateMaster", back_populates="cities")
    
    __table_args__ = (
        UniqueConstraint('city_name', 'state_id', name='unique_city_state'),
    )

# Industry Category Master
class IndustryCategoryMaster(BaseModel):
    __tablename__ = "industry_category_master"
    
    industry_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)