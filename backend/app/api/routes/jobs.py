from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.routes.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobSearch

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting."""
    # Check if user can post jobs
    if current_user.role not in [UserRole.RECRUITER, UserRole.FACULTY, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters, faculty, and admins can post jobs"
        )
    
    # Create job
    db_job = Job(
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
        requirements=job_data.requirements,
        location=job_data.location,
        job_type=job_data.job_type,
        experience_level=job_data.experience_level,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        required_skills=job_data.required_skills,
        preferred_skills=job_data.preferred_skills,
        keywords=job_data.keywords,
        application_deadline=job_data.application_deadline,
        posted_by_id=current_user.id
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job


@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    experience_level: Optional[str] = Query(None),
    is_active: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get jobs with optional filtering."""
    query = db.query(Job)
    
    # Apply filters
    if is_active:
        query = query.filter(Job.is_active == True)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Job.title.ilike(search_term) |
            Job.company.ilike(search_term) |
            Job.description.ilike(search_term)
        )
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)
    
    # Get results with pagination
    jobs = query.offset(skip).limit(limit).all()
    
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific job by ID."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    if job.posted_by_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own job postings"
        )
    
    # Update job fields
    update_data = job_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    
    return job


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a job posting."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    if job.posted_by_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own job postings"
        )
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}


@router.get("/my/posted", response_model=List[JobResponse])
async def get_my_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get jobs posted by the current user."""
    if current_user.role not in [UserRole.RECRUITER, UserRole.FACULTY, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters, faculty, and admins can view posted jobs"
        )
    
    jobs = db.query(Job).filter(Job.posted_by_id == current_user.id).all()
    return jobs