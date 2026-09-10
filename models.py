from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

# ============================================================
# ENUMS
# ============================================================

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    LEGAL = "legal"
    VIEWER = "viewer"

class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ContractType(str, enum.Enum):
    EMPLOYMENT = "employment"
    NDA = "nda"
    SALES = "sales"
    PURCHASE = "purchase"
    LEASE = "lease"
    SERVICE = "service"
    LICENSE = "license"
    OTHER = "other"

# ============================================================
# USER MODEL
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    contracts = relationship("Contract", back_populates="uploader", cascade="all, delete-orphan")
    approvals_requested = relationship("Approval", foreign_keys="Approval.requested_by", back_populates="requester")
    approvals_done = relationship("Approval", foreign_keys="Approval.approved_by", back_populates="approver")
    audit_logs = relationship("AuditLog", back_populates="user")

# ============================================================
# CONTRACT MODEL
# ============================================================

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    contract_type = Column(Enum(ContractType), default=ContractType.OTHER)
    
    # File
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    clauses = Column(JSON, nullable=True)
    meta_data = Column(JSON, nullable=True)  # ✅ metadata → meta_data
    tags = Column(JSON, nullable=True)

    # Status & Version
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT)
    current_version = Column(Integer, default=1)
    
    # Dates
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    signing_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # Financial
    amount = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    
    # Parties
    party_a = Column(String(255), nullable=True)
    party_b = Column(String(255), nullable=True)
    party_a_contact = Column(String(255), nullable=True)
    party_b_contact = Column(String(255), nullable=True)
    
    # Audit
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)

    # Relationships
    uploader = relationship("User", back_populates="contracts")
    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="contract", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="contract")

# ============================================================
# CONTRACT VERSION MODEL
# ============================================================

class ContractVersion(Base):
    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=True)
    clauses = Column(JSON, nullable=True)
    change_summary = Column(Text, nullable=True)
    modified_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())

    contract = relationship("Contract", back_populates="versions")

# ============================================================
# APPROVAL MODEL
# ============================================================

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    version_id = Column(Integer, ForeignKey("contract_versions.id"))
    requested_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    contract = relationship("Contract", back_populates="approvals")
    requester = relationship("User", foreign_keys=[requested_by], back_populates="approvals_requested")
    approver = relationship("User", foreign_keys=[approved_by], back_populates="approvals_done")

# ============================================================
# AUDIT LOG MODEL
# ============================================================

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
    contract = relationship("Contract", back_populates="audit_logs")