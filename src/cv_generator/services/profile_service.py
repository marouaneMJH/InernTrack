"""
Profile Service

Handles user profile management operations.
Single Responsibility: Profile CRUD operations.

Author: El Moujahid Marouane
Version: 1.0
"""

from typing import Optional, List
from dataclasses import dataclass

from ..repository import ProfileRepository
from ..models import (
    UserProfile, PersonalInfo, Skill, Project, 
    Education, Experience, SkillCategory, ProficiencyLevel
)

try:
    from ...logger_setup import get_logger
except ImportError:
    from src.logger_setup import get_logger

logger = get_logger("cv_generator.profile_service")


@dataclass
class ServiceResult:
    """Result wrapper for service operations."""
    success: bool
    data: any = None
    error: Optional[str] = None
    status_code: int = 200
    
    def __post_init__(self):
        """Set status_code based on success if not explicitly provided."""
        if self.status_code == 200 and not self.success:
            self.status_code = 400


class ProfileService:
    """
    Service for managing user profiles.
    
    Provides high-level operations for profile management
    following the Single Responsibility Principle.
    """
    
    def __init__(self, repository: ProfileRepository = None):
        self.repo = repository or ProfileRepository()
    
    # =========================================================================
    # PROFILE OPERATIONS
    # =========================================================================
    
    def get_or_create_profile(self) -> ServiceResult:
        """
        Get the default profile or create one if none exists.
        Single-user mode: assumes one profile per installation.
        """
        try:
            profile_id = self.repo.get_default_profile_id()
            
            if profile_id:
                profile = self.repo.get_full_profile(profile_id)
                return ServiceResult(success=True, data=profile)
            
            # Create default profile
            default_info = PersonalInfo(
                first_name="",
                last_name="",
                email="",
                summary=""
            )
            profile_id = self.repo.create_personal_info(default_info)
            profile = self.repo.get_full_profile(profile_id)
            
            logger.info(f"Created new profile with ID: {profile_id}")
            return ServiceResult(success=True, data=profile)
            
        except Exception as e:
            logger.error(f"Error getting/creating profile: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def get_profile(self, profile_id: int = None) -> ServiceResult:
        """Get a profile by ID or the default profile."""
        try:
            if profile_id is None:
                profile_id = self.repo.get_default_profile_id()
            
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            profile = self.repo.get_full_profile(profile_id)
            if profile:
                return ServiceResult(success=True, data=profile)
            return ServiceResult(success=False, error="Profile not found")
            
        except Exception as e:
            logger.error(f"Error getting profile: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def update_personal_info(self, **kwargs) -> ServiceResult:
        """
        Update personal information.
        
        Args:
            **kwargs: Personal info fields. Special handling for 'full_name'
                     which will be split into first_name and last_name, and
                     'location' which will be mapped to 'city'.
        """
        try:
            # Handle full_name -> first_name/last_name conversion
            if 'full_name' in kwargs:
                full_name = kwargs.pop('full_name', '').strip()
                parts = full_name.split(maxsplit=1)
                kwargs['first_name'] = parts[0] if parts else ''
                kwargs['last_name'] = parts[1] if len(parts) > 1 else ''
            
            # Handle location -> city mapping (web form sends 'location')
            if 'location' in kwargs:
                kwargs['city'] = kwargs.pop('location')
            
            # Handle LinkedIn/GitHub URL mappings
            if 'linkedin' in kwargs:
                kwargs['linkedin_url'] = kwargs.pop('linkedin')
            if 'github' in kwargs:
                kwargs['github_url'] = kwargs.pop('github')
            if 'website' in kwargs:
                kwargs['portfolio_url'] = kwargs.pop('website')
            
            # Get or create profile
            profile_id = self.repo.get_default_profile_id()
            if profile_id:
                # Get existing info and update
                existing = self.repo.get_personal_info(profile_id)
                if existing:
                    # Update only provided fields
                    for key, value in kwargs.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                    info = existing
                else:
                    info = PersonalInfo(id=profile_id, **kwargs)
            else:
                # Create new profile
                info = PersonalInfo(**kwargs)
                info.id = self.repo.create_personal_info(info)
                logger.info(f"Created new profile with ID: {info.id}")
                return ServiceResult(success=True, data={'id': info.id})
            
            success = self.repo.update_personal_info(info)
            if success:
                logger.info(f"Updated personal info for profile {info.id}")
                return ServiceResult(success=True, data={'id': info.id})
            return ServiceResult(success=False, error="Failed to update personal info")
            
        except Exception as e:
            logger.error(f"Error updating personal info: {e}")
            return ServiceResult(success=False, error=str(e))
    
    # =========================================================================
    # SKILLS OPERATIONS
    # =========================================================================
    
    def add_skill(self, profile_id: int = None, **kwargs) -> ServiceResult:
        """Add a skill to the profile."""
        try:
            if profile_id is None:
                profile_id = self.repo.get_default_profile_id()
            
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            # Convert string category/proficiency to enum if needed
            if 'category' in kwargs and isinstance(kwargs['category'], str):
                kwargs['category'] = SkillCategory(kwargs['category'])
            if 'proficiency' in kwargs and isinstance(kwargs['proficiency'], str):
                kwargs['proficiency'] = ProficiencyLevel(kwargs['proficiency'])
            
            skill = Skill(**kwargs)
            skill_id = self.repo.add_skill(profile_id, skill)
            logger.info(f"Added skill '{skill.name}' to profile {profile_id}")
            return ServiceResult(success=True, data={'id': skill_id})
            
        except Exception as e:
            logger.error(f"Error adding skill: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def update_skill(self, skill_id: int, updates: dict) -> ServiceResult:
        """Update a skill."""
        try:
            # Get existing skill
            profile_id = self.repo.get_default_profile_id()
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            skills = self.repo.get_skills(profile_id)
            skill = next((s for s in skills if s.id == skill_id), None)
            
            if not skill:
                return ServiceResult(success=False, error="Skill not found")
            
            # Update fields
            for key, value in updates.items():
                if hasattr(skill, key):
                    if key == 'category' and isinstance(value, str):
                        value = SkillCategory(value)
                    elif key == 'proficiency' and isinstance(value, str):
                        value = ProficiencyLevel(value)
                    setattr(skill, key, value)
            
            success = self.repo.update_skill(skill)
            if success:
                return ServiceResult(success=True, data={'id': skill.id})
            return ServiceResult(success=False, error="Failed to update skill")
            
        except Exception as e:
            logger.error(f"Error updating skill: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def delete_skill(self, skill_id: int) -> ServiceResult:
        """Delete a skill."""
        try:
            success = self.repo.delete_skill(skill_id)
            if success:
                return ServiceResult(success=True)
            return ServiceResult(success=False, error="Skill not found")
            
        except Exception as e:
            logger.error(f"Error deleting skill: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def get_skills(self, profile_id: int = None) -> ServiceResult:
        """Get all skills for a profile."""
        try:
            if profile_id is None:
                profile_id = self.repo.get_default_profile_id()
            
            if not profile_id:
                return ServiceResult(success=True, data=[])
            
            skills = self.repo.get_skills(profile_id)
            return ServiceResult(success=True, data=skills)
            
        except Exception as e:
            logger.error(f"Error getting skills: {e}")
            return ServiceResult(success=False, error=str(e))
    
    # =========================================================================
    # PROJECTS OPERATIONS
    # =========================================================================
    
    def add_project(self, profile_id: int = None, **kwargs) -> ServiceResult:
        """Add a project to the profile."""
        try:
            if profile_id is None:
                profile_id = self.repo.get_default_profile_id()
            
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            project = Project(**kwargs)
            project_id = self.repo.add_project(profile_id, project)
            logger.info(f"Added project '{project.name}' to profile {profile_id}")
            return ServiceResult(success=True, data={'id': project_id})
            
        except Exception as e:
            logger.error(f"Error adding project: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def update_project(self, project_id: int, updates: dict) -> ServiceResult:
        """Update a project."""
        try:
            profile_id = self.repo.get_default_profile_id()
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            projects = self.repo.get_projects(profile_id)
            project = next((p for p in projects if p.id == project_id), None)
            
            if not project:
                return ServiceResult(success=False, error="Project not found")
            
            # Update fields
            for key, value in updates.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            success = self.repo.update_project(project)
            if success:
                return ServiceResult(success=True, data={'id': project.id})
            return ServiceResult(success=False, error="Failed to update project")
            
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def delete_project(self, project_id: int) -> ServiceResult:
        """Delete a project."""
        try:
            success = self.repo.delete_project(project_id)
            if success:
                return ServiceResult(success=True)
            return ServiceResult(success=False, error="Project not found")
            
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def get_projects(self, profile_id: int = None) -> ServiceResult:
        """Get all projects for a profile."""
        try:
            if profile_id is None:
                profile_id = self.repo.get_default_profile_id()
            
            if not profile_id:
                return ServiceResult(success=True, data=[])
            
            projects = self.repo.get_projects(profile_id)
            return ServiceResult(success=True, data=projects)
            
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return ServiceResult(success=False, error=str(e))
    
    # =========================================================================
    # EDUCATION OPERATIONS
    # =========================================================================
    
    def add_education(self, profile_id: int = None, **kwargs) -> ServiceResult:
        """Add education entry to the profile."""
        try:
            if profile_id is None:
                profile_id = self.repo.get_default_profile_id()
            
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            education = Education(**kwargs)
            edu_id = self.repo.add_education(profile_id, education)
            logger.info(f"Added education '{education.institution}' to profile {profile_id}")
            return ServiceResult(success=True, data={'id': edu_id})
            
        except Exception as e:
            logger.error(f"Error adding education: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def update_education(self, education_id: int, updates: dict) -> ServiceResult:
        """Update an education entry."""
        try:
            profile_id = self.repo.get_default_profile_id()
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            education_list = self.repo.get_education(profile_id)
            education = next((e for e in education_list if e.id == education_id), None)
            
            if not education:
                return ServiceResult(success=False, error="Education entry not found")
            
            # Update fields
            for key, value in updates.items():
                if hasattr(education, key):
                    setattr(education, key, value)
            
            success = self.repo.update_education(education)
            if success:
                return ServiceResult(success=True, data={'id': education.id})
            return ServiceResult(success=False, error="Failed to update education")
            
        except Exception as e:
            logger.error(f"Error updating education: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def delete_education(self, education_id: int) -> ServiceResult:
        """Delete an education entry."""
        try:
            success = self.repo.delete_education(education_id)
            if success:
                return ServiceResult(success=True)
            return ServiceResult(success=False, error="Education entry not found")
            
        except Exception as e:
            logger.error(f"Error deleting education: {e}")
            return ServiceResult(success=False, error=str(e))
    
    # =========================================================================
    # EXPERIENCE OPERATIONS
    # =========================================================================
    
    def add_experience(self, profile_id: int = None, **kwargs) -> ServiceResult:
        """Add experience entry to the profile."""
        try:
            if profile_id is None:
                profile_id = self.repo.get_default_profile_id()
            
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            experience = Experience(**kwargs)
            exp_id = self.repo.add_experience(profile_id, experience)
            logger.info(f"Added experience '{experience.company}' to profile {profile_id}")
            return ServiceResult(success=True, data={'id': exp_id})
            
        except Exception as e:
            logger.error(f"Error adding experience: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def update_experience(self, experience_id: int, updates: dict) -> ServiceResult:
        """Update an experience entry."""
        try:
            profile_id = self.repo.get_default_profile_id()
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            experience_list = self.repo.get_experience(profile_id)
            experience = next((e for e in experience_list if e.id == experience_id), None)
            
            if not experience:
                return ServiceResult(success=False, error="Experience entry not found")
            
            # Update fields
            for key, value in updates.items():
                if hasattr(experience, key):
                    setattr(experience, key, value)
            
            success = self.repo.update_experience(experience)
            if success:
                return ServiceResult(success=True, data={'id': experience.id})
            return ServiceResult(success=False, error="Failed to update experience")
            
        except Exception as e:
            logger.error(f"Error updating experience: {e}")
            return ServiceResult(success=False, error=str(e))
    
    def delete_experience(self, experience_id: int) -> ServiceResult:
        """Delete an experience entry."""
        try:
            success = self.repo.delete_experience(experience_id)
            if success:
                return ServiceResult(success=True)
            return ServiceResult(success=False, error="Experience entry not found")
            
        except Exception as e:
            logger.error(f"Error deleting experience: {e}")
            return ServiceResult(success=False, error=str(e))
    
    # =========================================================================
    # METADATA OPERATIONS
    # =========================================================================
    
    def update_metadata(self, certifications: List[str] = None,
                        languages: List[dict] = None,
                        interests: List[str] = None,
                        profile_id: int = None) -> ServiceResult:
        """Update profile metadata (certifications, languages, interests)."""
        try:
            if profile_id is None:
                profile_id = self.repo.get_default_profile_id()
            
            if not profile_id:
                return ServiceResult(success=False, error="No profile found")
            
            # Get current metadata and merge
            current = self.repo.get_metadata(profile_id)
            
            self.repo.save_metadata(
                profile_id,
                certifications if certifications is not None else current.get('certifications', []),
                languages if languages is not None else current.get('languages', []),
                interests if interests is not None else current.get('interests', [])
            )
            
            logger.info(f"Updated metadata for profile {profile_id}")
            return ServiceResult(success=True)
            
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
            return ServiceResult(success=False, error=str(e))
