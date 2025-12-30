#!/usr/bin/env python3
"""
Internship Sync - Main Pipeline Module

This is the main entry point for the internship synchronization pipeline.
It orchestrates the complete workflow:

1. Fetches job listings from multiple sources using JobSpy
2. Normalizes and filters internship-specific positions
3. Removes duplicate entries
4. Syncs data to Notion databases (companies and offers)

The pipeline supports:
- Multi-site scraping (LinkedIn, Indeed, Glassdoor)
- Intelligent internship filtering using keyword detection
- Dry-run mode for testing without actual Notion updates
- Comprehensive logging and error handling

Usage:
    python -m src.main
    
Environment Variables:
    NOTION_TOKEN: Required Notion integration token
    DB_COMPANIES_ID: Companies database ID in Notion
    DB_OFFERS_ID: Job offers database ID in Notion
    DRY_RUN: Set to 'true' to test without uploading
    
Author: El Moujahid Marouane
Version: 1.0
"""

from .logger_setup import get_logger
from .config import settings
from .jobspy_client import fetch_jobs
from .normalizer import normalize_job
from .dedupe import dedupe_by_url
from .database_client import DatabaseClient
import json

logger = get_logger("main", settings.LOG_LEVEL)



def main():
    logger.info("Start pipeline")
    
    # Initialize database client
    try:
        db = DatabaseClient()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return
    
    # Fetch raw jobs
    raw_jobs = fetch_jobs()
    logger.info("Raw jobs fetched: %d", len(raw_jobs))
    
    if not raw_jobs:
        logger.warning("No jobs fetched, exiting")
        return
    
    # Normalize and filter
    normalized = [normalize_job(rj) for rj in raw_jobs if rj]
    interns = [j for j in normalized if j.get("is_intern")]
    logger.info("Filtered internships: %d", len(interns))
    
    # Deduplicate
    unique = dedupe_by_url(interns)
    logger.info("After dedupe: %d", len(unique))
    
    if not unique:
        logger.info("No unique internship offers to process")
        return


    # Process each job
    success_count = 0

    for job in unique:
        logger.info("Processing: %s - %s", job["company"], job["title"])
        
        if settings.DRY_RUN:
            logger.info("[DRY RUN] Would create company and internship for: %s", job.get("url", "No URL"))
            success_count += 1
            continue
        
        try:
            
            pretty = json.dumps(job, indent=2, ensure_ascii=False, sort_keys=True)
            logger.info("Job details:\n%s", pretty)

            result = db.ensure_company_and_internship(job)
            if result:
                success_count += 1
        except Exception as e:
            logger.exception("Failed to sync job: ")

    # Show database statistics
    try:
        stats = db.get_stats()
        logger.info("Database statistics:")
        for table, count in stats.items():
            logger.info(f"  {table}: {count} records")
    except Exception as e:
        logger.error(f"Failed to get database statistics: {e}")

    logger.info("Pipeline completed. Successfully processed: %d/%d jobs", success_count, len(unique))

if __name__ == "__main__":
    main()