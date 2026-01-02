"""
Data Models for CV Generator

Clean, immutable data classes representing domain entities.
Following Single Responsibility Principle - each model represents one concept.

Author: El Moujahid Marouane
Version: 1.0
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date
from enum import Enum


class SkillCategory(Enum):
    """Categories for skills."""
    TECHNICAL = "technical"
    SOFT = "soft"
    LANGUAGE = "language"
    TOOL = "tool"
    FRAMEWORK = "framework"
    OTHER = "other"


class ProficiencyLevel(Enum):
    """Proficiency levels for skills."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Skill:
    """Represents a skill with category and proficiency."""
    id: Optional[int] = None
    name: str = ""
    category: SkillCategory = SkillCategory.TECHNICAL
    proficiency: ProficiencyLevel = ProficiencyLevel.INTERMEDIATE
    years_experience: float = 0.0
    keywords: List[str] = field(default_factory=list)  # Related keywords for matching
    description: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category.value,
            'proficiency': self.proficiency.value,
            'years_experience': self.years_experience,
            'keywords': self.keywords,
            'description': self.description,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Skill':
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            category=SkillCategory(data.get('category', 'technical')),
            proficiency=ProficiencyLevel(data.get('proficiency', 'intermediate')),
            years_experience=data.get('years_experience', 0.0),
            keywords=data.get('keywords', []),
            description=data.get('description'),
        )


@dataclass
class Project:
    """Represents a project in the user's portfolio."""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    role: str = ""
    technologies: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)  # Key achievements/outcomes
    url: Optional[str] = None
    github_url: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_ongoing: bool = False
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'role': self.role,
            'technologies': self.technologies,
            'highlights': self.highlights,
            'url': self.url,
            'github_url': self.github_url,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_ongoing': self.is_ongoing,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            role=data.get('role', ''),
            technologies=data.get('technologies', []),
            highlights=data.get('highlights', []),
            url=data.get('url'),
            github_url=data.get('github_url'),
            start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            is_ongoing=data.get('is_ongoing', False),
        )


@dataclass
class Education:
    """Represents an educational background entry."""
    id: Optional[int] = None
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_ongoing: bool = False
    gpa: Optional[float] = None
    achievements: List[str] = field(default_factory=list)
    relevant_coursework: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'institution': self.institution,
            'degree': self.degree,
            'field_of_study': self.field_of_study,
            'location': self.location,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_ongoing': self.is_ongoing,
            'gpa': self.gpa,
            'achievements': self.achievements,
            'relevant_coursework': self.relevant_coursework,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Education':
        return cls(
            id=data.get('id'),
            institution=data.get('institution', ''),
            degree=data.get('degree', ''),
            field_of_study=data.get('field_of_study', ''),
            location=data.get('location'),
            start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            is_ongoing=data.get('is_ongoing', False),
            gpa=data.get('gpa'),
            achievements=data.get('achievements', []),
            relevant_coursework=data.get('relevant_coursework', []),
        )


@dataclass
class Experience:
    """Represents a work experience entry."""
    id: Optional[int] = None
    company: str = ""
    position: str = ""
    location: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: bool = False
    description: str = ""
    responsibilities: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    technologies_used: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'company': self.company,
            'position': self.position,
            'location': self.location,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'description': self.description,
            'responsibilities': self.responsibilities,
            'achievements': self.achievements,
            'technologies_used': self.technologies_used,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Experience':
        return cls(
            id=data.get('id'),
            company=data.get('company', ''),
            position=data.get('position', ''),
            location=data.get('location'),
            start_date=date.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=date.fromisoformat(data['end_date']) if data.get('end_date') else None,
            is_current=data.get('is_current', False),
            description=data.get('description', ''),
            responsibilities=data.get('responsibilities', []),
            achievements=data.get('achievements', []),
            technologies_used=data.get('technologies_used', []),
        )


@dataclass
class PersonalInfo:
    """Personal information for the CV header."""
    id: Optional[int] = None
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: str = ""  # Professional summary/objective
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'summary': self.summary,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PersonalInfo':
        return cls(
            id=data.get('id'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            country=data.get('country'),
            linkedin_url=data.get('linkedin_url'),
            github_url=data.get('github_url'),
            portfolio_url=data.get('portfolio_url'),
            summary=data.get('summary', ''),
        )


@dataclass
class UserProfile:
    """Complete user profile aggregating all components."""
    id: Optional[int] = None
    personal_info: PersonalInfo = field(default_factory=PersonalInfo)
    skills: List[Skill] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[dict] = field(default_factory=list)  # [{name, level}]
    interests: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """Get skills filtered by category."""
        return [s for s in self.skills if s.category == category]
    
    @property
    def technical_skills(self) -> List[Skill]:
        return self.get_skills_by_category(SkillCategory.TECHNICAL)
    
    @property
    def soft_skills(self) -> List[Skill]:
        return self.get_skills_by_category(SkillCategory.SOFT)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'personal_info': self.personal_info.to_dict(),
            'skills': [s.to_dict() for s in self.skills],
            'projects': [p.to_dict() for p in self.projects],
            'education': [e.to_dict() for e in self.education],
            'experience': [e.to_dict() for e in self.experience],
            'certifications': self.certifications,
            'languages': self.languages,
            'interests': self.interests,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserProfile':
        return cls(
            id=data.get('id'),
            personal_info=PersonalInfo.from_dict(data.get('personal_info', {})),
            skills=[Skill.from_dict(s) for s in data.get('skills', [])],
            projects=[Project.from_dict(p) for p in data.get('projects', [])],
            education=[Education.from_dict(e) for e in data.get('education', [])],
            experience=[Experience.from_dict(e) for e in data.get('experience', [])],
            certifications=data.get('certifications', []),
            languages=data.get('languages', []),
            interests=data.get('interests', []),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
        )


@dataclass
class MatchResult:
    """Result of matching a profile against a job offer."""
    overall_score: float = 0.0  # 0-100
    matched_skills: List[Skill] = field(default_factory=list)
    matched_projects: List[Project] = field(default_factory=list)
    skill_gaps: List[str] = field(default_factory=list)  # Skills in job but not in profile
    priority_skills: List[Skill] = field(default_factory=list)  # Top skills to highlight
    priority_projects: List[Project] = field(default_factory=list)  # Top projects to highlight
    relevant_experience: List[Experience] = field(default_factory=list)
    keyword_matches: dict = field(default_factory=dict)  # {keyword: count}
    
    def to_dict(self) -> dict:
        return {
            'overall_score': self.overall_score,
            'matched_skills': [s.to_dict() for s in self.matched_skills],
            'matched_projects': [p.to_dict() for p in self.matched_projects],
            'skill_gaps': self.skill_gaps,
            'priority_skills': [s.to_dict() for s in self.priority_skills],
            'priority_projects': [p.to_dict() for p in self.priority_projects],
            'relevant_experience': [e.to_dict() for e in self.relevant_experience],
            'keyword_matches': self.keyword_matches,
        }


@dataclass
class GeneratedDocument:
    """Represents a generated CV or cover letter."""
    id: Optional[int] = None
    document_type: str = "cv"  # "cv" or "cover_letter"
    internship_id: Optional[int] = None
    company_name: str = ""
    job_title: str = ""
    content: str = ""  # Raw text content
    latex_content: str = ""  # Rendered LaTeX
    pdf_path: Optional[str] = None
    match_score: float = 0.0
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'document_type': self.document_type,
            'internship_id': self.internship_id,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'content': self.content,
            'latex_content': self.latex_content,
            'pdf_path': self.pdf_path,
            'match_score': self.match_score,
            'created_at': self.created_at,
        }
