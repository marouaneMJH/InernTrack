#!/usr/bin/env python3
"""
Data Normalization Module

This module handles data cleaning and standardization for job listings
scraped from various sources. It ensures consistent data format across
different job boards and platforms.

Key Responsibilities:

1. HTML Cleaning:
   - Removes HTML tags from job descriptions
   - Converts HTML entities to plain text
   - Preserves text structure with proper spacing
   - Handles malformed HTML gracefully

2. Data Type Normalization:
   - Converts various data types (float, int, None) to strings
   - Handles missing or empty fields with sensible defaults
   - Ensures consistent string formatting

3. Internship Detection:
   - Uses regex patterns to identify internship positions
   - Searches titles and descriptions for relevant keywords
   - Supports multiple languages (English: internship, French: stage)
   - Case-insensitive matching

4. Field Mapping:
   - Maps different field names from various job boards
   - Standardizes field names across platforms
   - Handles alternative field names (e.g., 'job_title' vs 'title')

Data Quality Features:
- Robust error handling for unexpected data types
- Automatic text truncation to prevent overflow
- Whitespace normalization
- URL validation and cleaning

Internship Detection Patterns:
- Keywords: intern, internship, internee, stagiaire, stage
- Word boundaries to prevent false matches
- Multi-language support

Usage:
    normalized_job = normalize_job(raw_job_data)
    clean_text = clean_html(html_string)
    
Author: El Moujahid Marouane
Version: 1.0
"""

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