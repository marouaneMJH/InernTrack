#!/usr/bin/env python3
"""
Simple Notion Connection Test

Minimal test script for quickly validating Notion API connectivity
and basic functionality. Designed for rapid debugging and setup
verification without complex test frameworks.

Test Scope:
- Notion client initialization
- Basic API connectivity
- Database access validation
- Simple query execution
- Optional upload testing

Features:
- Minimal dependencies
- Clear pass/fail indicators
- Detailed error reporting
- Configuration validation
- Safe test data creation

Output Format:
- ✅ Success indicators
- ❌ Error indicators with details
- ℹ️ Informational messages
- ⚠️ Warning messages

Safety:
- Respects DRY_RUN configuration
- Creates uniquely identified test data
- Provides cleanup instructions
- Minimal API impact

Usage:
    python __test__/simple_notion_test.py
    
Prerequisites:
- Valid NOTION_TOKEN in environment
- Properly configured database IDs
- Databases shared with integration

Author: El Moujahid Marouane
Version: 1.0
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("Starting simple test...")

try:
    from src.config import settings
    print(f"✅ Config loaded - DRY_RUN: {settings.DRY_RUN}")
    print(f"✅ NOTION_TOKEN: {'SET' if settings.NOTION_TOKEN else 'NOT SET'}")
    
    from src.notion_client import NotionSync
    print("✅ NotionSync imported")
    
    if settings.NOTION_TOKEN:
        notion = NotionSync(settings.NOTION_TOKEN)
        print("✅ Notion client created")
        
        # Simple test query
        if settings.DB_COMPANIES:
            print(f"Testing companies DB: {settings.DB_COMPANIES}")
            results = notion.find_page_by_property(
                settings.DB_COMPANIES, 
                "Name", 
                "TestQuery"
            )
            print(f"✅ Query successful, found {len(results)} results")
        
        if not settings.DRY_RUN:
            print("⚠️ DRY_RUN is FALSE - real upload test will run!")
            print("Creating test data...")
            
            import time
            timestamp = int(time.time())
            test_job = {
                "title": f"Test Job {timestamp}",
                "company": f"Test Company {timestamp}",
                "location": "Morocco",
                "url": f"https://test.example/{timestamp}",
                "description": "Test description",
                "is_intern": True
            }
            
            result = notion.ensure_company_and_offer(test_job)
            print(f"✅ Upload test completed: {result}")
            
        else:
            print("ℹ️ DRY_RUN enabled - skipping actual upload")
            
    else:
        print("❌ No NOTION_TOKEN found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed!")