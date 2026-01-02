"""
LaTeX Renderer Service

Renders content into LaTeX and compiles to PDF.
Single Responsibility: Template rendering and PDF compilation.

Author: El Moujahid Marouane
Version: 1.0
"""

import os
import re
import subprocess
import tempfile
import shutil
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime

from .content_generator import CVContent, CoverLetterContent

try:
    from ...logger_setup import get_logger
    from ...config import settings
except ImportError:
    from src.logger_setup import get_logger
    from src.config import settings

logger = get_logger("cv_generator.latex_renderer")


class LatexRendererService:
    """
    Service for rendering LaTeX templates and compiling to PDF.
    
    Handles template loading, placeholder substitution, and
    LaTeX compilation using pdflatex.
    """
    
    def __init__(self, template_dir: str = None, output_dir: str = None):
        """
        Initialize the renderer.
        
        Args:
            template_dir: Directory containing LaTeX templates
            output_dir: Directory for generated PDFs
        """
        self.template_dir = template_dir or self._get_default_template_dir()
        self.output_dir = output_dir or self._get_default_output_dir()
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _get_default_template_dir(self) -> str:
        """Get default template directory."""
        return os.path.join(os.path.dirname(__file__), '..', 'templates')
    
    def _get_default_output_dir(self) -> str:
        """Get default output directory."""
        return os.path.join(
            getattr(settings, 'DATA_DIR', 'data'),
            'generated_documents'
        )
    
    def render_cv(self, content: CVContent, filename: str = None) -> Tuple[str, Optional[str]]:
        """
        Render CV content to LaTeX and compile to PDF.
        
        Args:
            content: CVContent object with all sections
            filename: Optional output filename (without extension)
        
        Returns:
            Tuple of (latex_content, pdf_path or None if compilation failed)
        """
        logger.info("Rendering CV to LaTeX")
        
        # Load template
        template = self._load_template('cv_template.tex')
        
        # Substitute placeholders
        latex = self._substitute_cv_placeholders(template, content)
        
        # Generate filename
        if not filename:
            name = content.personal_info.get('name', 'cv').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cv_{name}_{timestamp}"
        
        # Compile to PDF
        pdf_path = self._compile_latex(latex, filename)
        
        return latex, pdf_path
    
    def render_cover_letter(self, content: CoverLetterContent, 
                            filename: str = None) -> Tuple[str, Optional[str]]:
        """
        Render cover letter content to LaTeX and compile to PDF.
        
        Args:
            content: CoverLetterContent object
            filename: Optional output filename (without extension)
        
        Returns:
            Tuple of (latex_content, pdf_path or None if compilation failed)
        """
        logger.info("Rendering cover letter to LaTeX")
        
        # Load template
        template = self._load_template('cover_letter_template.tex')
        
        # Substitute placeholders
        latex = self._substitute_cover_letter_placeholders(template, content)
        
        # Generate filename
        if not filename:
            company = content.recipient_info.get('company', 'company').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cover_letter_{company}_{timestamp}"
        
        # Compile to PDF
        pdf_path = self._compile_latex(latex, filename)
        
        return latex, pdf_path
    
    def _load_template(self, template_name: str) -> str:
        """Load a LaTeX template from file."""
        template_path = os.path.join(self.template_dir, template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _substitute_cv_placeholders(self, template: str, content: CVContent) -> str:
        """Substitute placeholders in CV template."""
        latex = template
        
        # Personal info
        info = content.personal_info
        latex = latex.replace('{{NAME}}', self._escape_latex(info.get('name', '')))
        latex = latex.replace('{{EMAIL}}', self._escape_latex(info.get('email', '')))
        latex = latex.replace('{{PHONE}}', self._escape_latex(info.get('phone', '')))
        latex = latex.replace('{{ADDRESS}}', self._escape_latex(info.get('address', '')))
        latex = latex.replace('{{LINKEDIN}}', info.get('linkedin', ''))
        latex = latex.replace('{{GITHUB}}', info.get('github', ''))
        latex = latex.replace('{{PORTFOLIO}}', info.get('portfolio', ''))
        
        # Summary
        latex = latex.replace('{{SUMMARY}}', self._escape_latex(content.summary))
        
        # Skills
        latex = latex.replace('{{SKILLS_SECTION}}', 
                             self._format_skills_latex(content.skills_section))
        
        # Experience
        latex = latex.replace('{{EXPERIENCE_SECTION}}', 
                             self._format_experience_latex(content.experience_section))
        
        # Education
        latex = latex.replace('{{EDUCATION_SECTION}}', 
                             self._format_education_latex(content.education_section))
        
        # Projects
        latex = latex.replace('{{PROJECTS_SECTION}}', 
                             self._format_projects_latex(content.projects_section))
        
        # Certifications (conditional section)
        if content.certifications_section:
            latex = latex.replace('{{#CERTIFICATIONS_SECTION}}', '')
            latex = latex.replace('{{/CERTIFICATIONS_SECTION}}', '')
            latex = latex.replace('{{CERTIFICATIONS_SECTION}}', 
                                 self._format_list_latex(content.certifications_section))
        else:
            # Remove the entire certifications section
            latex = re.sub(
                r'\{\{#CERTIFICATIONS_SECTION\}\}.*?\{\{/CERTIFICATIONS_SECTION\}\}',
                '', latex, flags=re.DOTALL
            )
        
        # Languages (conditional section)
        if content.languages_section:
            latex = latex.replace('{{#LANGUAGES_SECTION}}', '')
            latex = latex.replace('{{/LANGUAGES_SECTION}}', '')
            latex = latex.replace('{{LANGUAGES_SECTION}}', 
                                 self._escape_latex(content.languages_section))
        else:
            latex = re.sub(
                r'\{\{#LANGUAGES_SECTION\}\}.*?\{\{/LANGUAGES_SECTION\}\}',
                '', latex, flags=re.DOTALL
            )
        
        return latex
    
    def _substitute_cover_letter_placeholders(self, template: str, 
                                              content: CoverLetterContent) -> str:
        """Substitute placeholders in cover letter template."""
        latex = template
        
        # Sender info
        sender = content.sender_info
        latex = latex.replace('{{SENDER_NAME}}', self._escape_latex(sender.get('name', '')))
        latex = latex.replace('{{SENDER_EMAIL}}', self._escape_latex(sender.get('email', '')))
        latex = latex.replace('{{SENDER_PHONE}}', self._escape_latex(sender.get('phone', '')))
        latex = latex.replace('{{SENDER_ADDRESS}}', self._escape_latex(sender.get('address', '')))
        latex = latex.replace('{{DATE}}', sender.get('date', ''))
        
        # Recipient info
        recipient = content.recipient_info
        latex = latex.replace('{{COMPANY}}', self._escape_latex(recipient.get('company', '')))
        latex = latex.replace('{{POSITION}}', self._escape_latex(recipient.get('position', '')))
        latex = latex.replace('{{COMPANY_LOCATION}}', self._escape_latex(recipient.get('location', '')))
        
        # Content
        latex = latex.replace('{{OPENING_PARAGRAPH}}', 
                             self._escape_latex(content.opening_paragraph))
        
        # Body paragraphs (join with spacing)
        body_latex = '\n\n\\vspace{0.5em}\n\n'.join(
            self._escape_latex(p) for p in content.body_paragraphs
        )
        latex = latex.replace('{{BODY_PARAGRAPHS}}', body_latex)
        
        latex = latex.replace('{{CLOSING_PARAGRAPH}}', 
                             self._escape_latex(content.closing_paragraph))
        latex = latex.replace('{{SIGNATURE}}', 
                             self._escape_latex(content.signature).replace('\\n', '\\\\'))
        
        return latex
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        if not text:
            return ''
        
        # Characters that need escaping
        replacements = [
            ('\\', '\\textbackslash{}'),
            ('&', '\\&'),
            ('%', '\\%'),
            ('$', '\\$'),
            ('#', '\\#'),
            ('_', '\\_'),
            ('{', '\\{'),
            ('}', '\\}'),
            ('~', '\\textasciitilde{}'),
            ('^', '\\textasciicircum{}'),
        ]
        
        result = text
        for char, replacement in replacements:
            result = result.replace(char, replacement)
        
        return result
    
    def _format_skills_latex(self, skills_section: str) -> str:
        """Format skills section for LaTeX."""
        if not skills_section:
            return ''
        
        lines = []
        for line in skills_section.split('\n'):
            if line.strip():
                if ':' in line:
                    category, skills = line.split(':', 1)
                    lines.append(f"\\textbf{{{self._escape_latex(category)}:}} {self._escape_latex(skills.strip())}")
                else:
                    lines.append(self._escape_latex(line))
        
        return '\\\\[0.3em]\n'.join(lines)
    
    def _format_experience_latex(self, experience_section: str) -> str:
        """Format experience section for LaTeX."""
        if not experience_section:
            return ''
        
        entries = experience_section.split('\n\n')
        latex_entries = []
        
        for entry in entries:
            if not entry.strip():
                continue
            
            lines = entry.strip().split('\n')
            if len(lines) >= 2:
                # First line: position at company, location
                header = self._escape_latex(lines[0])
                # Second line: date range
                dates = self._escape_latex(lines[1])
                
                latex_entry = f"\\textbf{{{header}}}\\\\\\textit{{{dates}}}"
                
                # Remaining lines as bullet points
                if len(lines) > 2:
                    items = []
                    for line in lines[2:]:
                        if line.startswith('• '):
                            items.append(f"\\item {self._escape_latex(line[2:])}")
                        elif line.strip():
                            items.append(f"\\item {self._escape_latex(line)}")
                    
                    if items:
                        latex_entry += "\n\\begin{itemize}[leftmargin=*, nosep]\n"
                        latex_entry += '\n'.join(items)
                        latex_entry += "\n\\end{itemize}"
                
                latex_entries.append(latex_entry)
        
        return '\n\n\\vspace{0.5em}\n\n'.join(latex_entries)
    
    def _format_education_latex(self, education_section: str) -> str:
        """Format education section for LaTeX."""
        if not education_section:
            return ''
        
        entries = education_section.split('\n\n')
        latex_entries = []
        
        for entry in entries:
            if not entry.strip():
                continue
            
            lines = entry.strip().split('\n')
            latex_lines = []
            
            for i, line in enumerate(lines):
                if i == 0:
                    latex_lines.append(f"\\textbf{{{self._escape_latex(line)}}}")
                elif line.startswith('• '):
                    latex_lines.append(f"\\item {self._escape_latex(line[2:])}")
                else:
                    latex_lines.append(self._escape_latex(line))
            
            latex_entries.append('\\\\'.join(latex_lines))
        
        return '\n\n\\vspace{0.5em}\n\n'.join(latex_entries)
    
    def _format_projects_latex(self, projects_section: str) -> str:
        """Format projects section for LaTeX."""
        if not projects_section:
            return ''
        
        entries = projects_section.split('\n\n')
        latex_entries = []
        
        for entry in entries:
            if not entry.strip():
                continue
            
            lines = entry.strip().split('\n')
            latex_lines = []
            
            for i, line in enumerate(lines):
                if i == 0:
                    latex_lines.append(f"\\textbf{{{self._escape_latex(line)}}}")
                elif line.startswith('Technologies:'):
                    latex_lines.append(f"\\textit{{{self._escape_latex(line)}}}")
                elif line.startswith('• '):
                    latex_lines.append(f"\\item {self._escape_latex(line[2:])}")
                elif line.startswith('GitHub:') or line.startswith('Demo:'):
                    url = line.split(': ', 1)[1] if ': ' in line else ''
                    label = 'GitHub' if line.startswith('GitHub') else 'Demo'
                    latex_lines.append(f"\\href{{{url}}}{{{label}}}")
                else:
                    latex_lines.append(self._escape_latex(line))
            
            latex_entries.append('\\\\'.join(latex_lines))
        
        return '\n\n\\vspace{0.5em}\n\n'.join(latex_entries)
    
    def _format_list_latex(self, text: str) -> str:
        """Format a bullet list for LaTeX."""
        if not text:
            return ''
        
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('• '):
                items.append(f"\\item {self._escape_latex(line[2:])}")
            elif line:
                items.append(f"\\item {self._escape_latex(line)}")
        
        if items:
            return "\\begin{itemize}[leftmargin=*, nosep]\n" + '\n'.join(items) + "\n\\end{itemize}"
        return ''
    
    def _compile_latex(self, latex_content: str, filename: str) -> Optional[str]:
        """
        Compile LaTeX content to PDF.
        
        Args:
            latex_content: LaTeX source code
            filename: Output filename (without extension)
        
        Returns:
            Path to generated PDF or None if compilation failed
        """
        # Check if pdflatex is available
        if not self._check_pdflatex():
            logger.warning("pdflatex not found. Skipping PDF compilation.")
            return None
        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write LaTeX file
            tex_path = os.path.join(tmpdir, f"{filename}.tex")
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Run pdflatex twice (for references)
            try:
                for _ in range(2):
                    result = subprocess.run(
                        ['pdflatex', '-interaction=nonstopmode', '-output-directory', tmpdir, tex_path],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                
                # Check if PDF was created
                pdf_temp = os.path.join(tmpdir, f"{filename}.pdf")
                if os.path.exists(pdf_temp):
                    # Move to output directory
                    pdf_output = os.path.join(self.output_dir, f"{filename}.pdf")
                    shutil.copy2(pdf_temp, pdf_output)
                    logger.info(f"PDF generated: {pdf_output}")
                    return pdf_output
                else:
                    logger.error(f"PDF not generated. LaTeX output: {result.stdout}")
                    return None
                    
            except subprocess.TimeoutExpired:
                logger.error("pdflatex compilation timed out")
                return None
            except Exception as e:
                logger.error(f"PDF compilation failed: {e}")
                return None
    
    def _check_pdflatex(self) -> bool:
        """Check if pdflatex is available."""
        try:
            subprocess.run(['pdflatex', '--version'], 
                          capture_output=True, timeout=10)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def get_latex_only(self, content: CVContent) -> str:
        """Get only the LaTeX content without compilation."""
        template = self._load_template('cv_template.tex')
        return self._substitute_cv_placeholders(template, content)
    
    def get_cover_letter_latex_only(self, content: CoverLetterContent) -> str:
        """Get only the cover letter LaTeX content without compilation."""
        template = self._load_template('cover_letter_template.tex')
        return self._substitute_cover_letter_placeholders(template, content)
