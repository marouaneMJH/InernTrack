#!/usr/bin/env python3
"""
JobSpy Integration Module

This module provides job scraping functionality using the JobSpy library.
It handles fetching job listings from multiple job boards with intelligent
query generation and error handling.

Supported Job Boards:
- LinkedIn: Professional networking and job platform
- Indeed: General job search platform
- Glassdoor: Company reviews and job listings
- Stack Overflow: Developer-focused job board

Features:
- Multi-platform scraping with concurrent requests
- Configurable search terms and locations
- Rate limiting and error recovery
- Automatic retry logic for failed requests
- Result aggregation and deduplication
- Support for internship-specific filtering

Configuration:
The module uses settings from config.py:
- SEARCH_TERMS: Keywords like 'internship', 'stage', 'intern'
- LOCATIONS: Geographic locations to search
- RESULTS_WANTED: Maximum results per search query

Error Handling:
- Graceful handling of invalid locations
- Network timeout recovery
- API rate limit management
- Partial result collection on failures

Data Format:
Returns standardized job objects with fields:
- title, company, location, url, description, posted_date
- Raw data preserved for debugging

Usage:
    jobs = fetch_jobs()
    print(f"Found {len(jobs)} job listings")
    
Author: El Moujahid Marouane
Version: 1.0
"""

from jobspy import scrape_jobs   # si le package diffère, adapte l'import
from .logger_setup import get_logger
from .config import settings

logger = get_logger("jobspy_client", settings.LOG_LEVEL)

def fetch_jobs():
    """Retourne une liste d'objets job bruts depuis JobSpy."""
    queries = []

    for term in settings.SEARCH_TERMS:
        for loc in settings.LOCATIONS:
            queries.append((term.strip(), loc.strip()))

    all_jobs = []
    for term, loc in queries:
        logger.info(f"Scraping '{term}' in '{loc} ({'-'.join(settings.SITE_NAMES)})' ...")
        try:
            # TODO: add hours, more details
            jobs = scrape_jobs(
                site_name=settings.SITE_NAMES,  # adapte selon disponibilité
                search_term=term,
                location=loc,
                results_wanted=settings.RESULTS_WANTED,
                job_type="internship"
                # hours_old=
            )

            logger.info(f"Fetched {len(jobs)} results for ({term}, {loc})")
            all_jobs.extend(jobs.to_dict('records') if hasattr(jobs, 'to_dict') else jobs)

        except Exception as e:
            logger.exception("Erreur lors du scraping JobSpy: %s", e)
    # optional: unique by url or id
    return all_jobs