#!/usr/bin/env python3
"""
Simple Notion Connection Test

Minimal test script for quickly validating Notion API connectivity
and basic functionality. Designed for rapid debugging and setup
verification without complex test frameworks.

Author: El Moujahid Marouane
Version: 1.0
"""

import sys
import os
import time

# Adjust PYTHONPATH to reach the project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, ROOT_DIR)

print("Starting simple test...")

# Example job payload (correct Python syntax)
job = {
    "company": "ALX South Africa",
    "description": "nan",
    "is_intern": True,
    "location": "Rabat, Rabat-Salé-Kénitra, Morocco",
    "raw": {
        "company": "ALX South Africa",
        "company_addresses": None,
        "company_description": None,
        "company_industry": None,
        "company_logo": None,
        "company_num_employees": None,
        "company_rating": None,
        "company_revenue": None,
        "company_reviews_count": None,
        "company_url": "https://za.linkedin.com/company/alx-africa-sa",
        "company_url_direct": None,
        "currency": None,
        "date_posted": None,
        "description": None,
        "emails": None,
        "experience_range": None,
        "id": "li-4339454142",
        "interval": None,
        "is_remote": False,
        "job_function": None,
        "job_level": "",
        "job_type": None,
        "job_url": "https://www.linkedin.com/jobs/view/4339454142",
        "job_url_direct": None,
        "listing_type": None,
        "location": "Rabat, Rabat-Salé-Kénitra, Morocco",
        "max_amount": None,
        "min_amount": None,
        "salary_source": None,
        "site": "linkedin",
        "skills": None,
        "title": "Hub Operations Intern",
        "vacancy_count": None,
        "work_from_home_type": None,
    },
    "title": "Hub Operations Intern",
    "url": "https://www.linkedin.com/jobs/view/4339454142",
}


def main():
    try:
        from src.config import settings
        print(f"✅ Config loaded - DRY_RUN: {settings.DRY_RUN}")
        print(f"✅ NOTION_TOKEN: {'SET' if settings.NOTION_TOKEN else 'NOT SET'}")

        from src.notion_client import NotionSync
        print("✅ NotionSync imported")

        if not settings.NOTION_TOKEN:
            print("❌ No NOTION_TOKEN found – aborting Notion tests")
            return

        notion = NotionSync(settings.NOTION_TOKEN)
        print("✅ Notion client created")

        # 1) Simple connectivity / query test on companies DB
        if settings.DB_COMPANIES:
            print(f"ℹ️ Testing companies DB: {settings.DB_COMPANIES}")
            results = notion.find_page_by_property(
                settings.DB_COMPANIES,
                "Name",      # will work if your title property is "Name"
                "TestQuery", # arbitrary value, just to validate the call
            )
            print(f"✅ Query successful, found {len(results)} results")

        # 2) Optional upload test (company + offer)
        if not settings.DRY_RUN:
            print("⚠️ DRY_RUN is FALSE - real upload test will run!")
            print("Creating test data...")

            timestamp = int(time.time())
            test_job = {
                "title": f"{job['title']} [{timestamp}]",
                "company": job["company"],
                "location": job["location"],
                "url": job["url"],
                "description": job["description"],
                "is_intern": job["is_intern"],
                "raw": job["raw"],
            }

            result = notion.ensure_company_and_offer(test_job)
            print(f"✅ Upload test completed: {result}")
        else:
            print("ℹ️ DRY_RUN enabled - skipping actual upload")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Test completed!")


if __name__ == "__main__":
    main()
