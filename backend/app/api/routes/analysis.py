from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import base64
import os
import tempfile
import subprocess
import sys
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResponse, AnalysisRequest
from app.api.routes.auth import get_current_active_user

# Runtime import with fallback
try:
    from app.services.ats_analyzer import ATSAnalyzer
    from app.services.resume_parser import ResumeParser
    ML_SERVICES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ML services not available: {e}")
    ML_SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter()

# Track if ML packages have been installed
ml_packages_installed = False

def ensure_ml_packages():
    """Ensure ML packages are installed at runtime."""
    global ml_packages_installed
    
    if ml_packages_installed:
        return True
        
    try:
        # Try to install required packages
        packages = ["spacy>=3.4.0", "scikit-learn>=1.0.0", "numpy>=1.21.0", "pandas>=1.3.0"]
        
        for package in packages:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True, text=True, timeout=30)
                logger.info(f"Installed {package}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                logger.warning(f"Failed to install {package}: {e}")
        
        # Try to download spaCy model
        try:
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                         check=True, capture_output=True, text=True, timeout=60)
            logger.info("Downloaded spaCy model")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            logger.warning("Could not download spaCy model")
        
        ml_packages_installed = True
        return True
        
    except Exception as e:
        logger.error(f"Failed to install ML packages: {e}")
        return False


@router.post("/analyze", response_model=AnalysisResponse)
async def create_analysis(
    job_description: str = Form(...),
    job_title: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    resume_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Analyze resume against job description and return ATS score with detailed feedback
    """
    # Try to ensure ML packages are available
    if not ML_SERVICES_AVAILABLE:
        logger.info("Attempting to install ML packages at runtime...")
        if ensure_ml_packages():
            # Try to import services again
            try:
                global ATSAnalyzer, ResumeParser
                from app.services.ats_analyzer import ATSAnalyzer
                from app.services.resume_parser import ResumeParser
                ML_SERVICES_AVAILABLE = True
                logger.info("ML services now available")
            except ImportError as e:
                logger.error(f"Still cannot import ML services: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Resume analysis services are currently unavailable. Please try again later."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Resume analysis services are currently unavailable. Please try again later."
            )
    # Ensure we have either a file or resume_id
    if not resume_file and not resume_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either resume_file or resume_id must be provided"
        )
    
    resume_text = ""
    resume_record = None
    
    # Get resume text
    if resume_id:
        # Use existing resume
        resume_record = db.query(Resume).filter(
            Resume.id == resume_id, 
            Resume.user_id == current_user.id
        ).first()
        
        if not resume_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        resume_text = resume_record.raw_text or ""
        
    elif resume_file:
        # Process uploaded file
        try:
            # Save temporary file
            content = await resume_file.read()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.filename.split('.')[-1]}") as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            # Parse resume
            parser = ResumeParser()
            parsed_result = parser.parse_resume(tmp_file_path)
            resume_text = parsed_result.get('raw_text', '')
            extracted_info = parsed_result.get('extracted_info')
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            # Convert ExtractedInfo to dict for database storage
            parsed_data = {
                'name': extracted_info.name,
                'email': extracted_info.email,
                'phone': extracted_info.phone,
                'address': extracted_info.address,
                'skills': extracted_info.skills,
                'education': extracted_info.education,
                'experience': extracted_info.experience,
                'certifications': extracted_info.certifications,
                'languages': extracted_info.languages,
                'projects': extracted_info.projects
            }
            
            # Optionally save resume to database
            resume_record = Resume(
                user_id=current_user.id,
                filename=resume_file.filename,
                file_path="",  # We're not storing the file permanently
                file_size=len(content),
                file_type=resume_file.content_type or "application/octet-stream",
                raw_text=resume_text,
                parsed_data=parsed_data,
                is_processed="completed"
            )
            db.add(resume_record)
            db.commit()
            db.refresh(resume_record)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process resume file: {str(e)}"
            )
    
    if not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from resume"
        )
    
    # Perform ATS analysis
    try:
        analyzer = ATSAnalyzer()
        analysis_result = analyzer.analyze_resume_vs_job(resume_text, job_description)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATS analysis failed: {str(e)}"
        )
    
    # Save analysis to database
    analysis = Analysis(
        user_id=current_user.id,
        resume_id=resume_record.id if resume_record else None,
        job_description=job_description,
        job_title=job_title,
        company_name=company_name,
        ats_score=analysis_result['ats_score'],
        missing_keywords=analysis_result['missing_keywords'],
        strong_keywords=analysis_result['strong_keywords'],
        suggestions=analysis_result['suggestions'],
        resume_text=resume_text,
        analysis_details={
            'detailed_analysis': analysis_result['detailed_analysis'],
            'strengths_analysis': analysis_result['strengths_analysis'],
            'weaknesses_analysis': analysis_result['weaknesses_analysis']
        }
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis


@router.get("/", response_model=List[AnalysisResponse])
async def get_user_analyses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all analyses for the current user
    """
    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).order_by(Analysis.created_at.desc()).all()
    
    return analyses


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific analysis by ID
    """
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return analysis


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete specific analysis
    """
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    db.delete(analysis)
    db.commit()
    
    return {"message": "Analysis deleted successfully"}