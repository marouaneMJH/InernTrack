"""
Matching Service

Matches user profiles against job descriptions.
Uses keyword extraction and scoring algorithms.
Single Responsibility: Profile-to-job matching logic.

Author: El Moujahid Marouane
Version: 1.0
"""

import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field
from collections import Counter

from ..models import (
    UserProfile, Skill, Project, Experience, MatchResult,
    SkillCategory, ProficiencyLevel
)

try:
    from ...logger_setup import get_logger
except ImportError:
    from src.logger_setup import get_logger

logger = get_logger("cv_generator.matching_service")


# Common technical keywords and their variations
SKILL_SYNONYMS = {
    'python': ['python', 'python3', 'py'],
    'javascript': ['javascript', 'js', 'es6', 'es2015', 'ecmascript'],
    'typescript': ['typescript', 'ts'],
    'react': ['react', 'reactjs', 'react.js'],
    'vue': ['vue', 'vuejs', 'vue.js'],
    'angular': ['angular', 'angularjs'],
    'node': ['node', 'nodejs', 'node.js'],
    'java': ['java', 'jdk', 'jre'],
    'csharp': ['c#', 'csharp', '.net', 'dotnet'],
    'cpp': ['c++', 'cpp'],
    'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'mssql'],
    'nosql': ['nosql', 'mongodb', 'redis', 'cassandra', 'dynamodb'],
    'docker': ['docker', 'containerization', 'containers'],
    'kubernetes': ['kubernetes', 'k8s'],
    'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
    'azure': ['azure', 'microsoft azure'],
    'gcp': ['gcp', 'google cloud', 'google cloud platform'],
    'git': ['git', 'github', 'gitlab', 'bitbucket', 'version control'],
    'ci/cd': ['ci/cd', 'cicd', 'continuous integration', 'continuous deployment', 'jenkins', 'github actions'],
    'agile': ['agile', 'scrum', 'kanban', 'sprint'],
    'rest': ['rest', 'restful', 'rest api', 'api'],
    'graphql': ['graphql', 'gql'],
    'machine learning': ['machine learning', 'ml', 'deep learning', 'dl', 'ai', 'artificial intelligence'],
    'data science': ['data science', 'data analysis', 'analytics', 'pandas', 'numpy'],
}

# Soft skills keywords
SOFT_SKILL_KEYWORDS = [
    'communication', 'teamwork', 'leadership', 'problem solving', 'problem-solving',
    'critical thinking', 'adaptability', 'flexibility', 'creativity', 'time management',
    'organization', 'attention to detail', 'initiative', 'self-motivated', 'collaborative',
    'interpersonal', 'presentation', 'negotiation', 'conflict resolution', 'mentoring',
]


@dataclass
class JobOffer:
    """Represents a job offer for matching."""
    title: str = ""
    description: str = ""
    company: str = ""
    requirements: str = ""
    skills: List[str] = field(default_factory=list)
    location: str = ""
    
    @property
    def full_text(self) -> str:
        """Get full text for analysis."""
        return f"{self.title} {self.description} {self.requirements} {' '.join(self.skills)}"


