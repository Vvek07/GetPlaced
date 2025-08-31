import re
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class MatchScore:
    """Data class for compatibility matching scores."""
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


class JobMatcher:
    """Advanced job matching engine using multiple algorithms."""
    
    def __init__(self):
        """Initialize the job matcher with scoring weights."""
        self.weights = {
            'skills': 0.4,
            'experience': 0.25,
            'education': 0.15,
            'keywords': 0.2
        }
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def calculate_compatibility_score(
        self, 
        resume_data: Dict[str, Any], 
        job_data: Dict[str, Any]
    ) -> MatchScore:
        """Calculate comprehensive compatibility score between resume and job."""
        
        # Extract relevant data
        resume_skills = resume_data.get('skills', [])
        resume_experience = resume_data.get('experience', [])
        resume_education = resume_data.get('education', [])
        resume_text = resume_data.get('raw_text', '')
        
        job_skills = job_data.get('required_skills', []) + job_data.get('preferred_skills', [])
        job_description = job_data.get('description', '')
        job_requirements = job_data.get('requirements', '')
        job_keywords = job_data.get('keywords', [])
        
        # Calculate individual scores
        skill_score, matched_skills, missing_skills = self._calculate_skill_score(resume_skills, job_skills)
        experience_score = self._calculate_experience_score(resume_experience, job_data)
        education_score = self._calculate_education_score(resume_education, job_data)
        keyword_score = self._calculate_keyword_score(resume_text, job_description + ' ' + job_requirements, job_keywords)
        
        # Calculate weighted overall score
        overall_score = (
            skill_score * self.weights['skills'] +
            experience_score * self.weights['experience'] +
            education_score * self.weights['education'] +
            keyword_score * self.weights['keywords']
        )
        
        # Generate insights
        strengths, weaknesses, recommendations = self._generate_insights(
            skill_score, experience_score, education_score, keyword_score,
            matched_skills, missing_skills, resume_data, job_data
        )
        
        return MatchScore(
            overall_score=round(overall_score, 2),
            skill_score=round(skill_score, 2),
            experience_score=round(experience_score, 2),
            education_score=round(education_score, 2),
            keyword_score=round(keyword_score, 2),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
    
    def _calculate_skill_score(
        self, 
        resume_skills: List[str], 
        job_skills: List[str]
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate skill matching score with fuzzy matching."""
        if not job_skills:
            return 100.0, resume_skills, []
        
        if not resume_skills:
            return 0.0, [], job_skills
        
        matched_skills = []
        missing_skills = []
        skill_scores = []
        
        # Normalize skills for better matching
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        for job_skill in job_skills:
            job_skill_lower = job_skill.lower()
            best_match_score = 0
            best_match = None
            
            # Find best matching resume skill using fuzzy matching
            for resume_skill in resume_skills:
                resume_skill_lower = resume_skill.lower()
                
                # Exact match
                if job_skill_lower == resume_skill_lower:
                    score = 100
                # Fuzzy match
                else:
                    score = fuzz.ratio(job_skill_lower, resume_skill_lower)
                
                if score > best_match_score:
                    best_match_score = score
                    best_match = resume_skill
            
            # Consider it a match if score is above threshold
            if best_match_score >= 80:
                matched_skills.append(best_match)
                skill_scores.append(best_match_score / 100)
            else:
                missing_skills.append(job_skill)
                skill_scores.append(0)
        
        # Calculate overall skill score
        if skill_scores:
            skill_score = sum(skill_scores) / len(skill_scores) * 100
        else:
            skill_score = 0
        
        return skill_score, matched_skills, missing_skills
    
    def _calculate_experience_score(
        self, 
        resume_experience: List[Dict[str, str]], 
        job_data: Dict[str, Any]
    ) -> float:
        """Calculate experience relevance score."""
        if not resume_experience:
            return 0.0
        
        job_title = job_data.get('title', '').lower()
        job_description = job_data.get('description', '').lower()
        job_requirements = job_data.get('requirements', '').lower()
        experience_level = job_data.get('experience_level', '').lower()
        
        # Extract keywords from job posting
        job_keywords = self._extract_experience_keywords(job_title + ' ' + job_description + ' ' + job_requirements)
        
        total_score = 0
        weight_sum = 0
        
        for exp in resume_experience:
            exp_title = exp.get('title', '').lower()
            exp_description = exp.get('description', '').lower()
            exp_company = exp.get('company', '').lower()
            
            # Calculate relevance score for this experience
            exp_text = exp_title + ' ' + exp_description + ' ' + exp_company
            relevance_score = self._calculate_text_similarity(exp_text, job_title + ' ' + job_description)
            
            # Weight recent experience more heavily (simplified)
            weight = 1.0  # Could be enhanced with actual date parsing
            
            total_score += relevance_score * weight
            weight_sum += weight
        
        if weight_sum > 0:
            experience_score = (total_score / weight_sum) * 100
        else:
            experience_score = 0
        
        # Adjust based on experience level requirement
        experience_score = self._adjust_for_experience_level(experience_score, len(resume_experience), experience_level)
        
        return min(experience_score, 100.0)
    
    def _calculate_education_score(
        self, 
        resume_education: List[Dict[str, str]], 
        job_data: Dict[str, Any]
    ) -> float:
        """Calculate education relevance score."""
        if not resume_education:
            return 50.0  # Neutral score if no education info
        
        job_requirements = job_data.get('requirements', '').lower()
        job_description = job_data.get('description', '').lower()
        
        # Look for degree requirements in job posting
        degree_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma', 'certificate']
        has_degree_requirement = any(keyword in job_requirements or keyword in job_description for keyword in degree_keywords)
        
        if not has_degree_requirement:
            return 100.0  # Full score if no specific education requirement
        
        # Calculate education relevance
        max_score = 0
        for education in resume_education:
            degree = education.get('degree', '').lower()
            
            # Basic scoring based on degree level
            if any(keyword in degree for keyword in ['phd', 'doctorate']):
                score = 100
            elif any(keyword in degree for keyword in ['master', 'mba', 'ms', 'ma']):
                score = 90
            elif any(keyword in degree for keyword in ['bachelor', 'bs', 'ba', 'bsc']):
                score = 80
            elif any(keyword in degree for keyword in ['associate', 'diploma']):
                score = 60
            else:
                score = 40
            
            # Bonus for relevant field
            if self._is_relevant_field(degree, job_requirements + ' ' + job_description):
                score += 20
            
            max_score = max(max_score, score)
        
        return min(max_score, 100.0)
    
    def _calculate_keyword_score(
        self, 
        resume_text: str, 
        job_text: str, 
        job_keywords: List[str]
    ) -> float:
        """Calculate keyword matching score using TF-IDF and cosine similarity."""
        if not resume_text or not job_text:
            return 0.0
        
        try:
            # Prepare texts
            texts = [resume_text.lower(), job_text.lower()]
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            base_score = similarity * 100
            
            # Bonus for specific job keywords
            if job_keywords:
                keyword_matches = 0
                resume_lower = resume_text.lower()
                
                for keyword in job_keywords:
                    if keyword.lower() in resume_lower:
                        keyword_matches += 1
                
                keyword_bonus = (keyword_matches / len(job_keywords)) * 20
                base_score += keyword_bonus
            
            return min(base_score, 100.0)
            
        except Exception as e:
            logger.error(f"Error calculating keyword score: {str(e)}")
            return 0.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using TF-IDF."""
        if not text1 or not text2:
            return 0.0
        
        try:
            texts = [text1.lower(), text2.lower()]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except:
            return 0.0
    
    def _extract_experience_keywords(self, text: str) -> List[str]:
        """Extract experience-related keywords from job text."""
        keywords = []
        
        # Common experience indicators
        experience_patterns = [
            r'(\d+)(?:\+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:experience|exp).*?(\d+)(?:\+)?\s*(?:years?|yrs?)',
            r'(?:senior|junior|lead|principal|entry|mid)',
            r'(?:developer|engineer|manager|analyst|specialist|coordinator)'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(matches)
        
        return keywords
    
    def _adjust_for_experience_level(self, score: float, exp_count: int, required_level: str) -> float:
        """Adjust experience score based on required experience level."""
        if not required_level:
            return score
        
        # Define experience level requirements
        level_requirements = {
            'entry': (0, 2),
            'junior': (0, 3),
            'mid': (2, 7),
            'senior': (5, 15),
            'lead': (7, 20),
            'principal': (10, 25)
        }
        
        if required_level in level_requirements:
            min_exp, max_exp = level_requirements[required_level]
            
            if exp_count < min_exp:
                # Penalize for insufficient experience
                penalty = (min_exp - exp_count) * 10
                score = max(score - penalty, 0)
            elif exp_count > max_exp:
                # Slight bonus for over-qualification (but not too much)
                bonus = min((exp_count - max_exp) * 2, 10)
                score = min(score + bonus, 100)
        
        return score
    
    def _is_relevant_field(self, degree: str, job_text: str) -> bool:
        """Check if the degree field is relevant to the job."""
        # Define field mappings
        tech_fields = ['computer', 'software', 'information', 'engineering', 'technology', 'science']
        business_fields = ['business', 'management', 'administration', 'finance', 'economics']
        design_fields = ['design', 'art', 'creative', 'visual', 'graphic']
        
        # Check for tech relevance
        if any(field in job_text for field in ['software', 'developer', 'engineer', 'technology', 'programming']):
            return any(field in degree for field in tech_fields)
        
        # Check for business relevance
        if any(field in job_text for field in ['manager', 'business', 'sales', 'marketing', 'finance']):
            return any(field in degree for field in business_fields)
        
        # Check for design relevance
        if any(field in job_text for field in ['design', 'creative', 'visual', 'ui', 'ux']):
            return any(field in degree for field in design_fields)
        
        return False
    
    def _generate_insights(
        self,
        skill_score: float,
        experience_score: float,
        education_score: float,
        keyword_score: float,
        matched_skills: List[str],
        missing_skills: List[str],
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate strengths, weaknesses, and recommendations."""
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Analyze strengths
        if skill_score >= 80:
            strengths.append("Strong skill match with job requirements")
        if experience_score >= 80:
            strengths.append("Highly relevant work experience")
        if education_score >= 80:
            strengths.append("Educational background aligns well with job requirements")
        if keyword_score >= 80:
            strengths.append("Resume content strongly matches job description")
        
        if matched_skills:
            strengths.append(f"Key matching skills: {', '.join(matched_skills[:5])}")
        
        # Analyze weaknesses
        if skill_score < 60:
            weaknesses.append("Limited skill match with job requirements")
        if experience_score < 60:
            weaknesses.append("Work experience may not be highly relevant")
        if education_score < 60:
            weaknesses.append("Educational background could be more aligned")
        if keyword_score < 60:
            weaknesses.append("Resume content doesn't strongly match job description")
        
        if missing_skills:
            weaknesses.append(f"Missing key skills: {', '.join(missing_skills[:5])}")
        
        # Generate recommendations
        if missing_skills:
            recommendations.append(f"Consider developing skills in: {', '.join(missing_skills[:3])}")
        
        if skill_score < 70:
            recommendations.append("Highlight relevant skills more prominently in your resume")
        
        if keyword_score < 70:
            recommendations.append("Include more job-specific keywords in your resume")
        
        if experience_score < 70:
            recommendations.append("Emphasize relevant work experience and achievements")
        
        # Always provide at least one recommendation
        if not recommendations:
            recommendations.append("Your profile looks good! Consider customizing your resume for this specific role")
        
        return strengths, weaknesses, recommendations


# Initialize global matcher instance
job_matcher = JobMatcher()