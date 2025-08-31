from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    APPLIED = "applied"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Relationships
    job = relationship("Job")
    user = relationship("User")
    resume = relationship("Resume")
    
    # Application details
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    cover_letter = Column(Text, nullable=True)
    
    # Matching analysis
    compatibility_score = Column(Float, nullable=True)
    skill_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    keyword_match_score = Column(Float, nullable=True)
    
    # Detailed analysis
    matched_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    match_analysis = Column(JSON, nullable=True)
    
    # Recruiter feedback
    recruiter_notes = Column(Text, nullable=True)
    recruiter_rating = Column(Float, nullable=True)
    
    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Relationships
    job = relationship("Job")
    user = relationship("User")
    resume = relationship("Resume")
    
    # Matching scores
    overall_score = Column(Float, nullable=False)
    skill_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    keyword_score = Column(Float, nullable=False)
    
    # Match details
    match_details = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())