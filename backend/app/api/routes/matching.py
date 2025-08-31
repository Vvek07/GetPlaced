from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.routes.auth import get_current_active_user
from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app.models.application import JobMatch, Application, ApplicationStatus
from app.services.job_matcher import job_matcher
from app.schemas.resume import ResumeMatch

router = APIRouter()


@router.post("/resume/{resume_id}/job/{job_id}", response_model=ResumeMatch)
async def match_resume_to_job(
    resume_id: int,
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate compatibility score between a resume and a job."""
    
    # Get resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.is_processed != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume is still being processed"
        )
    
    # Get job
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Prepare data for matching
    resume_data = {
        'skills': resume.skills or [],
        'experience': resume.experience or [],
        'education': resume.education or [],
        'raw_text': resume.raw_text or ''
    }
    
    job_data = {
        'title': job.title,
        'description': job.description,
        'requirements': job.requirements,
        'required_skills': job.required_skills or [],
        'preferred_skills': job.preferred_skills or [],
        'keywords': job.keywords or [],
        'experience_level': job.experience_level
    }
    
    # Calculate match score
    match_score = job_matcher.calculate_compatibility_score(resume_data, job_data)
    
    # Save or update job match record
    existing_match = db.query(JobMatch).filter(
        JobMatch.job_id == job_id,
        JobMatch.user_id == current_user.id,
        JobMatch.resume_id == resume_id
    ).first()
    
    if existing_match:
        # Update existing match
        existing_match.overall_score = match_score.overall_score
        existing_match.skill_score = match_score.skill_score
        existing_match.experience_score = match_score.experience_score
        existing_match.education_score = match_score.education_score
        existing_match.keyword_score = match_score.keyword_score
        existing_match.match_details = {
            'matched_skills': match_score.matched_skills,
            'missing_skills': match_score.missing_skills,
            'strengths': match_score.strengths,
            'weaknesses': match_score.weaknesses,
            'recommendations': match_score.recommendations
        }
    else:
        # Create new match
        new_match = JobMatch(
            job_id=job_id,
            user_id=current_user.id,
            resume_id=resume_id,
            overall_score=match_score.overall_score,
            skill_score=match_score.skill_score,
            experience_score=match_score.experience_score,
            education_score=match_score.education_score,
            keyword_score=match_score.keyword_score,
            match_details={
                'matched_skills': match_score.matched_skills,
                'missing_skills': match_score.missing_skills,
                'strengths': match_score.strengths,
                'weaknesses': match_score.weaknesses,
                'recommendations': match_score.recommendations
            }
        )
        db.add(new_match)
    
    db.commit()
    
    return ResumeMatch(
        job_id=job_id,
        job_title=job.title,
        company=job.company,
        overall_score=match_score.overall_score,
        skill_score=match_score.skill_score,
        experience_score=match_score.experience_score,
        education_score=match_score.education_score,
        keyword_score=match_score.keyword_score,
        matched_skills=match_score.matched_skills,
        missing_skills=match_score.missing_skills,
        strengths=match_score.strengths,
        weaknesses=match_score.weaknesses,
        recommendations=match_score.recommendations
    )


@router.get("/resume/{resume_id}/recommendations", response_model=List[ResumeMatch])
async def get_job_recommendations(
    resume_id: int,
    limit: int = Query(10, ge=1, le=50),
    min_score: float = Query(50.0, ge=0.0, le=100.0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get job recommendations for a resume based on compatibility scores."""
    
    # Get resume
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.is_processed != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume is still being processed"
        )
    
    # Get active jobs
    jobs = db.query(Job).filter(Job.is_active == True).limit(50).all()  # Limit for performance
    
    recommendations = []
    
    # Prepare resume data
    resume_data = {
        'skills': resume.skills or [],
        'experience': resume.experience or [],
        'education': resume.education or [],
        'raw_text': resume.raw_text or ''
    }
    
    for job in jobs:
        # Prepare job data
        job_data = {
            'title': job.title,
            'description': job.description,
            'requirements': job.requirements,
            'required_skills': job.required_skills or [],
            'preferred_skills': job.preferred_skills or [],
            'keywords': job.keywords or [],
            'experience_level': job.experience_level
        }
        
        # Calculate match score
        match_score = job_matcher.calculate_compatibility_score(resume_data, job_data)
        
        # Only include jobs above minimum score
        if match_score.overall_score >= min_score:
            recommendations.append(ResumeMatch(
                job_id=job.id,
                job_title=job.title,
                company=job.company,
                overall_score=match_score.overall_score,
                skill_score=match_score.skill_score,
                experience_score=match_score.experience_score,
                education_score=match_score.education_score,
                keyword_score=match_score.keyword_score,
                matched_skills=match_score.matched_skills,
                missing_skills=match_score.missing_skills,
                strengths=match_score.strengths,
                weaknesses=match_score.weaknesses,
                recommendations=match_score.recommendations
            ))
    
    # Sort by overall score and limit results
    recommendations.sort(key=lambda x: x.overall_score, reverse=True)
    return recommendations[:limit]


