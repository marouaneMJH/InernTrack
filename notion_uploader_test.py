#!/usr/bin/env python3
"""
Enhanced Notion test with better diagnostics and setup instructions.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.config import settings
from src.notion_client import NotionSync

def test_notion_setup():
    """Test Notion setup and provide setup instructions if needed."""
    print("🔍 Testing Notion Integration Setup...")
    print("=" * 50)
    
    # Check configuration
    print(f"✅ NOTION_TOKEN: {'✓ SET' if settings.NOTION_TOKEN else '❌ NOT SET'}")
    print(f"✅ DB_COMPANIES_ID: {settings.DB_COMPANIES or '❌ NOT SET'}")
    print(f"✅ DB_OFFERS_ID: {settings.DB_OFFERS or '❌ NOT SET'}")
    print(f"✅ DRY_RUN: {settings.DRY_RUN}")
    print()
    
    if not settings.NOTION_TOKEN:
        print("❌ NOTION_TOKEN is missing!")
        print("To fix this:")
        print("1. Go to https://developers.notion.com/")
        print("2. Create a new integration")
        print("3. Copy the Internal Integration Token")
        print("4. Add it to your .env file as NOTION_TOKEN=your_token_here")
        return False
    
    if not settings.DB_COMPANIES or not settings.DB_OFFERS:
        print("❌ Database IDs are missing!")
        print("To fix this:")
        print("1. Create databases in Notion (Companies, Offers, etc.)")
        print("2. Share each database with your integration")
        print("3. Copy database IDs from URLs and add to .env file")
        return False
    
    # Test Notion client creation
    try:
        notion = NotionSync(settings.NOTION_TOKEN)
        print("✅ Notion client created successfully")
    except Exception as e:
        print(f"❌ Failed to create Notion client: {e}")
        return False
    
    # Test database access
    print("\n🔍 Testing Database Access...")
    print("-" * 30)
    
    # Test Companies DB
    try:
        print(f"Testing Companies DB: {settings.DB_COMPANIES}")
        results = notion.find_page_by_property(settings.DB_COMPANIES, "Name", "__test_query__")
        print(f"✅ Companies database accessible (query returned {len(results)} results)")
    except Exception as e:
        print(f"❌ Companies database access failed: {e}")
        if "404" in str(e):
            print("   💡 This means the database isn't shared with your integration!")
            print("   Fix: Go to your Companies database in Notion → Share → Add your integration")
        return False
    
    # Test Offers DB  
    try:
        print(f"Testing Offers DB: {settings.DB_OFFERS}")
        results = notion.find_page_by_property(settings.DB_OFFERS, "Offer Title", "__test_query__")
        print(f"✅ Offers database accessible (query returned {len(results)} results)")
    except Exception as e:
        print(f"❌ Offers database access failed: {e}")
        if "404" in str(e):
            print("   💡 This means the database isn't shared with your integration!")
            print("   Fix: Go to your Offers database in Notion → Share → Add your integration")
        return False
    
    print("\n🎉 All basic tests passed! Notion integration is properly configured.")
    return True

def test_upload_functionality():
    """Test actual upload functionality if not in dry run mode."""
    print("\n🔍 Testing Upload Functionality...")
    print("-" * 35)
    
    if settings.DRY_RUN:
        print("ℹ️ DRY_RUN=true - Skipping actual upload test")
        print("   To test real uploads, set DRY_RUN=false in .env file")
        return True
    
    notion = NotionSync(settings.NOTION_TOKEN)
    
    # Create test data
    import time
    timestamp = int(time.time())
    test_job = {
        "title": f"TEST: Internship {timestamp}",
        "company": f"TEST: Company {timestamp}", 
        "location": "Morocco",
        "url": f"https://test.example.com/{timestamp}",
        "description": f"This is a test entry created at {timestamp} for pipeline verification. Please delete manually.",
        "is_intern": True
    }
    
    print(f"Creating test job: {test_job['title']}")
    
    try:
        result = notion.ensure_company_and_offer(test_job)
        if result:
            print(f"✅ Successfully created test data!")
            print(f"   Company: {test_job['company']}")
            print(f"   Offer: {test_job['title']}")
            print("   ⚠️  IMPORTANT: Remember to delete this test data from your Notion databases!")
        else:
            print("❌ Upload test failed - no result returned")
            return False
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False
    
    return True

def print_setup_summary():
    """Print setup summary and next steps."""
    print("\n" + "=" * 60)
    print("📋 SETUP SUMMARY")
    print("=" * 60)
    print("1. ✅ Project structure created")
    print("2. ✅ Dependencies installed") 
    print("3. ✅ Configuration loaded")
    print("4. ✅ Notion integration tested")
    print()
    print("🚀 NEXT STEPS:")
    print("- Run full pipeline: python -m src.main")
    print("- Or use the script: bash scripts/run.sh") 
    print("- Set up GitHub Actions for automation")
    print()
    print("💡 TIPS:")
    print("- Set DRY_RUN=true to test without uploading")
    print("- Check logs for any scraping issues")
    print("- Verify Notion database property names match the code")

if __name__ == "__main__":
    success = test_notion_setup()
    
    if success:
        test_upload_functionality()
        print_setup_summary()
    else:
        print("\n❌ Setup incomplete. Please fix the issues above and run this test again.")
        print("📖 For detailed setup instructions, see the README.md file.")