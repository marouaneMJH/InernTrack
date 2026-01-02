"""
CV Generator Facade

Provides a simplified interface to the CV generation system.
Follows the Facade Pattern to coordinate complex operations.

Author: El Moujahid Marouane
Version: 1.0
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from ..models import UserProfile, GeneratedDocument, MatchResult
from ..repository import ProfileRepository
from .profile_service import ProfileService
from .matching_service import MatchingService, JobOffer
from .content_generator import ContentGeneratorService, CVContent, CoverLetterContent
from .latex_renderer import LatexRendererService

try:
    from ...logger_setup import get_logger
except ImportError:
    from src.logger_setup import get_logger

logger = get_logger("cv_generator.facade")


@dataclass
class GenerationResult:
    """Result of document generation."""
    success: bool
    document: Optional[GeneratedDocument] = None
    cv_content: Optional[CVContent] = None
    cover_letter_content: Optional[CoverLetterContent] = None
    match_result: Optional[MatchResult] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            'success': self.success,
            'error': self.error,
        }
        if self.document:
            result['document'] = self.document.to_dict()
        if self.match_result:
            result['match_result'] = self.match_result.to_dict()
        if self.cv_content:
            result['cv_content'] = self.cv_content.to_dict()
        if self.cover_letter_content:
            result['cover_letter_content'] = self.cover_letter_content.to_dict()
        return result


class CVGeneratorFacade:
    """
    Facade for the CV generation system.
    
    Coordinates profile management, matching, content generation,
    and PDF rendering into a simple interface.
    """
    
    def __init__(self):
        """Initialize all services."""
        self.profile_service = ProfileService()
        self.matching_service = MatchingService()
        self.content_generator = ContentGeneratorService()
        self.latex_renderer = LatexRendererService()
        self.repository = ProfileRepository()
    
    def generate_cv_for_job(self, job_data: Dict[str, Any], 
                            profile_id: int = None,
                            compile_pdf: bool = True) -> GenerationResult:
        """
        Generate a tailored CV for a specific job offer.
        
        This is the main entry point for CV generation. It:
        1. Loads the user profile
        2. Creates a job offer from the data
        3. Matches profile to job
        4. Generates tailored content
        5. Renders to LaTeX and optionally compiles to PDF
        
        Args:
            job_data: Dictionary with job details (title, description, company, etc.)
            profile_id: Optional profile ID (uses default if not specified)
            compile_pdf: Whether to compile LaTeX to PDF
        
        Returns:
            GenerationResult with document and match details
        """
        logger.info(f"Generating CV for job: {job_data.get('title')} at {job_data.get('company')}")
        
        try:
            # Get profile
            result = self.profile_service.get_profile(profile_id)
            if not result.success:
                return GenerationResult(success=False, error="Profile not found. Please create a profile first.")
            
            profile = result.data
            
            # Create job offer
            job = JobOffer(
                title=job_data.get('title', ''),
                description=job_data.get('description', ''),
                company=job_data.get('company', ''),
                requirements=job_data.get('requirements', ''),
                skills=job_data.get('skills', []),
                location=job_data.get('location', ''),
            )
            
            # Match profile to job
            match_result = self.matching_service.match(profile, job)
            
            # Generate content
            cv_content = self.content_generator.generate_cv_content(profile, match_result, job)
            
            # Render to LaTeX
            if compile_pdf:
                latex, pdf_path = self.latex_renderer.render_cv(cv_content)
            else:
                latex = self.latex_renderer.get_latex_only(cv_content)
                pdf_path = None
            
            # Create document record
            document = GeneratedDocument(
                document_type='cv',
                internship_id=job_data.get('internship_id'),
                company_name=job.company,
                job_title=job.title,
                content=cv_content.summary,
                latex_content=latex,
                pdf_path=pdf_path,
                match_score=match_result.overall_score,
            )
            
            # Save to database
            if profile.id:
                doc_id = self.repository.save_generated_document(profile.id, document)
                document.id = doc_id
            
            logger.info(f"CV generated successfully. Match score: {match_result.overall_score:.1f}%")
            
            return GenerationResult(
                success=True,
                document=document,
                cv_content=cv_content,
                match_result=match_result,
            )
            
        except Exception as e:
            logger.error(f"CV generation failed: {e}")
            return GenerationResult(success=False, error=str(e))
    
    def generate_cover_letter_for_job(self, job_data: Dict[str, Any],
                                       profile_id: int = None,
                                       compile_pdf: bool = True) -> GenerationResult:
        """
        Generate a cover letter for a specific job offer.
        
        Args:
            job_data: Dictionary with job details
            profile_id: Optional profile ID
            compile_pdf: Whether to compile LaTeX to PDF
        
        Returns:
            GenerationResult with document and match details
        """
        logger.info(f"Generating cover letter for: {job_data.get('title')} at {job_data.get('company')}")
        
        try:
            # Get profile
            result = self.profile_service.get_profile(profile_id)
            if not result.success:
                return GenerationResult(success=False, error="Profile not found")
            
            profile = result.data
            
            # Create job offer
            job = JobOffer(
                title=job_data.get('title', ''),
                description=job_data.get('description', ''),
                company=job_data.get('company', ''),
                requirements=job_data.get('requirements', ''),
                skills=job_data.get('skills', []),
                location=job_data.get('location', ''),
            )
            
            # Match profile to job
            match_result = self.matching_service.match(profile, job)
            
            # Generate content
            cover_letter_content = self.content_generator.generate_cover_letter_content(
                profile, match_result, job
            )
            
            # Render to LaTeX
            if compile_pdf:
                latex, pdf_path = self.latex_renderer.render_cover_letter(cover_letter_content)
            else:
                latex = self.latex_renderer.get_cover_letter_latex_only(cover_letter_content)
                pdf_path = None
            
            # Create document record
            document = GeneratedDocument(
                document_type='cover_letter',
                internship_id=job_data.get('internship_id'),
                company_name=job.company,
                job_title=job.title,
                content=cover_letter_content.full_text,
                latex_content=latex,
                pdf_path=pdf_path,
                match_score=match_result.overall_score,
            )
            
            # Save to database
            if profile.id:
                doc_id = self.repository.save_generated_document(profile.id, document)
                document.id = doc_id
            
            logger.info(f"Cover letter generated successfully")
            
            return GenerationResult(
                success=True,
                document=document,
                cover_letter_content=cover_letter_content,
                match_result=match_result,
            )
            
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            return GenerationResult(success=False, error=str(e))
    
    def generate_both(self, job_data: Dict[str, Any],
                      profile_id: int = None,
                      compile_pdf: bool = True) -> Dict[str, GenerationResult]:
        """
        Generate both CV and cover letter for a job.
        
        Args:
            job_data: Dictionary with job details
            profile_id: Optional profile ID
            compile_pdf: Whether to compile LaTeX to PDF
        
        Returns:
            Dictionary with 'cv' and 'cover_letter' GenerationResults
        """
        return {
            'cv': self.generate_cv_for_job(job_data, profile_id, compile_pdf),
            'cover_letter': self.generate_cover_letter_for_job(job_data, profile_id, compile_pdf),
        }
    
    def analyze_job_match(self, job_data: Dict[str, Any],
                          profile_id: int = None) -> GenerationResult:
        """
        Analyze how well a profile matches a job without generating documents.
        
        Useful for previewing match score before generation.
        
        Args:
            job_data: Dictionary with job details
            profile_id: Optional profile ID
        
        Returns:
            GenerationResult with match_result only
        """
        try:
            # Get profile
            result = self.profile_service.get_profile(profile_id)
            if not result.success:
                return GenerationResult(success=False, error="Profile not found")
            
            profile = result.data
            
            # Create job offer
            job = JobOffer(
                title=job_data.get('title', ''),
                description=job_data.get('description', ''),
                company=job_data.get('company', ''),
                requirements=job_data.get('requirements', ''),
                skills=job_data.get('skills', []),
                location=job_data.get('location', ''),
            )
            
            # Match profile to job
            match_result = self.matching_service.match(profile, job)
            
            return GenerationResult(
                success=True,
                match_result=match_result,
            )
            
        except Exception as e:
            logger.error(f"Job match analysis failed: {e}")
            return GenerationResult(success=False, error=str(e))
    
    def get_generated_documents(self, profile_id: int = None, 
                                 limit: int = 20) -> Dict[str, Any]:
        """
        Get recently generated documents.
        
        Args:
            profile_id: Optional profile ID
            limit: Maximum number of documents to return
        
        Returns:
            Dictionary with success status and documents list
        """
        try:
            if profile_id is None:
                profile_id = self.repository.get_default_profile_id()
            
            if not profile_id:
                return {'success': False, 'error': 'No profile found'}
            
            docs = self.repository.get_generated_documents(profile_id, limit)
            
            return {
                'success': True,
                'documents': [d.to_dict() for d in docs],
            }
            
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            return {'success': False, 'error': str(e)}
