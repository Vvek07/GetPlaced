from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    
    # Job description text
    job_description = Column(Text, nullable=False)
    job_title = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    
    # Analysis results
    ats_score = Column(Float, nullable=False)
    missing_keywords = Column(JSON, nullable=False, default=list)
    strong_keywords = Column(JSON, nullable=False, default=list)
    suggestions = Column(JSON, nullable=False, default=list)
    
    # Additional analysis data
    resume_text = Column(Text, nullable=True)
    analysis_details = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")