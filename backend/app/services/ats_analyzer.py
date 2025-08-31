import re
import string
from typing import List, Tuple, Dict, Set
from collections import Counter, defaultdict
import math
from dataclasses import dataclass


@dataclass
class KeywordMatch:
    """Represents a matched keyword with context and importance"""
    keyword: str
    frequency_resume: int
    frequency_job: int
    importance_score: float
    context_matches: List[str]
    category: str


@dataclass
class WeaknessAnalysis:
    """Detailed analysis of resume weaknesses"""
    missing_hard_skills: List[str]
    missing_soft_skills: List[str]
    weak_experience_areas: List[str]
    missing_education_keywords: List[str]
    formatting_issues: List[str]
    quantification_gaps: List[str]


@dataclass
class StrengthAnalysis:
    """Detailed analysis of resume strengths"""
    strong_technical_skills: List[KeywordMatch]
    strong_experience_matches: List[KeywordMatch]
    education_advantages: List[str]
    quantified_achievements: List[str]
    keyword_density_score: float


class ATSAnalyzer:
    """
    Advanced ATS scoring system that mimics real organizational ATS systems
    with sophisticated resume analysis and precise job matching.
    """
    
    def __init__(self):
        # Enhanced stop words for better filtering
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i',
            'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'am', 'also', 'very',
            'just', 'so', 'than', 'too', 'any', 'some', 'no', 'not', 'only', 'own',
            'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should',
            'now', 'use', 'work', 'experience', 'years', 'year', 'skills', 'skill'
        }
        
        # Advanced skill categorization with importance weights
        self.skill_categories = {
            'critical_technical': {
                'weight': 1.0,
                'keywords': [
                    'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
                    'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'tensorflow', 'pytorch',
                    'machine learning', 'deep learning', 'artificial intelligence', 'data science',
                    'sql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'kafka',
                    'microservices', 'rest api', 'graphql', 'ci/cd', 'devops', 'agile',
                    'scrum', 'git', 'github', 'gitlab', 'jenkins', 'terraform', 'ansible'
                ]
            },
            'important_technical': {
                'weight': 0.8,
                'keywords': [
                    'html', 'css', 'bootstrap', 'sass', 'typescript', 'php', 'ruby',
                    'c++', 'c#', 'go', 'rust', 'swift', 'kotlin', 'scala', 'r',
                    'mysql', 'oracle', 'cassandra', 'dynamodb', 'firebase', 'supabase',
                    'express', 'django', 'flask', 'spring', 'laravel', 'rails',
                    'webpack', 'babel', 'nginx', 'apache', 'linux', 'unix', 'windows'
                ]
            },
            'frameworks_libraries': {
                'weight': 0.7,
                'keywords': [
                    'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn',
                    'fastapi', 'nextjs', 'nuxt', 'svelte', 'ember', 'backbone',
                    'jquery', 'lodash', 'moment', 'axios', 'fetch', 'websocket',
                    'redux', 'vuex', 'mobx', 'rxjs', 'jest', 'mocha', 'cypress'
                ]
            },
            'methodologies': {
                'weight': 0.6,
                'keywords': [
                    'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'six sigma',
                    'tdd', 'bdd', 'pair programming', 'code review', 'continuous integration',
                    'continuous deployment', 'test automation', 'unit testing',
                    'integration testing', 'performance testing', 'security testing'
                ]
            },
            'soft_skills': {
                'weight': 0.5,
                'keywords': [
                    'leadership', 'communication', 'teamwork', 'problem solving',
                    'critical thinking', 'analytical', 'creative', 'innovative',
                    'project management', 'time management', 'organization',
                    'attention to detail', 'multitasking', 'adaptable', 'flexible',
                    'collaborative', 'mentoring', 'coaching', 'presentation skills'
                ]
            },
            'certifications': {
                'weight': 0.9,
                'keywords': [
                    'aws certified', 'azure certified', 'google cloud certified',
                    'pmp', 'cissp', 'ceh', 'cisa', 'cism', 'comptia', 'cisco',
                    'microsoft certified', 'oracle certified', 'scrum master',
                    'product owner', 'safe', 'itil', 'cobit', 'prince2'
                ]
            }
        }
        
        # Industry-specific keyword patterns
        self.industry_patterns = {
            'software': ['development', 'programming', 'coding', 'software', 'application'],
            'data': ['data', 'analytics', 'analysis', 'statistics', 'machine learning'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'serverless', 'containerization'],
            'security': ['security', 'cybersecurity', 'encryption', 'authentication'],
            'mobile': ['mobile', 'ios', 'android', 'app development', 'react native'],
            'web': ['web', 'frontend', 'backend', 'fullstack', 'responsive'],
            'devops': ['devops', 'ci/cd', 'deployment', 'infrastructure', 'monitoring']
        }
        
        # Experience level indicators
        self.experience_indicators = {
            'senior': ['senior', 'lead', 'principal', 'architect', 'manager', 'director'],
            'mid': ['mid-level', 'intermediate', '3-5 years', '4-6 years', '5-7 years'],
            'junior': ['junior', 'entry', 'associate', 'graduate', '0-2 years', '1-3 years']
        }
        
        # Action verbs that show impact
        self.impact_verbs = [
            'achieved', 'improved', 'increased', 'decreased', 'reduced', 'optimized',
            'implemented', 'developed', 'created', 'designed', 'built', 'launched',
            'delivered', 'managed', 'led', 'coordinated', 'streamlined', 'automated',
            'enhanced', 'upgraded', 'modernized', 'scaled', 'migrated', 'integrated'
        ]
    
    def analyze_resume_vs_job(self, resume_text: str, job_description: str) -> Dict:
        """
        Advanced analysis function that provides accurate ATS scoring like real systems
        """
        # Deep clean and process texts
        resume_clean = self._advanced_text_cleaning(resume_text)
        job_clean = self._advanced_text_cleaning(job_description)
        
        # Extract sophisticated keyword sets
        resume_keywords = self._extract_advanced_keywords(resume_clean)
        job_keywords = self._extract_advanced_keywords(job_clean)
        
        # Perform industry and role detection
        job_industry = self._detect_industry(job_clean)
        job_level = self._detect_experience_level(job_clean)
        
        # Advanced matching analysis
        keyword_matches = self._perform_advanced_matching(resume_keywords, job_keywords)
        missing_analysis = self._analyze_missing_keywords(resume_keywords, job_keywords, job_industry)
        
        # Comprehensive strength and weakness analysis
        strengths = self._analyze_strengths(resume_clean, job_clean, keyword_matches)
        weaknesses = self._analyze_weaknesses(resume_clean, job_clean, missing_analysis)
        
        # Calculate sophisticated ATS score
        ats_score = self._calculate_advanced_ats_score(
            keyword_matches, missing_analysis, resume_clean, job_clean, job_industry, job_level
        )
        
        # Generate actionable, non-BS suggestions
        suggestions = self._generate_actionable_suggestions(
            strengths, weaknesses, missing_analysis, ats_score, job_industry
        )
        
        # Extract quantified achievements and impact metrics
        quantified_achievements = self._extract_quantified_achievements(resume_clean)
        impact_score = self._calculate_impact_score(resume_clean)
        
        return {
            'ats_score': round(ats_score, 1),
            'strong_keywords': [match.keyword for match in keyword_matches[:15]],
            'missing_keywords': missing_analysis['critical_missing'][:10],
            'suggestions': suggestions,
            'detailed_analysis': {
                'keyword_density': self._calculate_keyword_density(resume_clean, job_clean),
                'industry_alignment': self._calculate_industry_alignment(resume_clean, job_industry),
                'experience_level_match': self._calculate_experience_match(resume_clean, job_level),
                'quantification_score': impact_score,
                'formatting_score': self._assess_resume_formatting(resume_text),
                'strength_areas': [s.category for s in strengths.strong_technical_skills[:5]] if strengths.strong_technical_skills else [],
                'weakness_areas': weaknesses.missing_hard_skills[:5],
                'total_keywords_found': len(keyword_matches),
                'total_keywords_expected': sum(len(terms) for terms in job_keywords.values()),
                'match_ratio': len(keyword_matches) / max(sum(len(terms) for terms in job_keywords.values()), 1)
            },
            'strengths_analysis': {
                'technical_skills': [{'keyword': m.keyword, 'score': m.importance_score} for m in strengths.strong_technical_skills[:10]],
                'quantified_achievements': quantified_achievements[:5],
                'keyword_density_score': strengths.keyword_density_score
            },
            'weaknesses_analysis': {
                'missing_hard_skills': weaknesses.missing_hard_skills[:8],
                'missing_soft_skills': weaknesses.missing_soft_skills[:5],
                'weak_areas': weaknesses.weak_experience_areas[:5],
                'formatting_issues': weaknesses.formatting_issues[:3]
            }
        }
    
    def _advanced_text_cleaning(self, text: str) -> str:
        """Advanced text cleaning with better normalization"""
        # Convert to lowercase
        text = text.lower()
        
        # Normalize common variations
        text = re.sub(r'\bn\.?js\b', 'nodejs', text)
        text = re.sub(r'\bc\+\+\b', 'cpp', text)
        text = re.sub(r'\bc#\b', 'csharp', text)
        text = re.sub(r'\b\.net\b', 'dotnet', text)
        text = re.sub(r'\bai/ml\b', 'artificial intelligence machine learning', text)
        text = re.sub(r'\bml/ai\b', 'machine learning artificial intelligence', text)
        text = re.sub(r'\bui/ux\b', 'user interface user experience', text)
        text = re.sub(r'\bci/cd\b', 'continuous integration continuous deployment', text)
        
        # Handle special characters and normalize spaces
        text = re.sub(r'[^\w\s\-\./]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _extract_advanced_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract keywords with categorization and context"""
        words = text.split()
        
        # Remove stop words and short words
        filtered_words = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Extract multi-word technical terms
        multiword_terms = self._extract_multiword_technical_terms(text)
        
        # Categorize keywords by importance
        categorized_keywords = defaultdict(list)
        
        # Process all skill categories
        for category, skill_data in self.skill_categories.items():
            keywords = skill_data['keywords']
            weight = skill_data['weight']
            
            for keyword in keywords:
                if keyword in text:
                    categorized_keywords[category].append(keyword)
        
        # Add multiword terms
        categorized_keywords['multiword_technical'] = multiword_terms
        
        # Extract numbers and quantified metrics
        quantified_terms = self._extract_quantified_terms(text)
        categorized_keywords['quantified'] = quantified_terms
        
        # Get word frequency for remaining terms
        word_freq = Counter(filtered_words)
        common_words = [word for word, freq in word_freq.most_common(30)]
        categorized_keywords['general'] = common_words
        
        return dict(categorized_keywords)
    
    def _extract_multiword_technical_terms(self, text: str) -> List[str]:
        """Extract sophisticated multi-word technical terms"""
        technical_patterns = [
            # Programming and Development
            r'machine learning', r'deep learning', r'artificial intelligence',
            r'data science', r'data analysis', r'data engineering',
            r'web development', r'mobile development', r'software engineering',
            r'full stack', r'front end', r'back end', r'frontend', r'backend',
            r'cloud computing', r'cloud architecture', r'microservices',
            
            # Methodologies
            r'agile development', r'scrum master', r'product owner',
            r'test driven development', r'behavior driven development',
            r'continuous integration', r'continuous deployment', r'devops',
            
            # Technologies
            r'version control', r'source control', r'code review',
            r'api development', r'rest api', r'graphql api',
            r'database design', r'system architecture', r'network security',
            
            # Soft Skills
            r'project management', r'team leadership', r'cross functional',
            r'problem solving', r'critical thinking', r'analytical skills',
            r'communication skills', r'presentation skills',
            
            # Industry Terms
            r'business intelligence', r'digital transformation',
            r'user experience', r'user interface', r'customer experience',
            r'product development', r'software architecture'
        ]
        
        terms = []
        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            terms.extend(matches)
        
        return list(set(terms))
    
    def _extract_quantified_terms(self, text: str) -> List[str]:
        """Extract quantified achievements and metrics"""
        quantified_patterns = [
            r'\d+%\s*(?:improvement|increase|decrease|reduction|growth)',
            r'\$\d+(?:,\d+)*(?:k|m|million|billion)?',
            r'\d+(?:,\d+)*\s*(?:users|customers|clients|projects|applications)',
            r'\d+(?:\.\d+)?x\s*(?:faster|improvement|increase)',
            r'reduced.*by\s*\d+%',
            r'increased.*by\s*\d+%',
            r'improved.*by\s*\d+%',
            r'\d+\s*(?:years?|months?)\s*(?:experience|exp)',
            r'managed\s*\d+\s*(?:people|team|members)',
            r'led\s*\d+\s*(?:people|team|members)'
        ]
        
        quantified = []
        for pattern in quantified_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            quantified.extend(matches)
        
        return list(set(quantified))
    
    def _perform_advanced_matching(self, resume_keywords: Dict, job_keywords: Dict) -> List[KeywordMatch]:
        """Perform sophisticated keyword matching with context and importance"""
        matches = []
        
        # Match across all categories
        for category in job_keywords:
            if category in resume_keywords:
                job_terms = job_keywords[category]
                resume_terms = resume_keywords[category]
                
                for job_term in job_terms:
                    for resume_term in resume_terms:
                        similarity = self._calculate_similarity(job_term, resume_term)
                        if similarity >= 0.8:  # High similarity threshold
                            importance = self._get_keyword_importance(job_term, category)
                            
                            match = KeywordMatch(
                                keyword=job_term,
                                frequency_resume=resume_terms.count(resume_term),
                                frequency_job=job_terms.count(job_term),
                                importance_score=importance * similarity,
                                context_matches=[resume_term],
                                category=category
                            )
                            matches.append(match)
        
        # Sort by importance score
        matches.sort(key=lambda x: x.importance_score, reverse=True)
        return matches
    
    def _analyze_missing_keywords(self, resume_keywords: Dict, job_keywords: Dict, industry: str) -> Dict:
        """Analyze missing keywords with categorization"""
        critical_missing = []
        important_missing = []
        nice_to_have_missing = []
        
        for category, job_terms in job_keywords.items():
            resume_terms = resume_keywords.get(category, [])
            weight = self.skill_categories.get(category, {}).get('weight', 0.5)
            
            for term in job_terms:
                if not self._is_term_covered(term, resume_terms):
                    importance = self._get_keyword_importance(term, category)
                    
                    if weight >= 0.9 or importance >= 0.9:
                        critical_missing.append(term)
                    elif weight >= 0.7 or importance >= 0.7:
                        important_missing.append(term)
                    else:
                        nice_to_have_missing.append(term)
        
        return {
            'critical_missing': critical_missing[:10],
            'important_missing': important_missing[:8],
            'nice_to_have_missing': nice_to_have_missing[:5]
        }
    
    def _analyze_strengths(self, resume_text: str, job_text: str, matches: List[KeywordMatch]) -> StrengthAnalysis:
        """Analyze resume strengths in detail"""
        # Technical skill strengths
        technical_matches = [m for m in matches if m.category in ['critical_technical', 'important_technical']]
        
        # Experience matches
        experience_matches = [m for m in matches if m.category in ['methodologies', 'frameworks_libraries']]
        
        # Education advantages
        education_keywords = self._extract_education_advantages(resume_text, job_text)
        
        # Quantified achievements
        achievements = self._extract_quantified_achievements(resume_text)
        
        # Calculate keyword density
        keyword_density = self._calculate_keyword_density(resume_text, job_text)
        
        return StrengthAnalysis(
            strong_technical_skills=technical_matches[:10],
            strong_experience_matches=experience_matches[:5],
            education_advantages=education_keywords,
            quantified_achievements=achievements,
            keyword_density_score=keyword_density
        )
    
    def _analyze_weaknesses(self, resume_text: str, job_text: str, missing_analysis: Dict) -> WeaknessAnalysis:
        """Analyze resume weaknesses comprehensively"""
        # Missing skills analysis
        missing_hard = missing_analysis['critical_missing'] + missing_analysis['important_missing']
        missing_soft = self._identify_missing_soft_skills(resume_text, job_text)
        
        # Experience gaps
        experience_gaps = self._identify_experience_gaps(resume_text, job_text)
        
        # Education gaps
        education_gaps = self._identify_education_gaps(resume_text, job_text)
        
        # Formatting issues
        formatting_issues = self._assess_formatting_issues(resume_text)
        
        # Quantification gaps
        quantification_gaps = self._identify_quantification_gaps(resume_text)
        
        return WeaknessAnalysis(
            missing_hard_skills=missing_hard[:8],
            missing_soft_skills=missing_soft[:5],
            weak_experience_areas=experience_gaps[:5],
            missing_education_keywords=education_gaps[:3],
            formatting_issues=formatting_issues[:3],
            quantification_gaps=quantification_gaps[:5]
        )
    
    def _analyze_strengths(self, resume_text: str, job_text: str, matches: List[KeywordMatch]) -> StrengthAnalysis:
        """Analyze resume strengths in detail"""
        # Technical skill strengths
        technical_matches = [m for m in matches if m.category in ['critical_technical', 'important_technical']]
        
        # Experience matches
        experience_matches = [m for m in matches if m.category in ['methodologies', 'frameworks_libraries']]
        
        # Education advantages
        education_keywords = self._extract_education_advantages(resume_text, job_text)
        
        # Quantified achievements
        achievements = self._extract_quantified_achievements(resume_text)
        
        # Calculate keyword density
        keyword_density = self._calculate_keyword_density(resume_text, job_text)
        
        return StrengthAnalysis(
            strong_technical_skills=technical_matches[:10],
            strong_experience_matches=experience_matches[:5],
            education_advantages=education_keywords,
            quantified_achievements=achievements,
            keyword_density_score=keyword_density
        )
    
    def _analyze_weaknesses(self, resume_text: str, job_text: str, missing_analysis: Dict) -> WeaknessAnalysis:
        """Analyze resume weaknesses comprehensively"""
        # Missing skills analysis
        missing_hard = missing_analysis['critical_missing'] + missing_analysis['important_missing']
        missing_soft = self._identify_missing_soft_skills(resume_text, job_text)
        
        # Experience gaps
        experience_gaps = self._identify_experience_gaps(resume_text, job_text)
        
        # Education gaps
        education_gaps = self._identify_education_gaps(resume_text, job_text)
        
        # Formatting issues
        formatting_issues = self._assess_formatting_issues(resume_text)
        
        # Quantification gaps
        quantification_gaps = self._identify_quantification_gaps(resume_text)
        
        return WeaknessAnalysis(
            missing_hard_skills=missing_hard[:8],
            missing_soft_skills=missing_soft[:5],
            weak_experience_areas=experience_gaps[:5],
            missing_education_keywords=education_gaps[:3],
            formatting_issues=formatting_issues[:3],
            quantification_gaps=quantification_gaps[:5]
        )
    
    def _calculate_advanced_ats_score(self, matches: List[KeywordMatch], missing: Dict, 
                                    resume_text: str, job_text: str, industry: str, level: str) -> float:
        """Calculate sophisticated ATS score like real systems"""
        if not matches:
            return 0.0
        
        # Base keyword matching score (40% weight)
        keyword_score = sum(match.importance_score for match in matches[:20]) / 20 * 40
        
        # Industry alignment score (25% weight)
        industry_score = self._calculate_industry_alignment(resume_text, industry) * 25
        
        # Experience level match score (20% weight)
        experience_score = self._calculate_experience_match(resume_text, level) * 20
        
        # Quantification and impact score (10% weight)
        impact_score = self._calculate_impact_score(resume_text) * 10
        
        # Formatting and structure score (5% weight)
        format_score = self._assess_resume_formatting(resume_text) * 5
        
        # Penalty for critical missing keywords
        critical_penalty = len(missing['critical_missing']) * 3
        important_penalty = len(missing['important_missing']) * 1.5
        
        total_score = keyword_score + industry_score + experience_score + impact_score + format_score
        total_score -= (critical_penalty + important_penalty)
        
        return max(0, min(100, total_score))
    
    def _generate_actionable_suggestions(self, strengths: StrengthAnalysis, weaknesses: WeaknessAnalysis, 
                                       missing: Dict, score: float, industry: str) -> List[str]:
        """Generate specific, actionable suggestions (no BS generic advice)"""
        suggestions = []
        
        # Score-based strategic advice
        if score < 30:
            suggestions.append(f"CRITICAL: Your resume needs major restructuring for {industry} roles. Focus on technical skills alignment first.")
        elif score < 50:
            suggestions.append(f"Your resume shows potential but needs significant keyword optimization for {industry} positions.")
        elif score < 70:
            suggestions.append("Good foundation! Focus on adding missing technical skills and quantifying your achievements.")
        elif score < 85:
            suggestions.append("Strong profile! Minor tweaks to keyword density and specific skills will boost your ATS score.")
        else:
            suggestions.append("Excellent ATS compatibility! Your resume is well-optimized for automated screening.")
        
        # Specific technical skill gaps
        if missing['critical_missing']:
            top_missing = missing['critical_missing'][:3]
            suggestions.append(f"IMMEDIATE ACTION: Add these critical skills to your resume: {', '.join(top_missing)}")
            suggestions.append(f"Create specific project examples or training certificates for: {', '.join(top_missing[:2])}")
        
        # Experience quantification
        if len(weaknesses.quantification_gaps) > 3:
            suggestions.append("Add specific metrics to your achievements (e.g., 'Improved system performance by 40%', 'Managed team of 5 developers')")
            suggestions.append("Replace generic statements with quantified results using numbers, percentages, or dollar amounts.")
        
        # Industry-specific advice
        if industry == 'software':
            if any(skill in missing['critical_missing'] for skill in ['python', 'javascript', 'react', 'node.js']):
                suggestions.append("For software roles: Highlight specific programming languages and frameworks in a dedicated 'Technical Skills' section.")
        
        # Formatting improvements
        if weaknesses.formatting_issues:
            suggestions.append(f"Resume structure issues: {', '.join(weaknesses.formatting_issues[:2])}")
        
        # Keyword density optimization
        if strengths.keyword_density_score < 0.6:
            suggestions.append("Increase keyword density by naturally incorporating job-specific terms throughout your experience descriptions.")
        
        # Missing soft skills
        if weaknesses.missing_soft_skills:
            suggestions.append(f"Add these soft skills with examples: {', '.join(weaknesses.missing_soft_skills[:3])}")
        
        return suggestions[:8]  # Return top 8 actionable suggestions
    
    # Helper methods for advanced analysis
    def _detect_industry(self, job_text: str) -> str:
        """Detect job industry from description"""
        industry_scores = {}
        
        for industry, keywords in self.industry_patterns.items():
            score = sum(1 for keyword in keywords if keyword in job_text)
            industry_scores[industry] = score
        
        return max(industry_scores, key=industry_scores.get) if industry_scores else 'general'
    
    def _detect_experience_level(self, job_text: str) -> str:
        """Detect required experience level"""
        for level, indicators in self.experience_indicators.items():
            if any(indicator in job_text for indicator in indicators):
                return level
        return 'mid'
    
    def _calculate_similarity(self, term1: str, term2: str) -> float:
        """Calculate semantic similarity between terms"""
        if term1 == term2:
            return 1.0
        if term1 in term2 or term2 in term1:
            return 0.9
        
        # Simple character-based similarity
        common_chars = set(term1) & set(term2)
        total_chars = set(term1) | set(term2)
        
        return len(common_chars) / len(total_chars) if total_chars else 0.0
    
    def _get_keyword_importance(self, keyword: str, category: str) -> float:
        """Get importance weight for a keyword"""
        base_weight = self.skill_categories.get(category, {}).get('weight', 0.5)
        
        # Boost importance for critical technical terms
        if keyword in ['python', 'java', 'javascript', 'react', 'aws', 'docker', 'kubernetes']:
            return min(1.0, base_weight + 0.2)
        
        return base_weight
    
    def _is_term_covered(self, term: str, resume_terms: List[str]) -> bool:
        """Check if term is covered in resume with fuzzy matching"""
        for resume_term in resume_terms:
            if self._calculate_similarity(term, resume_term) >= 0.8:
                return True
        return False
    
    def _calculate_keyword_density(self, resume_text: str, job_text: str) -> float:
        """Calculate keyword density score"""
        job_words = set(job_text.split())
        resume_words = set(resume_text.split())
        
        if not job_words:
            return 0.0
            
        common_words = job_words & resume_words
        return len(common_words) / len(job_words)
    
    def _calculate_industry_alignment(self, resume_text: str, industry: str) -> float:
        """Calculate how well resume aligns with industry"""
        if industry not in self.industry_patterns:
            return 0.5
            
        industry_keywords = self.industry_patterns[industry]
        matches = sum(1 for keyword in industry_keywords if keyword in resume_text)
        
        return min(1.0, matches / len(industry_keywords))
    
    def _calculate_experience_match(self, resume_text: str, required_level: str) -> float:
        """Calculate experience level alignment"""
        if required_level not in self.experience_indicators:
            return 0.5
            
        level_indicators = self.experience_indicators[required_level]
        matches = sum(1 for indicator in level_indicators if indicator in resume_text)
        
        return min(1.0, matches / len(level_indicators))
    
    def _calculate_impact_score(self, resume_text: str) -> float:
        """Calculate impact and quantification score"""
        # Count quantified achievements
        quantified_count = len(self._extract_quantified_achievements(resume_text))
        
        # Count impact verbs
        impact_count = sum(1 for verb in self.impact_verbs if verb in resume_text)
        
        # Calculate normalized score
        total_score = (quantified_count * 0.7) + (impact_count * 0.3)
        return min(1.0, total_score / 10)  # Normalize to 0-1
    
    def _assess_resume_formatting(self, resume_text: str) -> float:
        """Assess resume formatting and structure"""
        score = 1.0
        
        # Check for common sections
        sections = ['experience', 'education', 'skills', 'projects']
        section_score = sum(1 for section in sections if section in resume_text.lower())
        
        # Check text length (not too short, not too long)
        word_count = len(resume_text.split())
        if word_count < 100:
            score -= 0.3
        elif word_count > 2000:
            score -= 0.2
        
        # Normalize section score
        score = (section_score / len(sections)) * score
        
        return max(0.0, min(1.0, score))
    
    def _extract_quantified_achievements(self, text: str) -> List[str]:
        """Extract quantified achievements from resume"""
        patterns = [
            r'\d+%\s*(?:improvement|increase|decrease|reduction|growth|faster|better)',
            r'\$\d+(?:,\d+)*(?:k|m|million|billion)?',
            r'\d+(?:,\d+)*\s*(?:users|customers|clients|projects|applications|systems)',
            r'\d+(?:\.\d+)?x\s*(?:improvement|increase|faster|more)',
            r'saved\s*\$?\d+(?:,\d+)*',
            r'generated\s*\$?\d+(?:,\d+)*',
            r'managed\s*\$?\d+(?:,\d+)*\s*budget',
            r'team\s*of\s*\d+',
            r'\d+\s*(?:award|certification|patent)',
            r'ranked\s*#?\d+'
        ]
        
        achievements = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            achievements.extend(matches)
            
        return list(set(achievements))
    
    def _extract_education_advantages(self, resume_text: str, job_text: str) -> List[str]:
        """Extract education-related advantages"""
        education_terms = [
            'bachelor', 'master', 'phd', 'mba', 'degree', 'university',
            'college', 'certification', 'certified', 'diploma'
        ]
        
        advantages = []
        for term in education_terms:
            if term in resume_text and term in job_text:
                advantages.append(term)
                
        return advantages
    
    def _identify_missing_soft_skills(self, resume_text: str, job_text: str) -> List[str]:
        """Identify missing soft skills"""
        job_soft_skills = []
        resume_soft_skills = []
        
        soft_skills = self.skill_categories['soft_skills']['keywords']
        
        for skill in soft_skills:
            if skill in job_text:
                job_soft_skills.append(skill)
            if skill in resume_text:
                resume_soft_skills.append(skill)
        
        return [skill for skill in job_soft_skills if skill not in resume_soft_skills]
    
    def _identify_experience_gaps(self, resume_text: str, job_text: str) -> List[str]:
        """Identify experience-related gaps"""
        # Extract years of experience mentioned in job
        job_years = re.findall(r'(\d+)\+?\s*years?', job_text)
        resume_years = re.findall(r'(\d+)\+?\s*years?', resume_text)
        
        gaps = []
        
        if job_years and resume_years:
            required = int(job_years[0]) if job_years else 0
            available = int(resume_years[0]) if resume_years else 0
            
            if available < required:
                gaps.append(f"Experience gap: {required - available} years short")
        
        # Check for specific experience types
        experience_types = ['management', 'leadership', 'senior', 'architect', 'principal']
        for exp_type in experience_types:
            if exp_type in job_text and exp_type not in resume_text:
                gaps.append(f"Missing {exp_type} experience")
                
        return gaps
    
    def _identify_education_gaps(self, resume_text: str, job_text: str) -> List[str]:
        """Identify education-related gaps"""
        education_requirements = ['bachelor', 'master', 'phd', 'mba', 'degree']
        gaps = []
        
        for req in education_requirements:
            if req in job_text and req not in resume_text:
                gaps.append(f"Missing {req} degree requirement")
                
        return gaps
    
    def _assess_formatting_issues(self, resume_text: str) -> List[str]:
        """Assess potential formatting issues"""
        issues = []
        
        # Check for extremely long paragraphs
        paragraphs = resume_text.split('\n')
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 50]
        if len(long_paragraphs) > 3:
            issues.append("Use bullet points instead of long paragraphs")
        
        # Check for missing contact information patterns
        if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
            issues.append("Add professional email address")
            
        if not re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', resume_text):
            issues.append("Include phone number")
            
        # Check for weak action verbs
        weak_verbs = ['responsible for', 'worked on', 'helped with', 'involved in']
        if any(verb in resume_text.lower() for verb in weak_verbs):
            issues.append("Replace weak verbs with strong action verbs")
            
        return issues
    
    def _identify_quantification_gaps(self, resume_text: str) -> List[str]:
        """Identify areas lacking quantification"""
        gaps = []
        
        # Look for statements that could be quantified
        unquantified_patterns = [
            r'improved\s+(?!\d+%|by\s*\d+)',
            r'increased\s+(?!\d+%|by\s*\d+)',
            r'reduced\s+(?!\d+%|by\s*\d+)',
            r'managed\s+(?!\d+|team\s*of\s*\d+)',
            r'led\s+(?!\d+|team\s*of\s*\d+)',
            r'developed\s+(?!\d+)',
            r'created\s+(?!\d+)'
        ]
        
        for pattern in unquantified_patterns:
            if re.search(pattern, resume_text, re.IGNORECASE):
                verb = pattern.split('\\')[0]
                gaps.append(f"Quantify '{verb}' achievements with specific numbers or percentages")
                
        return list(set(gaps))