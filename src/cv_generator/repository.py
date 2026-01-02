"""
Repository Pattern for CV Generator

Handles data persistence following the Repository Pattern.
Single Responsibility: Database operations only.

Author: El Moujahid Marouane
Version: 1.0
"""

import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod

from .models import (
    UserProfile, PersonalInfo, Skill, Project, 
    Education, Experience, GeneratedDocument,
    SkillCategory, ProficiencyLevel
)

try:
    from ..logger_setup import get_logger
    from ..config import settings
except ImportError:
    from src.logger_setup import get_logger
    from src.config import settings

logger = get_logger("cv_generator.repository")


class BaseRepository(ABC):
    """Abstract base repository with common database operations."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or getattr(settings, 'DATABASE_PATH', 'data/internship_sync_new.db')
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


class ProfileRepository(BaseRepository):
    """Repository for user profile data operations."""
    
    def __init__(self, db_path: str = None):
        super().__init__(db_path)
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create CV generator tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Personal Info table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cv_personal_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    address TEXT,
                    city TEXT,
                    country TEXT,
                    linkedin_url TEXT,
                    github_url TEXT,
                    portfolio_url TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Skills table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cv_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    name TEXT NOT NULL,
                    category TEXT DEFAULT 'technical',
                    proficiency TEXT DEFAULT 'intermediate',
                    years_experience REAL DEFAULT 0,
                    keywords TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES cv_personal_info(id) ON DELETE CASCADE
                )
            """)
            
            # Projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cv_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    role TEXT,
                    technologies TEXT,
                    highlights TEXT,
                    url TEXT,
                    github_url TEXT,
                    start_date DATE,
                    end_date DATE,
                    is_ongoing BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES cv_personal_info(id) ON DELETE CASCADE
                )
            """)
            
            # Education table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cv_education (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    institution TEXT NOT NULL,
                    degree TEXT NOT NULL,
                    field_of_study TEXT,
                    location TEXT,
                    start_date DATE,
                    end_date DATE,
                    is_ongoing BOOLEAN DEFAULT FALSE,
                    gpa REAL,
                    achievements TEXT,
                    relevant_coursework TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES cv_personal_info(id) ON DELETE CASCADE
                )
            """)
            
            # Experience table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cv_experience (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    company TEXT NOT NULL,
                    position TEXT NOT NULL,
                    location TEXT,
                    start_date DATE,
                    end_date DATE,
                    is_current BOOLEAN DEFAULT FALSE,
                    description TEXT,
                    responsibilities TEXT,
                    achievements TEXT,
                    technologies_used TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES cv_personal_info(id) ON DELETE CASCADE
                )
            """)
            
            # Profile metadata table (certifications, languages, interests)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cv_profile_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER UNIQUE,
                    certifications TEXT,
                    languages TEXT,
                    interests TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES cv_personal_info(id) ON DELETE CASCADE
                )
            """)
            
            # Generated documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cv_generated_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER,
                    internship_id INTEGER,
                    document_type TEXT DEFAULT 'cv',
                    company_name TEXT,
                    job_title TEXT,
                    content TEXT,
                    latex_content TEXT,
                    pdf_path TEXT,
                    match_score REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES cv_personal_info(id) ON DELETE CASCADE,
                    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE SET NULL
                )
            """)
            
            conn.commit()
            logger.info("CV Generator tables initialized")
    
    # =========================================================================
    # PERSONAL INFO CRUD
    # =========================================================================
    
    def create_personal_info(self, info: PersonalInfo) -> int:
        """Create personal info record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cv_personal_info 
                (first_name, last_name, email, phone, address, city, country,
                 linkedin_url, github_url, portfolio_url, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                info.first_name, info.last_name, info.email, info.phone,
                info.address, info.city, info.country, info.linkedin_url,
                info.github_url, info.portfolio_url, info.summary
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_personal_info(self, profile_id: int) -> Optional[PersonalInfo]:
        """Get personal info by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cv_personal_info WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            if row:
                return PersonalInfo(
                    id=row['id'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row['email'],
                    phone=row['phone'],
                    address=row['address'],
                    city=row['city'],
                    country=row['country'],
                    linkedin_url=row['linkedin_url'],
                    github_url=row['github_url'],
                    portfolio_url=row['portfolio_url'],
                    summary=row['summary'],
                )
            return None
    
    def get_default_profile_id(self) -> Optional[int]:
        """Get the first profile ID (single-user mode)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cv_personal_info ORDER BY id LIMIT 1")
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def update_personal_info(self, info: PersonalInfo) -> bool:
        """Update personal info."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cv_personal_info SET
                    first_name = ?, last_name = ?, email = ?, phone = ?,
                    address = ?, city = ?, country = ?, linkedin_url = ?,
                    github_url = ?, portfolio_url = ?, summary = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                info.first_name, info.last_name, info.email, info.phone,
                info.address, info.city, info.country, info.linkedin_url,
                info.github_url, info.portfolio_url, info.summary, info.id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    # =========================================================================
    # SKILLS CRUD
    # =========================================================================
    
    def add_skill(self, profile_id: int, skill: Skill) -> int:
        """Add a skill to a profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cv_skills 
                (profile_id, name, category, proficiency, years_experience, keywords, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id, skill.name, skill.category.value, skill.proficiency.value,
                skill.years_experience, json.dumps(skill.keywords), skill.description
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_skills(self, profile_id: int) -> List[Skill]:
        """Get all skills for a profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cv_skills WHERE profile_id = ?", (profile_id,))
            skills = []
            for row in cursor.fetchall():
                skills.append(Skill(
                    id=row['id'],
                    name=row['name'],
                    category=SkillCategory(row['category']),
                    proficiency=ProficiencyLevel(row['proficiency']),
                    years_experience=row['years_experience'] or 0,
                    keywords=json.loads(row['keywords']) if row['keywords'] else [],
                    description=row['description'],
                ))
            return skills
    
    def update_skill(self, skill: Skill) -> bool:
        """Update a skill."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cv_skills SET
                    name = ?, category = ?, proficiency = ?, years_experience = ?,
                    keywords = ?, description = ?
                WHERE id = ?
            """, (
                skill.name, skill.category.value, skill.proficiency.value,
                skill.years_experience, json.dumps(skill.keywords), skill.description, skill.id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_skill(self, skill_id: int) -> bool:
        """Delete a skill."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cv_skills WHERE id = ?", (skill_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # =========================================================================
    # PROJECTS CRUD
    # =========================================================================
    
    def add_project(self, profile_id: int, project: Project) -> int:
        """Add a project to a profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cv_projects 
                (profile_id, name, description, role, technologies, highlights,
                 url, github_url, start_date, end_date, is_ongoing)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id, project.name, project.description, project.role,
                json.dumps(project.technologies), json.dumps(project.highlights),
                project.url, project.github_url,
                project.start_date.isoformat() if project.start_date else None,
                project.end_date.isoformat() if project.end_date else None,
                project.is_ongoing
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_projects(self, profile_id: int) -> List[Project]:
        """Get all projects for a profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cv_projects WHERE profile_id = ? ORDER BY start_date DESC", (profile_id,))
            projects = []
            for row in cursor.fetchall():
                from datetime import date
                projects.append(Project(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or '',
                    role=row['role'] or '',
                    technologies=json.loads(row['technologies']) if row['technologies'] else [],
                    highlights=json.loads(row['highlights']) if row['highlights'] else [],
                    url=row['url'],
                    github_url=row['github_url'],
                    start_date=date.fromisoformat(row['start_date']) if row['start_date'] else None,
                    end_date=date.fromisoformat(row['end_date']) if row['end_date'] else None,
                    is_ongoing=bool(row['is_ongoing']),
                ))
            return projects
    
    def update_project(self, project: Project) -> bool:
        """Update a project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cv_projects SET
                    name = ?, description = ?, role = ?, technologies = ?, highlights = ?,
                    url = ?, github_url = ?, start_date = ?, end_date = ?, is_ongoing = ?
                WHERE id = ?
            """, (
                project.name, project.description, project.role,
                json.dumps(project.technologies), json.dumps(project.highlights),
                project.url, project.github_url,
                project.start_date.isoformat() if project.start_date else None,
                project.end_date.isoformat() if project.end_date else None,
                project.is_ongoing, project.id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cv_projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # =========================================================================
    # EDUCATION CRUD
    # =========================================================================
    
    def add_education(self, profile_id: int, education: Education) -> int:
        """Add education entry to a profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cv_education 
                (profile_id, institution, degree, field_of_study, location,
                 start_date, end_date, is_ongoing, gpa, achievements, relevant_coursework)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id, education.institution, education.degree, education.field_of_study,
                education.location,
                education.start_date.isoformat() if education.start_date else None,
                education.end_date.isoformat() if education.end_date else None,
                education.is_ongoing, education.gpa,
                json.dumps(education.achievements), json.dumps(education.relevant_coursework)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_education(self, profile_id: int) -> List[Education]:
        """Get all education entries for a profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cv_education WHERE profile_id = ? ORDER BY start_date DESC", (profile_id,))
            entries = []
            for row in cursor.fetchall():
                from datetime import date
                entries.append(Education(
                    id=row['id'],
                    institution=row['institution'],
                    degree=row['degree'],
                    field_of_study=row['field_of_study'] or '',
                    location=row['location'],
                    start_date=date.fromisoformat(row['start_date']) if row['start_date'] else None,
                    end_date=date.fromisoformat(row['end_date']) if row['end_date'] else None,
                    is_ongoing=bool(row['is_ongoing']),
                    gpa=row['gpa'],
                    achievements=json.loads(row['achievements']) if row['achievements'] else [],
                    relevant_coursework=json.loads(row['relevant_coursework']) if row['relevant_coursework'] else [],
                ))
            return entries
    
    def update_education(self, education: Education) -> bool:
        """Update an education entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cv_education SET
                    institution = ?, degree = ?, field_of_study = ?, location = ?,
                    start_date = ?, end_date = ?, is_ongoing = ?, gpa = ?,
                    achievements = ?, relevant_coursework = ?
                WHERE id = ?
            """, (
                education.institution, education.degree, education.field_of_study,
                education.location,
                education.start_date.isoformat() if education.start_date else None,
                education.end_date.isoformat() if education.end_date else None,
                education.is_ongoing, education.gpa,
                json.dumps(education.achievements), json.dumps(education.relevant_coursework),
                education.id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_education(self, education_id: int) -> bool:
        """Delete an education entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cv_education WHERE id = ?", (education_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # =========================================================================
    # EXPERIENCE CRUD
    # =========================================================================
    
    def add_experience(self, profile_id: int, experience: Experience) -> int:
        """Add experience entry to a profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cv_experience 
                (profile_id, company, position, location, start_date, end_date,
                 is_current, description, responsibilities, achievements, technologies_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id, experience.company, experience.position, experience.location,
                experience.start_date.isoformat() if experience.start_date else None,
                experience.end_date.isoformat() if experience.end_date else None,
                experience.is_current, experience.description,
                json.dumps(experience.responsibilities), json.dumps(experience.achievements),
                json.dumps(experience.technologies_used)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_experience(self, profile_id: int) -> List[Experience]:
        """Get all experience entries for a profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cv_experience WHERE profile_id = ? ORDER BY start_date DESC", (profile_id,))
            entries = []
            for row in cursor.fetchall():
                from datetime import date
                entries.append(Experience(
                    id=row['id'],
                    company=row['company'],
                    position=row['position'],
                    location=row['location'],
                    start_date=date.fromisoformat(row['start_date']) if row['start_date'] else None,
                    end_date=date.fromisoformat(row['end_date']) if row['end_date'] else None,
                    is_current=bool(row['is_current']),
                    description=row['description'] or '',
                    responsibilities=json.loads(row['responsibilities']) if row['responsibilities'] else [],
                    achievements=json.loads(row['achievements']) if row['achievements'] else [],
                    technologies_used=json.loads(row['technologies_used']) if row['technologies_used'] else [],
                ))
            return entries
    
    def update_experience(self, experience: Experience) -> bool:
        """Update an experience entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cv_experience SET
                    company = ?, position = ?, location = ?, start_date = ?, end_date = ?,
                    is_current = ?, description = ?, responsibilities = ?, achievements = ?,
                    technologies_used = ?
                WHERE id = ?
            """, (
                experience.company, experience.position, experience.location,
                experience.start_date.isoformat() if experience.start_date else None,
                experience.end_date.isoformat() if experience.end_date else None,
                experience.is_current, experience.description,
                json.dumps(experience.responsibilities), json.dumps(experience.achievements),
                json.dumps(experience.technologies_used), experience.id
            ))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_experience(self, experience_id: int) -> bool:
        """Delete an experience entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cv_experience WHERE id = ?", (experience_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # =========================================================================
    # PROFILE METADATA (certifications, languages, interests)
    # =========================================================================
    
    def get_metadata(self, profile_id: int) -> Dict[str, Any]:
        """Get profile metadata."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cv_profile_metadata WHERE profile_id = ?", (profile_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'certifications': json.loads(row['certifications']) if row['certifications'] else [],
                    'languages': json.loads(row['languages']) if row['languages'] else [],
                    'interests': json.loads(row['interests']) if row['interests'] else [],
                }
            return {'certifications': [], 'languages': [], 'interests': []}
    
    def save_metadata(self, profile_id: int, certifications: List[str], 
                      languages: List[dict], interests: List[str]) -> bool:
        """Save profile metadata (upsert)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cv_profile_metadata (profile_id, certifications, languages, interests)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(profile_id) DO UPDATE SET
                    certifications = excluded.certifications,
                    languages = excluded.languages,
                    interests = excluded.interests,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                profile_id, json.dumps(certifications), 
                json.dumps(languages), json.dumps(interests)
            ))
            conn.commit()
            return True
    
    # =========================================================================
    # FULL PROFILE OPERATIONS
    # =========================================================================
    
    def get_full_profile(self, profile_id: int) -> Optional[UserProfile]:
        """Get complete user profile with all components."""
        personal_info = self.get_personal_info(profile_id)
        if not personal_info:
            return None
        
        metadata = self.get_metadata(profile_id)
        
        return UserProfile(
            id=profile_id,
            personal_info=personal_info,
            skills=self.get_skills(profile_id),
            projects=self.get_projects(profile_id),
            education=self.get_education(profile_id),
            experience=self.get_experience(profile_id),
            certifications=metadata.get('certifications', []),
            languages=metadata.get('languages', []),
            interests=metadata.get('interests', []),
        )
    
    # =========================================================================
    # GENERATED DOCUMENTS
    # =========================================================================
    
    def save_generated_document(self, profile_id: int, doc: GeneratedDocument) -> int:
        """Save a generated document."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cv_generated_documents 
                (profile_id, internship_id, document_type, company_name, job_title,
                 content, latex_content, pdf_path, match_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id, doc.internship_id, doc.document_type, doc.company_name,
                doc.job_title, doc.content, doc.latex_content, doc.pdf_path, doc.match_score
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_generated_documents(self, profile_id: int, limit: int = 20) -> List[GeneratedDocument]:
        """Get recent generated documents."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM cv_generated_documents 
                WHERE profile_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (profile_id, limit))
            docs = []
            for row in cursor.fetchall():
                docs.append(GeneratedDocument(
                    id=row['id'],
                    document_type=row['document_type'],
                    internship_id=row['internship_id'],
                    company_name=row['company_name'] or '',
                    job_title=row['job_title'] or '',
                    content=row['content'] or '',
                    latex_content=row['latex_content'] or '',
                    pdf_path=row['pdf_path'],
                    match_score=row['match_score'] or 0,
                    created_at=row['created_at'],
                ))
            return docs
