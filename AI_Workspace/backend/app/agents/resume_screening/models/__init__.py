"""
Resume Screening — Database Models

SQLAlchemy ORM models for resume screening, JD storage, and candidate tracking.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from ....core.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    experience_required = Column(String(100), nullable=True)
    skills = Column(JSON, nullable=True)  # List of required skills
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    candidates = relationship("Candidate", back_populates="job", cascade="all, delete-orphan")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    resume_path = Column(String(500), nullable=True)
    resume_text = Column(Text, nullable=True)

    # Scoring
    overall_score = Column(Float, default=0.0)
    keyword_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    education_score = Column(Float, default=0.0)
    visual_score = Column(Float, default=0.0)
    ai_analysis = Column(Text, nullable=True)  # LLM-generated analysis

    # Status
    status = Column(String(50), default="pending")  # pending, shortlisted, rejected, contacted
    email_sent = Column(Boolean, default=False)
    contacted_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("JobDescription", back_populates="candidates")
