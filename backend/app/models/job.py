from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    location = Column(String, nullable=True)
    job_type = Column(String, nullable=True)  # full-time, part-time, internship
    experience_level = Column(String, nullable=True)  # entry, mid, senior
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    
    # Skills and keywords (stored as JSON)
    required_skills = Column(JSON, nullable=True)
    preferred_skills = Column(JSON, nullable=True)
    keywords = Column(JSON, nullable=True)
    
    # Job status
    is_active = Column(Boolean, default=True)
    application_deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Posted by
    posted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    posted_by = relationship("User")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())