@router.get("/job/{job_id}/candidates")
async def get_job_candidates(
    job_id: int,
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(60.0, ge=0.0, le=100.0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get ranked candidates for a job (for recruiters)."""
    
    # Check if user can view candidates
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions (job poster or admin)
    if job.posted_by_id != current_user.id and not current_user.role.value in ['admin', 'faculty']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view candidates for your own job postings"
        )
    
    # Get job matches for this job
    matches = db.query(JobMatch).filter(
        JobMatch.job_id == job_id,
        JobMatch.overall_score >= min_score
    ).order_by(JobMatch.overall_score.desc()).limit(limit).all()
    
    candidates = []
    for match in matches:
        user = db.query(User).filter(User.id == match.user_id).first()
        resume = db.query(Resume).filter(Resume.id == match.resume_id).first()
        
        if user and resume:
            candidates.append({
                'user_id': user.id,
                'user_name': user.full_name,
                'user_email': user.email,
                'resume_id': resume.id,
                'overall_score': match.overall_score,
                'skill_score': match.skill_score,
                'experience_score': match.experience_score,
                'education_score': match.education_score,
                'keyword_score': match.keyword_score,
                'match_details': match.match_details,
                'created_at': match.created_at
            })
    
    return candidates


@router.post("/apply/{job_id}")
async def apply_to_job(
    job_id: int,
    resume_id: int,
    cover_letter: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Apply to a job with a specific resume."""
    
    # Check if job exists and is active
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not active"
        )
    
    # Check if resume exists and belongs to user
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Check if already applied
    existing_application = db.query(Application).filter(
        Application.job_id == job_id,
        Application.user_id == current_user.id
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job"
        )
    
    # Get or create job match score
    job_match = db.query(JobMatch).filter(
        JobMatch.job_id == job_id,
        JobMatch.user_id == current_user.id,
        JobMatch.resume_id == resume_id
    ).first()
    
    compatibility_score = job_match.overall_score if job_match else None
    
    # Create application
    application = Application(
        job_id=job_id,
        user_id=current_user.id,
        resume_id=resume_id,
        cover_letter=cover_letter,
        status=ApplicationStatus.APPLIED,
        compatibility_score=compatibility_score,
        skill_match_score=job_match.skill_score if job_match else None,
        experience_match_score=job_match.experience_score if job_match else None,
        keyword_match_score=job_match.keyword_score if job_match else None,
        matched_skills=job_match.match_details.get('matched_skills') if job_match and job_match.match_details else None,
        missing_skills=job_match.match_details.get('missing_skills') if job_match and job_match.match_details else None,
        match_analysis=job_match.match_details if job_match else None
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return {"message": "Application submitted successfully", "application_id": application.id}