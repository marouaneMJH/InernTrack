#!/usr/bin/env python3
"""
Quick test script to verify the internship sync pipeline components.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.logger_setup import get_logger
from src.config import settings
from src.normalizer import normalize_job, clean_html
from src.notion_client import NotionSync

logger = get_logger("test", "INFO")

def test_normalizer():
    """Test the normalizer functions."""
    logger.info("Testing normalizer functions...")
    
    # Test clean_html with different types
    assert clean_html("") == ""
    assert clean_html(None) == ""
    assert clean_html(3.14) == "3.14"
    assert clean_html("<p>Hello <b>world</b></p>") == "Hello world"
    
    # Test normalize_job with problematic data
    test_job = {
        "title": "Software Intern",
        "company": 123.45,  # float company name
        "location": None,
        "url": "https://example.com",
        "description": 456.78  # float description
    }
    
    result = normalize_job(test_job)
    assert isinstance(result["title"], str)
    assert isinstance(result["company"], str)
    assert isinstance(result["location"], str)
    assert result["company"] == "123.45"
    assert result["is_intern"] == True
    
    logger.info("✅ All normalizer tests passed!")

def test_config():
    """Test configuration loading."""
    logger.info("Testing configuration...")
    assert settings.SEARCH_TERMS is not None
    assert settings.LOCATIONS is not None
    assert isinstance(settings.RESULTS_WANTED, int)
    logger.info(f"Search terms: {settings.SEARCH_TERMS}")
    logger.info(f"Locations: {settings.LOCATIONS}")
    logger.info("✅ Configuration loaded successfully!")

def test_notion_connection():
    """Test Notion API connection and database access."""
    logger.info("Testing Notion connection...")
    
    if not settings.NOTION_TOKEN:
        logger.warning("⚠️ NOTION_TOKEN not set, skipping Notion tests")
        return
    
    try:
        notion = NotionSync(settings.NOTION_TOKEN)
        logger.info("✅ Notion client initialized successfully")
        
        # Test database access by querying companies
        if settings.DB_COMPANIES:
            logger.info(f"Testing access to Companies DB: {settings.DB_COMPANIES}")
            results = notion.find_page_by_property(
                settings.DB_COMPANIES, 
                "Name", 
                "NonExistentTestCompany"
            )
            logger.info(f"✅ Companies database accessible (found {len(results)} results)")
        
        # Test database access by querying offers
        if settings.DB_OFFERS:
            logger.info(f"Testing access to Offers DB: {settings.DB_OFFERS}")
            results = notion.find_page_by_property(
                settings.DB_OFFERS, 
                "Offer Title", 
                "NonExistentTestOffer"
            )
            logger.info(f"✅ Offers database accessible (found {len(results)} results)")
            
    except Exception as e:
        logger.error(f"❌ Notion connection failed: {e}")
        raise

def test_notion_upload_dry_run():
    """Test Notion upload functionality with sample data."""
    logger.info("Testing Notion upload with sample job data...")
    
    if not settings.NOTION_TOKEN:
        logger.warning("⚠️ NOTION_TOKEN not set, skipping upload test")
        return
    
    # Sample job data for testing
    sample_job = {
        "title": "Test Software Internship",
        "company": "Test Company Ltd",
        "location": "Morocco, Casablanca",
        "url": "https://test.example.com/job/12345",
        "description": "This is a test internship position for software development. Perfect for testing our sync pipeline.",
        "is_intern": True,
        "raw": {"source": "test"}
    }
    
    try:
        notion = NotionSync(settings.NOTION_TOKEN)
        
        # Test company creation (dry run check)
        logger.info("Testing company lookup/creation...")
        existing_companies = notion.find_page_by_property(
            settings.DB_COMPANIES, 
            "Name", 
            sample_job["company"]
        )
        
        if existing_companies:
            logger.info(f"✅ Found existing company: {sample_job['company']}")
        else:
            logger.info(f"Company '{sample_job['company']}' would be created")
        
        # Test offer creation (dry run check)
        logger.info("Testing offer lookup/creation...")
        existing_offers = notion.find_page_by_property(
            settings.DB_OFFERS, 
            "Offer Link", 
            sample_job["url"]
        )
        
        if existing_offers:
            logger.info(f"✅ Found existing offer with URL: {sample_job['url']}")
        else:
            logger.info(f"Offer '{sample_job['title']}' would be created")
        
        logger.info("✅ Notion upload test completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Notion upload test failed: {e}")
        raise

def test_notion_upload_real():
    """Test actual Notion upload (only if DRY_RUN=false)."""
    logger.info("Testing real Notion upload...")
    
    if settings.DRY_RUN:
        logger.info("⏭️ DRY_RUN=true, skipping real upload test")
        return
    
    if not settings.NOTION_TOKEN:
        logger.warning("⚠️ NOTION_TOKEN not set, skipping real upload test")
        return
    
    # Sample job data for testing with unique identifier
    import time
    timestamp = int(time.time())
    
    sample_job = {
        "title": f"Test Internship {timestamp}",
        "company": f"Test Company {timestamp}",
        "location": "Morocco",
        "url": f"https://test.example.com/job/{timestamp}",
        "description": f"This is a test internship created at {timestamp} for pipeline verification.",
        "is_intern": True,
        "raw": {"source": "test", "timestamp": timestamp}
    }
    
    try:
        notion = NotionSync(settings.NOTION_TOKEN)
        
        logger.info(f"Creating test company and offer: {sample_job['title']}")
        result = notion.ensure_company_and_offer(sample_job)
        
        if result:
            logger.info(f"✅ Successfully created test offer with ID: {result.get('id', 'unknown')}")
            logger.info("⚠️ Remember to clean up test data from your Notion databases!")
        else:
            logger.warning("⚠️ Upload completed but no result returned")
            
    except Exception as e:
        logger.error(f"❌ Real Notion upload test failed: {e}")
        raise

if __name__ == "__main__":
    logger.info("🔍 Running component tests...")
    
    # Basic component tests
    test_config()
    test_normalizer()
    
    # Notion tests
    test_notion_connection()
    test_notion_upload_dry_run()
    test_notion_upload_real()
    
    logger.info("🎉 All tests completed! Check the logs above for any issues.")