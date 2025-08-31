import re
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from PyPDF2 import PdfReader
import logging

# Simple fallback without NLTK/spaCy for basic functionality
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ExtractedInfo:
    """Data class for extracted resume information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    skills: List[str] = None
    education: List[Dict[str, str]] = None
    experience: List[Dict[str, str]] = None
    certifications: List[str] = None
    languages: List[str] = None
    projects: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.education is None:
            self.education = []
        if self.experience is None:
            self.experience = []
        if self.certifications is None:
            self.certifications = []
        if self.languages is None:
            self.languages = []
        if self.projects is None:
            self.projects = []


class ResumeParser:
    """Main class for parsing resumes using NLP techniques."""
    
    def __init__(self):
        """Initialize the parser with basic functionality."""
        # Simplified initialization without spaCy
        self.nlp = None
        self.skills_database = self._load_skills_database()
        self.degree_patterns = self._compile_degree_patterns()
        self.experience_patterns = self._compile_experience_patterns()
    
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """Load comprehensive skills database categorized by domain."""
        return {
            'programming_languages': [
                'Python', 'Java', 'JavaScript', 'C++', 'C#', 'C', 'PHP', 'Ruby', 'Go', 'Rust',
                'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Shell', 'PowerShell'
            ],
            'web_technologies': [
                'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js', 'Django',
                'Flask', 'Spring Boot', 'ASP.NET', 'Laravel', 'Bootstrap', 'Tailwind CSS',
                'TypeScript', 'jQuery', 'SASS', 'LESS'
            ],
            'databases': [
                'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Oracle', 'SQL Server', 'Redis',
                'Cassandra', 'DynamoDB', 'Neo4j', 'Elasticsearch', 'Firebase'
            ],
            'cloud_platforms': [
                'AWS', 'Azure', 'Google Cloud', 'Heroku', 'DigitalOcean', 'Linode',
                'IBM Cloud', 'Oracle Cloud', 'Alibaba Cloud'
            ],
            'devops_tools': [
                'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 'GitLab', 'Terraform',
                'Ansible', 'Chef', 'Puppet', 'Vagrant', 'Travis CI', 'CircleCI'
            ],
            'data_science': [
                'Machine Learning', 'Deep Learning', 'Data Analysis', 'Statistics',
                'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Matplotlib',
                'Seaborn', 'Tableau', 'Power BI', 'Apache Spark', 'Hadoop'
            ],
            'mobile_development': [
                'Android', 'iOS', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
                'PhoneGap', 'Cordova'
            ],
            'soft_skills': [
                'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking',
                'Project Management', 'Time Management', 'Analytical Skills', 'Creativity',
                'Adaptability', 'Collaboration', 'Public Speaking'
            ]
        }
    
    def _compile_degree_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for detecting educational qualifications."""
        degree_patterns = [
            r'(?i)\b(?:bachelor|b\.?[asc]\.?|bs|ba|bsc|be|btech|btec)\b.*?(?:in|of)?\s*([^,\n.]+)',
            r'(?i)\b(?:master|m\.?[asc]\.?|ms|ma|msc|me|mtech|mba|mfa)\b.*?(?:in|of)?\s*([^,\n.]+)',
            r'(?i)\b(?:phd|ph\.?d\.?|doctorate|doctoral)\b.*?(?:in|of)?\s*([^,\n.]+)',
            r'(?i)\b(?:associate|diploma|certificate)\b.*?(?:in|of)?\s*([^,\n.]+)'
        ]
        return [re.compile(pattern) for pattern in degree_patterns]
    
    def _compile_experience_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for detecting work experience."""
        experience_patterns = [
            r'(?i)(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?i)(?:experience|exp).*?(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
            r'(?i)(\d{4})\s*[-–]\s*(\d{4}|\w+)',  # Date ranges
            r'(?i)(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|\w+)'  # Month Year ranges
        ]
        return [re.compile(pattern) for pattern in experience_patterns]
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats."""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_text_from_pdf(file_path)
            elif file_extension in ['.doc', '.docx']:
                return self._extract_text_from_docx(file_path)
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                # Try textract for other formats
                return textract.process(file_path).decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        if not DOCX_AVAILABLE:
            logger.warning("python-docx not available. Cannot process DOCX files.")
            return ""
        
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            return ""
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Main method to parse resume and extract structured information."""
        text = self.extract_text_from_file(file_path)
        if not text:
            return {
                'raw_text': '',
                'extracted_info': ExtractedInfo()
            }
        
        extracted_info = ExtractedInfo()
        
        # Extract basic contact information
        extracted_info.name = self._extract_name(text)
        extracted_info.email = self._extract_email(text)
        extracted_info.phone = self._extract_phone(text)
        extracted_info.address = self._extract_address(text)
        
        # Extract skills
        extracted_info.skills = self._extract_skills(text)
        
        # Extract education
        extracted_info.education = self._extract_education(text)
        
        # Extract work experience
        extracted_info.experience = self._extract_experience(text)
        
        # Extract certifications
        extracted_info.certifications = self._extract_certifications(text)
        
        # Extract languages
        extracted_info.languages = self._extract_languages(text)
        
        # Extract projects
        extracted_info.projects = self._extract_projects(text)
        
        return {
            'raw_text': text,
            'extracted_info': extracted_info
        }
    
    def _extract_name(self, text: str) -> Optional[str]:
        """Extract person's name from resume text."""
        lines = text.split('\n')
        
        # Look for name in first few lines
        for i, line in enumerate(lines[:5]):
            line = line.strip()
            if len(line) > 0 and len(line.split()) <= 4:
                # Check if line looks like a name (no special characters, proper length)
                if re.match(r'^[A-Za-z\s.]+$', line) and 2 <= len(line.split()) <= 4:
                    return line.title()
        
        # Use NLP to find person names
        if self.nlp:
            doc = self.nlp(text[:500])  # Check first 500 characters
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text.title()
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from resume text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume text."""
        phone_patterns = [
            r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'(\+\d{1,3}[-.\s]?)?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'(\+\d{1,3}[-.\s]?)?\d{10}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0] if isinstance(phones[0], str) else ''.join(phones[0])
        
        return None
    
    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address from resume text."""
        # Look for address patterns
        address_patterns = [
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)',
            r'[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}',  # City, State ZIP
            r'[A-Za-z\s]+,\s*[A-Za-z\s]+\s+\d{5,6}'  # City, Country/State Postal
        ]
        
        for pattern in address_patterns:
            addresses = re.findall(pattern, text, re.IGNORECASE)
            if addresses:
                return addresses[0]
        
        return None
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text."""
        found_skills = []
        text_lower = text.lower()
        
        # Check against skills database
        for category, skills in self.skills_database.items():
            for skill in skills:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_skills))
    
    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume text."""
        education = []
        
        # Find education section
        education_section = self._find_section(text, ['education', 'academic', 'qualification'])
        
        if education_section:
            for pattern in self.degree_patterns:
                matches = pattern.findall(education_section)
                for match in matches:
                    degree_info = {
                        'degree': match.strip() if isinstance(match, str) else match[0].strip(),
                        'institution': '',
                        'year': ''
                    }
                    
                    # Try to find institution and year nearby
                    # This is a simplified extraction - could be enhanced
                    education.append(degree_info)
        
        return education
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from resume text."""
        experience = []
        
        # Find experience section
        experience_section = self._find_section(text, ['experience', 'work', 'employment', 'career'])
        
        if experience_section:
            # Split by common delimiters and extract job entries
            lines = experience_section.split('\n')
            current_job = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for job titles (lines that might be job titles)
                if self._looks_like_job_title(line):
                    if current_job:
                        experience.append(current_job)
                    current_job = {'title': line, 'company': '', 'duration': '', 'description': ''}
                elif current_job and not current_job.get('company'):
                    # Next line might be company
                    current_job['company'] = line
                elif current_job:
                    # Add to description
                    current_job['description'] += line + ' '
            
            if current_job:
                experience.append(current_job)
        
        return experience
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume text."""
        certifications = []
        
        # Common certification patterns
        cert_patterns = [
            r'(?i)(AWS|Amazon Web Services)\s+(?:Certified\s+)?([A-Za-z\s]+)',
            r'(?i)(Microsoft|Google|Oracle|Cisco)\s+(?:Certified\s+)?([A-Za-z\s]+)',
            r'(?i)Certified\s+([A-Za-z\s]+)',
            r'(?i)(PMP|CISSP|CISA|CISM|CompTIA)',
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    cert = ' '.join(match).strip()
                else:
                    cert = match.strip()
                if cert:
                    certifications.append(cert)
        
        return list(set(certifications))  # Remove duplicates
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from resume text."""
        languages = []
        
        # Common languages
        language_list = [
            'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Russian',
            'Chinese', 'Japanese', 'Korean', 'Arabic', 'Hindi', 'Bengali', 'Urdu'
        ]
        
        text_lower = text.lower()
        for language in language_list:
            if language.lower() in text_lower:
                languages.append(language)
        
        return languages
    
    def _extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information from resume text."""
        projects = []
        
        # Find projects section
        projects_section = self._find_section(text, ['projects', 'project work', 'personal projects'])
        
        if projects_section:
            # This is a simplified extraction - could be enhanced
            lines = projects_section.split('\n')
            current_project = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if self._looks_like_project_title(line):
                    if current_project:
                        projects.append(current_project)
                    current_project = {'title': line, 'description': '', 'technologies': ''}
                elif current_project:
                    current_project['description'] += line + ' '
            
            if current_project:
                projects.append(current_project)
        
        return projects
    
    def _find_section(self, text: str, section_keywords: List[str]) -> str:
        """Find and extract a specific section from resume text."""
        lines = text.split('\n')
        section_start = -1
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            for keyword in section_keywords:
                if keyword in line_lower and len(line_lower) < 50:  # Likely a section header
                    section_start = i
                    break
            if section_start != -1:
                break
        
        if section_start == -1:
            return ""
        
        # Find section end (next section or end of text)
        section_end = len(lines)
        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip().lower()
            # Check if this might be another section header
            if (line and len(line) < 50 and 
                any(keyword in line for keyword in ['experience', 'education', 'skills', 'projects', 'certifications'])):
                section_end = i
                break
        
        return '\n'.join(lines[section_start:section_end])
    
    def _looks_like_job_title(self, line: str) -> bool:
        """Heuristic to determine if a line looks like a job title."""
        line = line.strip()
        if not line or len(line) > 100:
            return False
        
        # Common job title indicators
        job_indicators = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator', 'director', 'lead']
        line_lower = line.lower()
        
        return any(indicator in line_lower for indicator in job_indicators)
    
    def _looks_like_project_title(self, line: str) -> bool:
        """Heuristic to determine if a line looks like a project title."""
        line = line.strip()
        if not line or len(line) > 80:
            return False
        
        # Project title indicators
        project_indicators = ['system', 'application', 'website', 'platform', 'tool', 'dashboard', 'app']
        line_lower = line.lower()
        
        return any(indicator in line_lower for indicator in project_indicators) or line.istitle()


# Initialize global parser instance
resume_parser = ResumeParser()