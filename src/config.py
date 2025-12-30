#!/usr/bin/env python3
"""
Configuration Management Module

This module handles all configuration settings for the internship sync pipeline.
It loads environment variables from .env files and provides a centralized
Settings class for accessing configuration throughout the application.

Configuration Categories:

1. Notion API Settings:
   - NOTION_TOKEN: Authentication token for Notion API
   - Database IDs for companies, offers, applications, contacts, documents

2. Job Scraping Settings:
   - SEARCH_TERMS: Keywords to search for (comma-separated)
   - LOCATIONS: Geographic locations to search (comma-separated)
   - RESULTS_WANTED: Maximum results per search query

3. Application Behavior:
   - DRY_RUN: Boolean flag for testing mode
   - LOG_LEVEL: Logging verbosity level

The settings are loaded automatically when the module is imported,
making configuration available as `settings.PROPERTY_NAME`.

Example:
    from src.config import settings
    print(f"Dry run mode: {settings.DRY_RUN}")
    
Author: El Moujahid Marouane
Version: 1.0
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database configuration
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/internship_sync.db")
    
    
    # JobSpy / Scraper settings
    SEARCH_TERMS = os.getenv("SEARCH_TERMS").split(",")
    LOCATIONS = os.getenv("LOCATIONS", "Morocco").split(",")
    SITE_NAMES = os.getenv("SITE_NAMES").split(",")
    RESULTS_WANTED = int(os.getenv("RESULTS_WANTED", "50"))
    DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()