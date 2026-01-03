"""
CV Generator Controller

Handles API routes for CV and cover letter generation.

Author: El Moujahid Marouane
Version: 1.0
"""

from flask import request, jsonify, send_file
import os

from .base import BaseController
from src.cv_generator.services import (
    CVGeneratorFacade,
    ProfileService,
    MatchingService,
)


class CVGeneratorController(BaseController):
    """Controller for CV generation API routes."""
    
    def __init__(self, blueprint):
        super().__init__(blueprint)
        self.facade = CVGeneratorFacade()
        self.profile_service = ProfileService()
    
    def register_routes(self):
        """Register CV generator routes."""
        # Profile routes
        self.bp.add_url_rule(
            '/api/cv/profile',
            'api_cv_profile',
            self.get_profile,
            methods=['GET']
        )
        self.bp.add_url_rule(
            '/api/cv/profile/personal',
            'api_cv_profile_personal',
            self.update_personal_info,
            methods=['PUT', 'POST']
        )
        
        # Skills routes
        self.bp.add_url_rule(
            '/api/cv/skills',
            'api_cv_skills_list',
            self.list_skills,
            methods=['GET']
        )
        self.bp.add_url_rule(
            '/api/cv/skills',
            'api_cv_skills_add',
            self.add_skill,
            methods=['POST']
        )
        self.bp.add_url_rule(
            '/api/cv/skills/<int:skill_id>',
            'api_cv_skill_update',
            self.update_skill,
            methods=['PUT']
        )
        self.bp.add_url_rule(
            '/api/cv/skills/<int:skill_id>',
            'api_cv_skill_delete',
            self.delete_skill,
            methods=['DELETE']
        )
        
        # Projects routes
        self.bp.add_url_rule(
            '/api/cv/projects',
            'api_cv_projects_list',
            self.list_projects,
            methods=['GET']
        )
        self.bp.add_url_rule(
            '/api/cv/projects',
            'api_cv_projects_add',
            self.add_project,
            methods=['POST']
        )
        self.bp.add_url_rule(
            '/api/cv/projects/<int:project_id>',
            'api_cv_project_update',
            self.update_project,
            methods=['PUT']
        )
        self.bp.add_url_rule(
            '/api/cv/projects/<int:project_id>',
            'api_cv_project_delete',
            self.delete_project,
            methods=['DELETE']
        )
        
        # Education routes
        self.bp.add_url_rule(
            '/api/cv/education',
            'api_cv_education_list',
            self.list_education,
            methods=['GET']
        )
        self.bp.add_url_rule(
            '/api/cv/education',
            'api_cv_education_add',
            self.add_education,
            methods=['POST']
        )
        self.bp.add_url_rule(
            '/api/cv/education/<int:edu_id>',
            'api_cv_education_update',
            self.update_education,
            methods=['PUT']
        )
        self.bp.add_url_rule(
            '/api/cv/education/<int:edu_id>',
            'api_cv_education_delete',
            self.delete_education,
            methods=['DELETE']
        )
        
        # Experience routes
        self.bp.add_url_rule(
            '/api/cv/experience',
            'api_cv_experience_list',
            self.list_experience,
            methods=['GET']
        )
        self.bp.add_url_rule(
            '/api/cv/experience',
            'api_cv_experience_add',
            self.add_experience,
            methods=['POST']
        )
        self.bp.add_url_rule(
            '/api/cv/experience/<int:exp_id>',
            'api_cv_experience_update',
            self.update_experience,
            methods=['PUT']
        )
        self.bp.add_url_rule(
            '/api/cv/experience/<int:exp_id>',
            'api_cv_experience_delete',
            self.delete_experience,
            methods=['DELETE']
        )
        
        # Generation routes
        self.bp.add_url_rule(
            '/api/cv/generate/cv',
            'api_generate_cv',
            self.generate_cv,
            methods=['POST']
        )
        self.bp.add_url_rule(
            '/api/cv/generate/cover-letter',
            'api_generate_cover_letter',
            self.generate_cover_letter,
            methods=['POST']
        )
        self.bp.add_url_rule(
            '/api/cv/generate/both',
            'api_generate_both',
            self.generate_both,
            methods=['POST']
        )
        self.bp.add_url_rule(
            '/api/cv/analyze-match',
            'api_analyze_match',
            self.analyze_match,
            methods=['POST']
        )
        
        # Documents routes
        self.bp.add_url_rule(
            '/api/cv/documents',
            'api_cv_documents',
            self.list_documents,
            methods=['GET']
        )
        self.bp.add_url_rule(
            '/api/cv/documents/<int:doc_id>/download',
            'api_cv_document_download',
            self.download_document,
            methods=['GET']
        )
    
    # =====================
    # Profile Methods
    # =====================
    
    def get_profile(self):
        """Get the current user profile."""
        result = self.profile_service.get_profile()
        if result.success:
            profile = result.data
            return self.json_response({
                'success': True,
                'profile': profile.to_dict() if profile else None,
            })
        return self.error_response(result.error, result.status_code)
    
    def update_personal_info(self):
        """Update personal information."""
        data = request.get_json()
        if not data:
            return self.error_response("No data provided", 400)
        
        result = self.profile_service.update_personal_info(
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            location=data.get('location'),
            linkedin=data.get('linkedin'),
            github=data.get('github'),
            website=data.get('website'),
            summary=data.get('summary'),
        )
        return self.service_to_response(result)
    
    # =====================
    # Skills Methods
    # =====================
    
    def list_skills(self):
        """List all skills."""
        result = self.profile_service.get_profile()
        if result.success and result.data:
            skills = [s.to_dict() for s in result.data.skills]
            return self.json_response({'success': True, 'skills': skills})
        return self.json_response({'success': True, 'skills': []})
    
    def add_skill(self):
        """Add a new skill."""
        data = request.get_json()
        if not data or 'name' not in data:
            return self.error_response("Skill name is required", 400)
        
        result = self.profile_service.add_skill(
            name=data['name'],
            category=data.get('category', 'other'),
            proficiency=data.get('proficiency', 'intermediate'),
            years_experience=data.get('years_experience'),
            keywords=data.get('keywords', []),
        )
        return self.service_to_response(result)
    
    def update_skill(self, skill_id: int):
        """Update a skill."""
        data = request.get_json()
        if not data:
            return self.error_response("No data provided", 400)
        
        result = self.profile_service.update_skill(skill_id, data)
        return self.service_to_response(result)
    
    def delete_skill(self, skill_id: int):
        """Delete a skill."""
        result = self.profile_service.delete_skill(skill_id)
        return self.service_to_response(result)
    
    # =====================
    # Projects Methods
    # =====================
    
    def list_projects(self):
        """List all projects."""
        result = self.profile_service.get_profile()
        if result.success and result.data:
            projects = [p.to_dict() for p in result.data.projects]
            return self.json_response({'success': True, 'projects': projects})
        return self.json_response({'success': True, 'projects': []})
    
    def add_project(self):
        """Add a new project."""
        data = request.get_json()
        if not data or 'name' not in data:
            return self.error_response("Project name is required", 400)
        
        result = self.profile_service.add_project(
            name=data['name'],
            description=data.get('description', ''),
            technologies=data.get('technologies', []),
            url=data.get('url'),
            github_url=data.get('github_url'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            highlights=data.get('highlights', []),
        )
        return self.service_to_response(result)
    
    def update_project(self, project_id: int):
        """Update a project."""
        data = request.get_json()
        if not data:
            return self.error_response("No data provided", 400)
        
        result = self.profile_service.update_project(project_id, data)
        return self.service_to_response(result)
    
    def delete_project(self, project_id: int):
        """Delete a project."""
        result = self.profile_service.delete_project(project_id)
        return self.service_to_response(result)
    
    # =====================
    # Education Methods
    # =====================
    
    def list_education(self):
        """List all education entries."""
        result = self.profile_service.get_profile()
        if result.success and result.data:
            education = [e.to_dict() for e in result.data.education]
            return self.json_response({'success': True, 'education': education})
        return self.json_response({'success': True, 'education': []})
    
    def add_education(self):
        """Add a new education entry."""
        data = request.get_json()
        if not data or 'institution' not in data or 'degree' not in data:
            return self.error_response("Institution and degree are required", 400)
        
        result = self.profile_service.add_education(
            institution=data['institution'],
            degree=data['degree'],
            field_of_study=data.get('field', ''),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            gpa=data.get('gpa'),
            achievements=data.get('achievements', []),
            location=data.get('location'),
        )
        return self.service_to_response(result)
    
    def update_education(self, edu_id: int):
        """Update an education entry."""
        data = request.get_json()
        if not data:
            return self.error_response("No data provided", 400)
        
        result = self.profile_service.update_education(edu_id, data)
        return self.service_to_response(result)
    
    def delete_education(self, edu_id: int):
        """Delete an education entry."""
        result = self.profile_service.delete_education(edu_id)
        return self.service_to_response(result)
    
    # =====================
    # Experience Methods
    # =====================
    
    def list_experience(self):
        """List all experience entries."""
        result = self.profile_service.get_profile()
        if result.success and result.data:
            experience = [e.to_dict() for e in result.data.experience]
            return self.json_response({'success': True, 'experience': experience})
        return self.json_response({'success': True, 'experience': []})
    
    def add_experience(self):
        """Add a new experience entry."""
        data = request.get_json()
        if not data or 'company' not in data or 'title' not in data:
            return self.error_response("Company and title are required", 400)
        
        result = self.profile_service.add_experience(
            company=data['company'],
            position=data['title'],
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            is_current=data.get('is_current', False),
            description=data.get('description', ''),
            achievements=data.get('achievements', []),
            technologies_used=data.get('technologies', []),
            location=data.get('location'),
        )
        return self.service_to_response(result)
    
    def update_experience(self, exp_id: int):
        """Update an experience entry."""
        data = request.get_json()
        if not data:
            return self.error_response("No data provided", 400)
        
        result = self.profile_service.update_experience(exp_id, data)
        return self.service_to_response(result)
    
    def delete_experience(self, exp_id: int):
        """Delete an experience entry."""
        result = self.profile_service.delete_experience(exp_id)
        return self.service_to_response(result)
    
    # =====================
    # Generation Methods
    # =====================
    
    def generate_cv(self):
        """Generate a CV for a job."""
        data = request.get_json()
        if not data:
            return self.error_response("Job data is required", 400)
        
        compile_pdf = data.get('compile_pdf', True)
        result = self.facade.generate_cv_for_job(data, compile_pdf=compile_pdf)
        
        return self.json_response(result.to_dict())
    
    def generate_cover_letter(self):
        """Generate a cover letter for a job."""
        data = request.get_json()
        if not data:
            return self.error_response("Job data is required", 400)
        
        compile_pdf = data.get('compile_pdf', True)
        result = self.facade.generate_cover_letter_for_job(data, compile_pdf=compile_pdf)
        
        return self.json_response(result.to_dict())
    
    def generate_both(self):
        """Generate both CV and cover letter for a job."""
        data = request.get_json()
        if not data:
            return self.error_response("Job data is required", 400)
        
        compile_pdf = data.get('compile_pdf', True)
        results = self.facade.generate_both(data, compile_pdf=compile_pdf)
        
        return self.json_response({
            'cv': results['cv'].to_dict(),
            'cover_letter': results['cover_letter'].to_dict(),
        })
    
    def analyze_match(self):
        """Analyze job match without generating documents."""
        data = request.get_json()
        if not data:
            return self.error_response("Job data is required", 400)
        
        result = self.facade.analyze_job_match(data)
        return self.json_response(result.to_dict())
    
    # =====================
    # Documents Methods
    # =====================
    
    def list_documents(self):
        """List generated documents."""
        limit = request.args.get('limit', 20, type=int)
        result = self.facade.get_generated_documents(limit=limit)
        return self.json_response(result)
    
    def download_document(self, doc_id: int):
        """Download a generated document PDF."""
        try:
            from src.cv_generator.repository import ProfileRepository
            repo = ProfileRepository()
            
            # Get document
            docs = repo.get_generated_documents(limit=100)
            doc = next((d for d in docs if d.id == doc_id), None)
            
            if not doc or not doc.pdf_path:
                return self.error_response("Document not found", 404)
            
            if not os.path.exists(doc.pdf_path):
                return self.error_response("PDF file not found", 404)
            
            filename = f"{doc.company_name}_{doc.document_type}.pdf"
            return send_file(
                doc.pdf_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
            
        except Exception as e:
            return self.error_response(str(e), 500)
