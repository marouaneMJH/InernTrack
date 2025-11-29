#!/usr/bin/env python3
"""
Internship Sync Package
A comprehensive Python package for automatically scraping internship
opportunities from multiple job boards and synchronizing them with
Notion databases for organized tracking and management.
Package Structure:
- main.py: Main pipeline orchestration and entry point
- config.py: Configuration management and environment variables
- logger_setup.py: Centralized logging configuration
- jobspy_client.py: Job scraping functionality using JobSpy
- normalizer.py: Data cleaning and standardization
- dedupe.py: Duplicate detection and removal
- notion_client.py: Notion API integration and database management
Key Features:
1. Multi-Platform Scraping:
   - LinkedIn, Indeed, Glassdoor integration
   - Intelligent internship detection
   - Configurable search parameters
   - Rate limiting and error handling
2. Data Processing:
   - HTML content cleaning
   - Data normalization across platforms
   - Duplicate detection and removal
   - Type safety and validation
3. Notion Integration:
   - Automated company and offer creation
   - Relationship management
   - Database schema support
   - Error recovery and validation
4. Configuration Management:
   - Environment-based configuration
   - Dry-run mode for testing
   - Comprehensive logging
   - Security best practices
Usage:
    from src import main
    from src.config import settings
    from src.logger_setup import get_logger
    
    # Run the main pipeline
    main.main()
    
    # Or use individual components
    logger = get_logger('my_module')
    logger.info(f'Dry run mode: {settings.DRY_RUN}')
Version: 1.0
Author: El Moujahid Marouane
License: MIT
\"\"\"
__version__ = \"1.0.0\"
__author__ = \"El Moujahid Marouane\"
__email__ = \"ai@assistant.com\"
__description__ = \"Automated internship scraping and Notion synchronization\"
# Package metadata
__all__ = [
    'main',
    'config', 
    'logger_setup',
    'jobspy_client',
    'normalizer',
    'dedupe',
    'notion_client'
]
"""