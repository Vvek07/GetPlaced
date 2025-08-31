from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class AnalysisCreate(BaseModel):
    job_description: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class DetailedAnalysis(BaseModel):
    """Schema for detailed ATS analysis results"""
    keyword_density: float
    industry_alignment: float
    experience_level_match: float
    quantification_score: float
    formatting_score: float
    strength_areas: List[str]
    weakness_areas: List[str]
    total_keywords_found: int
    total_keywords_expected: int
    match_ratio: float


class StrengthsAnalysis(BaseModel):
    """Schema for resume strengths analysis"""
    technical_skills: List[Dict[str, Any]]
    quantified_achievements: List[str]
    keyword_density_score: float


class WeaknessesAnalysis(BaseModel):
    """Schema for resume weaknesses analysis"""
    missing_hard_skills: List[str]
    missing_soft_skills: List[str]
    weak_areas: List[str]
    formatting_issues: List[str]


class AnalysisResponse(BaseModel):
    id: int
    resume_id: Optional[int]
    job_description: str
    job_title: Optional[str]
    company_name: Optional[str]
    ats_score: float
    missing_keywords: List[str]
    strong_keywords: List[str]
    suggestions: List[str]
    created_at: datetime
    analysis_details: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ResumeUpload(BaseModel):
    filename: str
    file_content: str  # base64 encoded content


class AnalysisRequest(BaseModel):
    resume_file: Optional[dict] = None  # For file upload
    resume_id: Optional[int] = None     # For existing resume
    job_description: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None