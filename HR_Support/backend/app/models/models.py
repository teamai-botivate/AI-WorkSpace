"""
Botivate HR Support - SQLAlchemy ORM Models
Master database tables for company management.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, DateTime, ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from app.database import Base
import enum


# ── Helpers ───────────────────────────────────────────────

def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Enums ─────────────────────────────────────────────────

class DatabaseType(str, enum.Enum):
    GOOGLE_SHEETS = "google_sheets"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    SUPABASE = "supabase"
    EXCEL = "excel"


class PolicyType(str, enum.Enum):
    TEXT = "text"
    DOCUMENT = "document"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class RequestPriority(str, enum.Enum):
    NORMAL = "normal"
    URGENT = "urgent"


class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr"
    CEO = "ceo"
    ADMIN = "admin"


# ── Company ───────────────────────────────────────────────

class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    industry = Column(String(255), nullable=True)
    hr_name = Column(String(255), nullable=False)
    hr_email = Column(String(255), nullable=False)
    # OAuth 2.0 Credentials (replaces password)
    google_refresh_token = Column(String(512), nullable=True)
    google_access_token = Column(String(512), nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    support_email = Column(String(255), nullable=True)
    support_phone = Column(String(50), nullable=True)
    support_whatsapp = Column(String(50), nullable=True)
    support_message = Column(Text, nullable=True)
    login_link = Column(String(512), nullable=True)
    is_active = Column(Boolean, default=True)
    schema_map = Column(JSON, nullable=True)  # AI-analyzed schema
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    policies = relationship("Policy", back_populates="company", cascade="all, delete-orphan")
    databases = relationship("DatabaseConnection", back_populates="company", cascade="all, delete-orphan")
    approval_requests = relationship("ApprovalRequest", back_populates="company", cascade="all, delete-orphan")


# ── Policy ────────────────────────────────────────────────

class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, default=generate_uuid)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    policy_type = Column(SAEnum(PolicyType), nullable=False)
    content = Column(Text, nullable=True)         # For TEXT type
    file_path = Column(String(512), nullable=True) # For DOCUMENT type
    file_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company", back_populates="policies")


# ── Database Connection ───────────────────────────────────

class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(String, primary_key=True, default=generate_uuid)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    db_type = Column(SAEnum(DatabaseType), nullable=False)
    connection_config = Column(JSON, nullable=False)  # Dynamic config per DB type
    schema_map = Column(JSON, nullable=True)          # AI-analyzed schema for this connection
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company", back_populates="databases")


# ── Approval Request ─────────────────────────────────────

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String, primary_key=True, default=generate_uuid)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    employee_id = Column(String, nullable=False)       # Primary key from company sheet
    employee_name = Column(String(255), nullable=True)
    request_type = Column(String(100), nullable=False)  # leave, resignation, grievance, etc.
    request_details = Column(JSON, nullable=True)
    context = Column(Text, nullable=True)
    status = Column(SAEnum(RequestStatus), default=RequestStatus.PENDING)
    priority = Column(SAEnum(RequestPriority), default=RequestPriority.NORMAL)
    assigned_to_role = Column(SAEnum(UserRole), nullable=True)
    assigned_to_id = Column(String, nullable=True)
    decision_note = Column(Text, nullable=True)
    decided_by = Column(String, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    escalated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company = relationship("Company", back_populates="approval_requests")


# ── Notification ──────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False)
    target_employee_id = Column(String, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # approval_request, decision_update, reminder, etc.
    related_request_id = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
