from bs4 import BeautifulSoup
from .logger_setup import get_logger
import re

logger = get_logger("normalizer")

def clean_html(html_text):
    if not html_text:
        return ""
    # Convert to string if it's not already
    if not isinstance(html_text, str):
        html_text = str(html_text)
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def normalize_job(raw_job):
    """Transforme l'objet JobSpy en structure standardisée."""
    title = raw_job.get("title") or raw_job.get("job_title")
    company = raw_job.get("company") or raw_job.get("company_name")
    location = raw_job.get("location") or raw_job.get("city")
    url = raw_job.get("url") or raw_job.get("link") or raw_job.get("job_url")
    desc = clean_html(raw_job.get("description") or raw_job.get("snippet") or "")
    
    # Convert to string if not already
    title = str(title) if title is not None else "No title"
    company = str(company) if company is not None else "Unknown"
    location = str(location) if location is not None else ""
    
    # tag detection
    is_intern = bool(re.search(r"\bintern(ship|ee)?\b|stagiaire|stage", title + " " + (desc or ""), re.I))
    return {
        "title": title.strip() if title else "No title",
        "company": company.strip() if company else "Unknown",
        "location": location.strip() if location else "",
        "url": url,
        "description": desc,
        "is_intern": is_intern,
        "raw": raw_job
    }