class MatchingService:
    """
    Service for matching user profiles against job offers.
    
    Uses keyword extraction, synonym matching, and scoring
    to determine how well a profile fits a job.
    """
    
    def __init__(self):
        self.skill_synonyms = SKILL_SYNONYMS
        self.soft_skill_keywords = SOFT_SKILL_KEYWORDS
    
    def match(self, profile: UserProfile, job: JobOffer) -> MatchResult:
        """
        Match a user profile against a job offer.
        
        Returns a MatchResult with scores and prioritized items.
        """
        logger.info(f"Matching profile against job: {job.title} at {job.company}")
        
        # Extract keywords from job
        job_keywords = self._extract_keywords(job.full_text)
        
        # Match skills
        matched_skills, skill_gaps = self._match_skills(profile.skills, job_keywords)
        
        # Match projects
        matched_projects = self._match_projects(profile.projects, job_keywords)
        
        # Match experience
        relevant_experience = self._match_experience(profile.experience, job_keywords)
        
        # Calculate overall score
        overall_score = self._calculate_score(
            matched_skills, skill_gaps, matched_projects, 
            relevant_experience, profile, job_keywords
        )
        
        # Prioritize items for CV
        priority_skills = self._prioritize_skills(matched_skills, job_keywords)
        priority_projects = self._prioritize_projects(matched_projects, job_keywords)
        
        # Get keyword match counts
        keyword_matches = self._count_keyword_matches(profile, job_keywords)
        
        result = MatchResult(
            overall_score=overall_score,
            matched_skills=matched_skills,
            matched_projects=matched_projects,
            skill_gaps=skill_gaps,
            priority_skills=priority_skills[:6],  # Top 6 skills
            priority_projects=priority_projects[:3],  # Top 3 projects
            relevant_experience=relevant_experience,
            keyword_matches=keyword_matches,
        )
        
        logger.info(f"Match complete. Score: {overall_score:.1f}%")
        return result
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract relevant keywords from text."""
        text_lower = text.lower()
        keywords = set()
        
        # Extract technical skills using synonyms
        for canonical, variations in self.skill_synonyms.items():
            for variation in variations:
                if variation in text_lower:
                    keywords.add(canonical)
                    break
        
        # Extract common programming patterns
        # Look for specific technologies mentioned
        tech_patterns = [
            r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|go|rust|swift|kotlin)\b',
            r'\b(react|vue|angular|django|flask|spring|express|rails)\b',
            r'\b(mysql|postgresql|mongodb|redis|elasticsearch)\b',
            r'\b(docker|kubernetes|aws|azure|gcp)\b',
            r'\b(git|jenkins|terraform|ansible)\b',
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower)
            keywords.update(matches)
        
        # Extract soft skills
        for skill in self.soft_skill_keywords:
            if skill in text_lower:
                keywords.add(skill)
        
        # Extract years of experience requirements
        exp_match = re.search(r'(\d+)\+?\s*years?\s*(of)?\s*experience', text_lower)
        if exp_match:
            keywords.add(f"{exp_match.group(1)}_years_exp")
        
        return keywords
    
    def _match_skills(self, skills: List[Skill], job_keywords: Set[str]) -> Tuple[List[Skill], List[str]]:
        """Match user skills against job keywords."""
        matched = []
        user_skill_names = set()
        
        for skill in skills:
            skill_lower = skill.name.lower()
            user_skill_names.add(skill_lower)
            
            # Check direct match
            if skill_lower in job_keywords:
                matched.append(skill)
                continue
            
            # Check synonym match
            for canonical, variations in self.skill_synonyms.items():
                if skill_lower in variations or canonical == skill_lower:
                    if canonical in job_keywords:
                        matched.append(skill)
                        break
            
            # Check if any skill keyword matches
            for keyword in skill.keywords:
                if keyword.lower() in job_keywords:
                    matched.append(skill)
                    break
        
        # Find skill gaps (skills in job but not in profile)
        skill_gaps = []
        for keyword in job_keywords:
            # Skip non-technical keywords
            if keyword in self.soft_skill_keywords:
                continue
            if '_years_exp' in keyword:
                continue
                
            # Check if user has this skill
            has_skill = False
            for skill in skills:
                skill_lower = skill.name.lower()
                if skill_lower == keyword:
                    has_skill = True
                    break
                # Check synonyms
                for canonical, variations in self.skill_synonyms.items():
                    if canonical == keyword and (skill_lower in variations or skill_lower == canonical):
                        has_skill = True
                        break
            
            if not has_skill and keyword in self.skill_synonyms:
                skill_gaps.append(keyword)
        
        return matched, skill_gaps
    
    def _match_projects(self, projects: List[Project], job_keywords: Set[str]) -> List[Project]:
        """Match projects based on technologies and descriptions."""
        matched = []
        
        for project in projects:
            # Check technologies
            project_techs = [t.lower() for t in project.technologies]
            
            for tech in project_techs:
                if tech in job_keywords:
                    matched.append(project)
                    break
                # Check synonyms
                for canonical, variations in self.skill_synonyms.items():
                    if tech in variations and canonical in job_keywords:
                        matched.append(project)
                        break
            
            if project not in matched:
                # Check description for keywords
                desc_lower = project.description.lower()
                for keyword in job_keywords:
                    if keyword in desc_lower:
                        matched.append(project)
                        break
        
        return matched
    
    def _match_experience(self, experiences: List[Experience], job_keywords: Set[str]) -> List[Experience]:
        """Match experience based on technologies and descriptions."""
        relevant = []
        
        for exp in experiences:
            # Check technologies used
            exp_techs = [t.lower() for t in exp.technologies_used]
            
            for tech in exp_techs:
                if tech in job_keywords:
                    relevant.append(exp)
                    break
                # Check synonyms
                for canonical, variations in self.skill_synonyms.items():
                    if tech in variations and canonical in job_keywords:
                        relevant.append(exp)
                        break
            
            if exp not in relevant:
                # Check description and responsibilities
                text = f"{exp.description} {' '.join(exp.responsibilities)}".lower()
                for keyword in job_keywords:
                    if keyword in text:
                        relevant.append(exp)
                        break
        
        return relevant
    
    def _calculate_score(self, matched_skills: List[Skill], skill_gaps: List[str],
                         matched_projects: List[Project], relevant_experience: List[Experience],
                         profile: UserProfile, job_keywords: Set[str]) -> float:
        """Calculate overall match score (0-100)."""
        score = 0.0
        
        # Skill match score (40% weight)
        total_job_skills = len([k for k in job_keywords if k in self.skill_synonyms])
        if total_job_skills > 0:
            skill_score = (len(matched_skills) / max(total_job_skills, 1)) * 40
            score += min(skill_score, 40)
        else:
            score += 20  # Neutral if no specific skills detected
        
        # Project relevance (25% weight)
        if profile.projects:
            project_score = (len(matched_projects) / len(profile.projects)) * 25
            score += project_score
        
        # Experience relevance (25% weight)
        if profile.experience:
            exp_score = (len(relevant_experience) / len(profile.experience)) * 25
            score += exp_score
        
        # Proficiency bonus (10% weight)
        advanced_skills = [s for s in matched_skills 
                          if s.proficiency in [ProficiencyLevel.ADVANCED, ProficiencyLevel.EXPERT]]
        if matched_skills:
            proficiency_score = (len(advanced_skills) / len(matched_skills)) * 10
            score += proficiency_score
        
        return min(score, 100)
    
    def _prioritize_skills(self, matched_skills: List[Skill], job_keywords: Set[str]) -> List[Skill]:
        """Prioritize skills based on relevance and proficiency."""
        def skill_priority(skill: Skill) -> Tuple[int, int, float]:
            # Priority: (keyword_match, proficiency, experience)
            keyword_match = 1 if skill.name.lower() in job_keywords else 0
            proficiency_order = {
                ProficiencyLevel.EXPERT: 4,
                ProficiencyLevel.ADVANCED: 3,
                ProficiencyLevel.INTERMEDIATE: 2,
                ProficiencyLevel.BEGINNER: 1,
            }
            return (keyword_match, proficiency_order.get(skill.proficiency, 0), skill.years_experience)
        
        return sorted(matched_skills, key=skill_priority, reverse=True)
    
    def _prioritize_projects(self, matched_projects: List[Project], job_keywords: Set[str]) -> List[Project]:
        """Prioritize projects based on relevance."""
        def project_priority(project: Project) -> int:
            # Count matching technologies
            count = 0
            for tech in project.technologies:
                if tech.lower() in job_keywords:
                    count += 1
                for canonical, variations in self.skill_synonyms.items():
                    if tech.lower() in variations and canonical in job_keywords:
                        count += 1
            return count
        
        return sorted(matched_projects, key=project_priority, reverse=True)
    
    def _count_keyword_matches(self, profile: UserProfile, job_keywords: Set[str]) -> Dict[str, int]:
        """Count how many times each keyword appears in the profile."""
        counts = Counter()
        
        # Count in skills
        for skill in profile.skills:
            skill_lower = skill.name.lower()
            if skill_lower in job_keywords:
                counts[skill_lower] += 1
            for keyword in skill.keywords:
                if keyword.lower() in job_keywords:
                    counts[keyword.lower()] += 1
        
        # Count in projects
        for project in profile.projects:
            for tech in project.technologies:
                if tech.lower() in job_keywords:
                    counts[tech.lower()] += 1
        
        # Count in experience
        for exp in profile.experience:
            for tech in exp.technologies_used:
                if tech.lower() in job_keywords:
                    counts[tech.lower()] += 1
        
        return dict(counts)
    
    def create_job_offer_from_internship(self, internship: dict) -> JobOffer:
        """Create a JobOffer from an internship database record."""
        return JobOffer(
            title=internship.get('title', ''),
            description=internship.get('description', ''),
            company=internship.get('company_name', ''),
            requirements=internship.get('requirements', ''),
            skills=internship.get('skills', '').split(',') if internship.get('skills') else [],
            location=internship.get('location', ''),
        )
