from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class JobBase(BaseModel):
    title: str
    company: str
    description: str
    requirements: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    application_deadline: Optional[datetime] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    id: int
    is_active: bool
    posted_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobSearch(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = []
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    page: int = 1
    limit: int = 10