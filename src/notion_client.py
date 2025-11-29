#!/usr/bin/env python3
"""
Notion API Integration Module

This module provides a comprehensive interface for interacting with Notion databases
in the internship sync pipeline. It handles:

- Database queries and page searches
- Company and job offer creation
- Property mapping and validation
- Error handling and recovery
- Relationship management between databases

The module uses the official Notion Python client and implements proper
error handling, rate limiting, and data validation to ensure reliable
operation with Notion's API.

Key Features:
- Automatic property discovery and mapping
- Duplicate detection and prevention
- Comprehensive error logging
- Support for various Notion property types
- Robust API error handling

Author: El Moujahid Marouane
Version: 1.0
"""

from notion_client import Client
from .config import settings
from .logger_setup import get_logger
import time
import re

logger = get_logger("notion_client", settings.LOG_LEVEL)

class NotionSync:
    def __init__(self, token):
        self.client = Client(auth=token)
        self._db_schemas = {}  # Cache for database schemas
        
    def get_database_schema(self, db_id):
        """Get and cache database schema to understand property names"""
        if db_id in self._db_schemas:
            return self._db_schemas[db_id]
            
        try:
            db = self.client.databases.retrieve(database_id=db_id)
            properties = db.get("properties", {})
            
            # Find title property
            title_prop = None
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "title":
                    title_prop = prop_name
                    break
            
            schema = {
                "title_property": title_prop,
                "properties": properties
            }
            
            self._db_schemas[db_id] = schema
            logger.info(f"Database schema cached for {db_id[:8]}... - Title property: {title_prop}")
            return schema
            
        except Exception as e:
            logger.error(f"Failed to get database schema for {db_id}: {e}")
            return {"title_property": "Name", "properties": {}}  # fallback

    def find_page_by_property(self, db_id, prop_name, prop_value, max_pages=50):
        """Search for pages in database by property value"""
        try:
            # Use the correct databases.query method
            filter_obj = {
                "property": prop_name,
                "rich_text": {
                    "contains": prop_value
                }
            }
            
            response = self.client.databases.query(
                database_id=db_id,
                filter=filter_obj,
                page_size=min(max_pages, 100)
            )
            
            results = response.get("results", [])
            logger.debug(f"Found {len(results)} pages matching '{prop_value}' in property '{prop_name}'")
            return results
            
        except Exception as e:
            logger.error(f"Error querying Notion database {db_id}: {e}")
            return []

    def create_company(self, company_name, website=None, industry=None, country=None, description=None):
        """Create a new company page in the companies database"""
        try:
            # Get database schema to use correct property names
            schema = self.get_database_schema(settings.DB_COMPANIES)
            title_prop = schema.get("title_property", "Name")
            
            # Build properties object
            properties = {
                title_prop: {
                    "title": [
                        {
                            "text": {
                                "content": company_name
                            }
                        }
                    ]
                }
            }
            
            # Add optional properties if they exist in the database
            db_properties = schema.get("properties", {})
            
            if website and "Website" in db_properties:
                properties["Website"] = {"url": website}
            
            if industry and "Industry" in db_properties:
                properties["Industry"] = {"select": {"name": industry}}
            
            if country and "Country" in db_properties:
                properties["Country"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": country
                            }
                        }
                    ]
                }
            
            if description and "Description" in db_properties:
                # Limit description to avoid API limits
                desc_text = description[:1900] if len(description) > 1900 else description
                properties["Description"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": desc_text
                            }
                        }
                    ]
                }
            
            # Create the page
            page = self.client.pages.create(
                parent={
                    "database_id": settings.DB_COMPANIES
                },
                properties=properties
            )
            
            logger.info(f"Created company: {company_name}")
            return page
            
        except Exception as e:
            logger.error(f"Failed to create company {company_name}: {e}")
            return None

    def create_offer(self, job):
        """Create a new job offer page in the offers database"""
        try:
            # Get database schema
            schema = self.get_database_schema(settings.DB_OFFERS)
            title_prop = schema.get("title_property", "Offer Title")
            
            properties = {
                title_prop: {
                    "title": [
                        {
                            "text": {
                                "content": job["title"]
                            }
                        }
                    ]
                }
            }
            
            # Add other properties based on what exists in the database
            db_properties = schema.get("properties", {})
            
            if job.get("url") and "Offer Link" in db_properties:
                properties["Offer Link"] = {"url": job["url"]}
            elif job.get("url") and "Link" in db_properties:
                properties["Link"] = {"url": job["url"]}
            elif job.get("url") and "URL" in db_properties:
                properties["URL"] = {"url": job["url"]}
                
            if job.get("description") and "Description" in db_properties:
                desc_text = job["description"][:1900] if len(job["description"]) > 1900 else job["description"]
                properties["Description"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": desc_text
                            }
                        }
                    ]
                }
            
            if "Status" in db_properties:
                properties["Status"] = {"select": {"name": "Open"}}
            
            if "Created On" in db_properties:
                properties["Created On"] = {
                    "date": {
                        "start": time.strftime("%Y-%m-%d")
                    }
                }
            
            if job.get("location") and "Location" in db_properties:
                properties["Location"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": job["location"]
                            }
                        }
                    ]
                }
            
            page = self.client.pages.create(
                parent={
                    "database_id": settings.DB_OFFERS
                },
                properties=properties
            )
            
            logger.info(f"Created offer: {job['title']} at {job['company']}")
            return page
            
        except Exception as e:
            logger.error(f"Failed to create offer {job['title']}: {e}")
            return None

    def ensure_company_and_offer(self, job):
        """High-level method to ensure company exists and create offer"""
        try:
            # Get company database schema to use correct property name
            schema = self.get_database_schema(settings.DB_COMPANIES)

            print("\n\n\n\n\n" ,schema ,"\n\n\n\n\n" );
            title_prop = schema.get("title_property", "Name")
            
            # Check if company exists
            company_results = self.find_page_by_property(
                settings.DB_COMPANIES, 
                title_prop, 
                job["company"]
            )
            
            company_page = None
            if company_results:
                company_page = company_results[0]
                logger.info(f"Company exists: {job['company']}")
            else:
                # Create company
                company_page = self.create_company(job["company"])
                if not company_page:
                    logger.error("Failed to create company, skipping offer creation")
                    return None
            
            # Check if offer already exists
            offer_schema = self.get_database_schema(settings.DB_OFFERS)
            
            # Try different possible property names for the link
            link_properties = ["Offer Link", "Link", "URL"]
            offer_exists = False
            
            for link_prop in link_properties:
                if link_prop in offer_schema.get("properties", {}):
                    existing_offers = self.find_page_by_property(
                        settings.DB_OFFERS, 
                        link_prop, 
                        job.get("url", "")
                    )
                    if existing_offers:
                        logger.info(f"Offer already exists: {job['url']}")
                        offer_exists = True
                        break
            
            if not offer_exists and job.get("url"):
                # Create the offer
                offer_page = self.create_offer(job)
                return offer_page
            
            return company_page
            
        except Exception as e:
            logger.exception(f"Failed to process job {job.get('title', 'Unknown')}: {e}")
            return None