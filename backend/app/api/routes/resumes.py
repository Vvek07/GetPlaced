from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import json
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.api.routes.auth import get_current_active_user
from app.models.user import User
from app.models.resume import Resume
from app.services.resume_parser import resume_parser
from app.services.job_matcher import job_matcher
from app.schemas.resume import ResumeResponse, ResumeAnalysis, ResumeCreate

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume file."""
    
    # Validate file type
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not supported. Allowed types: {allowed_extensions}"
        )
    
    # Validate file size
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = settings.UPLOAD_DIRECTORY
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create database record
        db_resume = Resume(
            user_id=current_user.id,
            filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            file_type=file_extension,
            is_processed="pending"
        )
        
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)
        
        # Parse resume asynchronously (in real app, this would be a background task)
        try:
            extracted_info = resume_parser.parse_resume(file_path)
            
            # Update resume with parsed data
            db_resume.raw_text = resume_parser.extract_text_from_file(file_path)
            db_resume.parsed_data = {
                "name": extracted_info.name,
                "email": extracted_info.email,
                "phone": extracted_info.phone,
                "address": extracted_info.address
            }
            db_resume.skills = extracted_info.skills
            db_resume.experience = [exp.__dict__ if hasattr(exp, '__dict__') else exp for exp in extracted_info.experience]
            db_resume.education = [edu.__dict__ if hasattr(edu, '__dict__') else edu for edu in extracted_info.education]
            db_resume.certifications = extracted_info.certifications
            db_resume.is_processed = "completed"
            
            # Calculate quality score (simplified)
            quality_score = calculate_resume_quality_score(extracted_info)
            db_resume.quality_score = quality_score
            
            # Generate strengths, weaknesses, and suggestions
            analysis = analyze_resume_quality(extracted_info, db_resume.raw_text)
            db_resume.strengths = analysis['strengths']
            db_resume.weaknesses = analysis['weaknesses']
            db_resume.suggestions = analysis['suggestions']
            
        except Exception as e:
            db_resume.is_processed = "failed"
            db_resume.processing_error = str(e)
        
        db.commit()
        db.refresh(db_resume)
        
        return db_resume
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )


@router.get("/", response_model=List[ResumeResponse])
async def get_user_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all resumes for the current user."""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a resume."""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file from filesystem
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysis)
async def get_resume_analysis(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed analysis of a resume."""
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
    
    return ResumeAnalysis(
        resume_id=resume.id,
        quality_score=resume.quality_score,
        strengths=resume.strengths or [],
        weaknesses=resume.weaknesses or [],
        suggestions=resume.suggestions or [],
        skills=resume.skills or [],
        experience_count=len(resume.experience or []),
        education_count=len(resume.education or []),
        certification_count=len(resume.certifications or [])
    )


def calculate_resume_quality_score(extracted_info) -> float:
    """Calculate a quality score for the resume based on completeness and content."""
    score = 0.0
    max_score = 100.0
    
    # Basic information (20 points)
    if extracted_info.name:
        score += 5
    if extracted_info.email:
        score += 5
    if extracted_info.phone:
        score += 5
    if extracted_info.address:
        score += 5
    
    # Skills (25 points)
    skill_count = len(extracted_info.skills)
    if skill_count >= 10:
        score += 25
    elif skill_count >= 5:
        score += 20
    elif skill_count >= 3:
        score += 15
    elif skill_count >= 1:
        score += 10
    
    # Experience (30 points)
    exp_count = len(extracted_info.experience)
    if exp_count >= 3:
        score += 30
    elif exp_count >= 2:
        score += 25
    elif exp_count >= 1:
        score += 20
    
    # Education (15 points)
    edu_count = len(extracted_info.education)
    if edu_count >= 2:
        score += 15
    elif edu_count >= 1:
        score += 12
    
    # Certifications (10 points)
    cert_count = len(extracted_info.certifications)
    if cert_count >= 3:
        score += 10
    elif cert_count >= 1:
        score += 5
    
    return min(score, max_score)


def analyze_resume_quality(extracted_info, raw_text: str) -> dict:
    """Analyze resume quality and provide feedback."""
    strengths = []
    weaknesses = []
    suggestions = []
    
    # Analyze completeness
    if extracted_info.name and extracted_info.email and extracted_info.phone:
        strengths.append("Complete contact information provided")
    else:
        weaknesses.append("Missing essential contact information")
        suggestions.append("Ensure your resume includes name, email, and phone number")
    
    # Analyze skills
    skill_count = len(extracted_info.skills)
    if skill_count >= 10:
        strengths.append("Comprehensive skills section")
    elif skill_count >= 5:
        strengths.append("Good variety of skills listed")
    else:
        weaknesses.append("Limited skills information")
        suggestions.append("Add more relevant technical and soft skills")
    
    # Analyze experience
    exp_count = len(extracted_info.experience)
    if exp_count >= 3:
        strengths.append("Extensive work experience")
    elif exp_count >= 1:
        strengths.append("Relevant work experience included")
    else:
        weaknesses.append("Limited work experience information")
        suggestions.append("Include internships, projects, or volunteer work")
    
    # Analyze education
    edu_count = len(extracted_info.education)
    if edu_count >= 1:
        strengths.append("Educational background provided")
    else:
        weaknesses.append("Missing education information")
        suggestions.append("Include your educational qualifications")
    
    # Analyze certifications
    cert_count = len(extracted_info.certifications)
    if cert_count >= 3:
        strengths.append("Multiple professional certifications")
    elif cert_count >= 1:
        strengths.append("Professional certifications included")
    else:
        suggestions.append("Consider adding relevant certifications or training")
    
    # Text analysis
    word_count = len(raw_text.split())
    if word_count < 200:
        weaknesses.append("Resume content appears too brief")
        suggestions.append("Expand descriptions of your experience and achievements")
    elif word_count > 1000:
        weaknesses.append("Resume content appears too lengthy")
        suggestions.append("Condense information to highlight key achievements")
    else:
        strengths.append("Appropriate resume length")
    
    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'suggestions': suggestions
    }