from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResumeBase(BaseModel):
    filename: str
    file_size: int
    file_type: str


class ResumeCreate(ResumeBase):
    pass


class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    file_path: str
    raw_text: Optional[str] = None
    parsed_data: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    education: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[str]] = None
    quality_score: Optional[float] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    is_processed: str
    processing_error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ResumeAnalysis(BaseModel):
    resume_id: int
    quality_score: Optional[float]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    skills: List[str]
    experience_count: int
    education_count: int
    certification_count: int


class ResumeMatch(BaseModel):
    job_id: int
    job_title: str
    company: str
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    keyword_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]