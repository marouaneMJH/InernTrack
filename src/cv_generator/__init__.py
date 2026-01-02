"""
CV Generator Module

A clean, SOLID-compliant module for generating customized CVs and cover letters.

Components:
- models: Data models for user profiles, skills, projects, etc.
- repositories: Data access layer (repository pattern)
- services: Business logic for matching, content generation, rendering
- templates: LaTeX template management

Author: El Moujahid Marouane
Version: 1.0
"""

from .models import (
    UserProfile,
    Skill,
    Project,
    Education,
    Experience,
    PersonalInfo,
    GeneratedDocument,
)
from .services import (
    ProfileService,
    MatchingService,
    ContentGeneratorService,
    LatexRendererService,
    CVGeneratorFacade,
)

__all__ = [
    # Models
    'UserProfile',
    'Skill',
    'Project',
    'Education',
    'Experience',
    'PersonalInfo',
    'GeneratedDocument',
    # Services
    'ProfileService',
    'MatchingService',
    'ContentGeneratorService',
    'LatexRendererService',
    'CVGeneratorFacade',
]
