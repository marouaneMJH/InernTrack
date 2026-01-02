"""
Content Generator Service

Generates structured CV and cover letter content.
Single Responsibility: Text content generation.

Author: El Moujahid Marouane
Version: 1.0
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import date

from ..models import (
    UserProfile, MatchResult, GeneratedDocument,
    Skill, Project, Education, Experience, SkillCategory
)
from .matching_service import JobOffer

try:
    from ...logger_setup import get_logger
except ImportError:
    from src.logger_setup import get_logger

logger = get_logger("cv_generator.content_generator")


@dataclass
class CVContent:
    """Structured CV content."""
    personal_info: Dict[str, str]
    summary: str
    skills_section: str
    experience_section: str
    education_section: str
    projects_section: str
    certifications_section: str
    languages_section: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'personal_info': self.personal_info,
            'summary': self.summary,
            'skills_section': self.skills_section,
            'experience_section': self.experience_section,
            'education_section': self.education_section,
            'projects_section': self.projects_section,
            'certifications_section': self.certifications_section,
            'languages_section': self.languages_section,
        }


@dataclass
class CoverLetterContent:
    """Structured cover letter content."""
    recipient_info: Dict[str, str]
    sender_info: Dict[str, str]
    opening_paragraph: str
    body_paragraphs: list
    closing_paragraph: str
    signature: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'recipient_info': self.recipient_info,
            'sender_info': self.sender_info,
            'opening_paragraph': self.opening_paragraph,
            'body_paragraphs': self.body_paragraphs,
            'closing_paragraph': self.closing_paragraph,
            'signature': self.signature,
        }
    
    @property
    def full_text(self) -> str:
        """Get the full letter as text."""
        paragraphs = [
            self.opening_paragraph,
            *self.body_paragraphs,
            self.closing_paragraph,
        ]
        return '\n\n'.join(paragraphs)


class ContentGeneratorService:
    """
    Service for generating CV and cover letter content.
    
    Takes a matched profile and generates structured text
    content ready for template rendering.
    """
    
    def generate_cv_content(self, profile: UserProfile, match_result: MatchResult,
                            job: JobOffer = None) -> CVContent:
        """
        Generate CV content tailored to a job offer.
        
        Uses match results to prioritize relevant skills and projects.
        """
        logger.info("Generating CV content")
        
        # Personal info
        personal_info = {
            'name': profile.personal_info.full_name,
            'email': profile.personal_info.email,
            'phone': profile.personal_info.phone or '',
            'address': self._format_address(profile.personal_info),
            'linkedin': profile.personal_info.linkedin_url or '',
            'github': profile.personal_info.github_url or '',
            'portfolio': profile.personal_info.portfolio_url or '',
        }
        
        # Generate tailored summary
        summary = self._generate_summary(profile, match_result, job)
        
        # Generate skills section (prioritized)
        skills_section = self._generate_skills_section(profile, match_result)
        
        # Generate experience section
        experience_section = self._generate_experience_section(profile, match_result)
        
        # Generate education section
        education_section = self._generate_education_section(profile)
        
        # Generate projects section (prioritized)
        projects_section = self._generate_projects_section(profile, match_result)
        
        # Certifications
        certifications_section = self._generate_certifications_section(profile)
        
        # Languages
        languages_section = self._generate_languages_section(profile)
        
        return CVContent(
            personal_info=personal_info,
            summary=summary,
            skills_section=skills_section,
            experience_section=experience_section,
            education_section=education_section,
            projects_section=projects_section,
            certifications_section=certifications_section,
            languages_section=languages_section,
        )
    
    def generate_cover_letter_content(self, profile: UserProfile, match_result: MatchResult,
                                       job: JobOffer) -> CoverLetterContent:
        """
        Generate cover letter content for a specific job.
        """
        logger.info(f"Generating cover letter for {job.title} at {job.company}")
        
        # Recipient info
        recipient_info = {
            'company': job.company,
            'position': job.title,
            'location': job.location,
        }
        
        # Sender info
        sender_info = {
            'name': profile.personal_info.full_name,
            'email': profile.personal_info.email,
            'phone': profile.personal_info.phone or '',
            'address': self._format_address(profile.personal_info),
            'date': date.today().strftime('%B %d, %Y'),
        }
        
        # Opening paragraph
        opening = self._generate_opening_paragraph(profile, job)
        
        # Body paragraphs
        body = self._generate_body_paragraphs(profile, match_result, job)
        
        # Closing paragraph
        closing = self._generate_closing_paragraph(profile, job)
        
        # Signature
        signature = f"Sincerely,\n{profile.personal_info.full_name}"
        
        return CoverLetterContent(
            recipient_info=recipient_info,
            sender_info=sender_info,
            opening_paragraph=opening,
            body_paragraphs=body,
            closing_paragraph=closing,
            signature=signature,
        )
    
    def _format_address(self, info) -> str:
        """Format address from personal info."""
        parts = []
        if info.city:
            parts.append(info.city)
        if info.country:
            parts.append(info.country)
        return ', '.join(parts) if parts else ''
    
    def _generate_summary(self, profile: UserProfile, match_result: MatchResult,
                          job: JobOffer = None) -> str:
        """Generate a tailored professional summary."""
        # Start with user's summary if available
        base_summary = profile.personal_info.summary
        
        if not base_summary:
            # Generate a basic summary
            skills = [s.name for s in match_result.priority_skills[:3]]
            if profile.education:
                edu = profile.education[0]
                base_summary = (
                    f"{edu.degree} student in {edu.field_of_study} "
                    f"at {edu.institution}"
                )
                if skills:
                    base_summary += f" with experience in {', '.join(skills)}"
                base_summary += "."
            elif skills:
                base_summary = f"Professional with expertise in {', '.join(skills)}."
            else:
                base_summary = "Motivated professional seeking new opportunities."
        
        # Add job-specific tailoring
        if job and match_result.priority_skills:
            top_skills = [s.name for s in match_result.priority_skills[:2]]
            if top_skills:
                base_summary += f" Seeking to leverage {' and '.join(top_skills)} skills"
                if job.company:
                    base_summary += f" at {job.company}"
                base_summary += "."
        
        return base_summary
    
    def _generate_skills_section(self, profile: UserProfile, match_result: MatchResult) -> str:
        """Generate skills section with prioritized skills."""
        # Group skills by category
        technical = []
        soft = []
        tools = []
        other = []
        
        # Use priority skills first, then add others
        added_ids = set()
        
        for skill in match_result.priority_skills:
            added_ids.add(skill.id)
            self._categorize_skill(skill, technical, soft, tools, other)
        
        # Add remaining skills
        for skill in profile.skills:
            if skill.id not in added_ids:
                self._categorize_skill(skill, technical, soft, tools, other)
        
        sections = []
        if technical:
            sections.append(f"Technical Skills: {', '.join(technical)}")
        if tools:
            sections.append(f"Tools & Technologies: {', '.join(tools)}")
        if soft:
            sections.append(f"Soft Skills: {', '.join(soft)}")
        if other:
            sections.append(f"Other: {', '.join(other)}")
        
        return '\n'.join(sections)
    
    def _categorize_skill(self, skill: Skill, technical: list, soft: list, 
                          tools: list, other: list):
        """Categorize a skill into the appropriate list."""
        skill_str = skill.name
        if skill.proficiency.value in ['advanced', 'expert']:
            skill_str += f" ({skill.proficiency.value})"
        
        if skill.category == SkillCategory.TECHNICAL:
            technical.append(skill_str)
        elif skill.category == SkillCategory.SOFT:
            soft.append(skill_str)
        elif skill.category in [SkillCategory.TOOL, SkillCategory.FRAMEWORK]:
            tools.append(skill_str)
        else:
            other.append(skill_str)
    
    def _generate_experience_section(self, profile: UserProfile, match_result: MatchResult) -> str:
        """Generate experience section."""
        entries = []
        
        # Prioritize relevant experience
        relevant_ids = {e.id for e in match_result.relevant_experience}
        sorted_exp = sorted(profile.experience, 
                           key=lambda e: (e.id in relevant_ids, e.start_date or date.min),
                           reverse=True)
        
        for exp in sorted_exp:
            entry = self._format_experience_entry(exp)
            entries.append(entry)
        
        return '\n\n'.join(entries)
    
    def _format_experience_entry(self, exp: Experience) -> str:
        """Format a single experience entry."""
        lines = []
        
        # Header: Position at Company, Location
        header = f"{exp.position} at {exp.company}"
        if exp.location:
            header += f", {exp.location}"
        lines.append(header)
        
        # Date range
        start = exp.start_date.strftime('%b %Y') if exp.start_date else 'Unknown'
        end = 'Present' if exp.is_current else (exp.end_date.strftime('%b %Y') if exp.end_date else 'Unknown')
        lines.append(f"{start} - {end}")
        
        # Description or responsibilities
        if exp.description:
            lines.append(exp.description)
        
        if exp.responsibilities:
            for resp in exp.responsibilities[:4]:  # Limit to 4
                lines.append(f"• {resp}")
        
        if exp.achievements:
            lines.append("Key Achievements:")
            for ach in exp.achievements[:3]:  # Limit to 3
                lines.append(f"• {ach}")
        
        return '\n'.join(lines)
    
    def _generate_education_section(self, profile: UserProfile) -> str:
        """Generate education section."""
        entries = []
        
        for edu in profile.education:
            entry = self._format_education_entry(edu)
            entries.append(entry)
        
        return '\n\n'.join(entries)
    
    def _format_education_entry(self, edu: Education) -> str:
        """Format a single education entry."""
        lines = []
        
        # Degree and field
        lines.append(f"{edu.degree} in {edu.field_of_study}")
        
        # Institution and location
        inst_line = edu.institution
        if edu.location:
            inst_line += f", {edu.location}"
        lines.append(inst_line)
        
        # Date range
        start = edu.start_date.strftime('%Y') if edu.start_date else ''
        end = 'Present' if edu.is_ongoing else (edu.end_date.strftime('%Y') if edu.end_date else '')
        if start or end:
            lines.append(f"{start} - {end}")
        
        # GPA
        if edu.gpa:
            lines.append(f"GPA: {edu.gpa}")
        
        # Achievements
        if edu.achievements:
            for ach in edu.achievements[:2]:
                lines.append(f"• {ach}")
        
        # Relevant coursework
        if edu.relevant_coursework:
            courses = ', '.join(edu.relevant_coursework[:5])
            lines.append(f"Relevant Coursework: {courses}")
        
        return '\n'.join(lines)
    
    def _generate_projects_section(self, profile: UserProfile, match_result: MatchResult) -> str:
        """Generate projects section with prioritized projects."""
        entries = []
        
        # Use priority projects first
        added_ids = set()
        
        for project in match_result.priority_projects:
            added_ids.add(project.id)
            entries.append(self._format_project_entry(project))
        
        # Add remaining projects up to a limit
        remaining_slots = 5 - len(entries)
        for project in profile.projects:
            if project.id not in added_ids and remaining_slots > 0:
                entries.append(self._format_project_entry(project))
                remaining_slots -= 1
        
        return '\n\n'.join(entries)
    
    def _format_project_entry(self, project: Project) -> str:
        """Format a single project entry."""
        lines = []
        
        # Project name and role
        header = project.name
        if project.role:
            header += f" ({project.role})"
        lines.append(header)
        
        # Technologies
        if project.technologies:
            techs = ', '.join(project.technologies)
            lines.append(f"Technologies: {techs}")
        
        # Description
        if project.description:
            lines.append(project.description)
        
        # Highlights
        if project.highlights:
            for highlight in project.highlights[:3]:
                lines.append(f"• {highlight}")
        
        # Links
        if project.github_url:
            lines.append(f"GitHub: {project.github_url}")
        if project.url:
            lines.append(f"Demo: {project.url}")
        
        return '\n'.join(lines)
    
    def _generate_certifications_section(self, profile: UserProfile) -> str:
        """Generate certifications section."""
        if not profile.certifications:
            return ""
        return '\n'.join(f"• {cert}" for cert in profile.certifications)
    
    def _generate_languages_section(self, profile: UserProfile) -> str:
        """Generate languages section."""
        if not profile.languages:
            return ""
        
        entries = []
        for lang in profile.languages:
            name = lang.get('name', '')
            level = lang.get('level', '')
            if name:
                entry = name
                if level:
                    entry += f" ({level})"
                entries.append(entry)
        
        return ', '.join(entries)
    
    # =========================================================================
    # COVER LETTER GENERATION
    # =========================================================================
    
    def _generate_opening_paragraph(self, profile: UserProfile, job: JobOffer) -> str:
        """Generate opening paragraph for cover letter."""
        name = profile.personal_info.full_name
        
        opening = (
            f"I am writing to express my strong interest in the {job.title} position "
            f"at {job.company}. "
        )
        
        # Add relevant background
        if profile.education:
            edu = profile.education[0]
            opening += (
                f"As a {edu.degree} student in {edu.field_of_study} "
                f"at {edu.institution}, I am eager to apply my academic knowledge "
                f"and practical skills in a professional environment."
            )
        else:
            opening += (
                f"With my background and passion for the field, I am excited about "
                f"the opportunity to contribute to your team."
            )
        
        return opening
    
    def _generate_body_paragraphs(self, profile: UserProfile, match_result: MatchResult,
                                   job: JobOffer) -> list:
        """Generate body paragraphs highlighting relevant qualifications."""
        paragraphs = []
        
        # Skills paragraph
        if match_result.priority_skills:
            skills = match_result.priority_skills[:3]
            skill_names = [s.name for s in skills]
            
            skills_para = (
                f"My technical expertise includes {', '.join(skill_names[:-1])}"
                f"{' and ' + skill_names[-1] if len(skill_names) > 1 else skill_names[0] if skill_names else ''}. "
            )
            
            # Add proficiency details for top skill
            top_skill = skills[0] if skills else None
            if top_skill and top_skill.years_experience > 0:
                skills_para += (
                    f"I have {top_skill.years_experience:.0f} years of experience with "
                    f"{top_skill.name}, reaching {top_skill.proficiency.value} level proficiency. "
                )
            
            paragraphs.append(skills_para)
        
        # Projects paragraph
        if match_result.priority_projects:
            project = match_result.priority_projects[0]
            project_para = (
                f"One of my notable projects is {project.name}, where I {project.role or 'contributed'}. "
            )
            
            if project.technologies:
                techs = ', '.join(project.technologies[:3])
                project_para += f"This project utilized {techs}. "
            
            if project.highlights:
                project_para += project.highlights[0]
            
            paragraphs.append(project_para)
        
        # Experience paragraph (if any)
        if match_result.relevant_experience:
            exp = match_result.relevant_experience[0]
            exp_para = (
                f"During my time at {exp.company} as a {exp.position}, "
                f"I gained valuable experience "
            )
            
            if exp.achievements:
                exp_para += f"and achieved {exp.achievements[0].lower()}. "
            elif exp.responsibilities:
                exp_para += f"in {exp.responsibilities[0].lower()}. "
            else:
                exp_para += "that has prepared me for this role. "
            
            paragraphs.append(exp_para)
        
        # Why this company paragraph
        company_para = (
            f"I am particularly drawn to {job.company} because of its reputation "
            f"and the opportunity to work on meaningful projects. "
            f"I believe my skills and enthusiasm make me a strong candidate "
            f"for the {job.title} position."
        )
        paragraphs.append(company_para)
        
        return paragraphs
    
    def _generate_closing_paragraph(self, profile: UserProfile, job: JobOffer) -> str:
        """Generate closing paragraph."""
        closing = (
            f"I am excited about the possibility of joining {job.company} and "
            f"contributing to your team. I would welcome the opportunity to discuss "
            f"how my background and skills align with your needs. "
            f"Thank you for considering my application."
        )
        
        return closing
