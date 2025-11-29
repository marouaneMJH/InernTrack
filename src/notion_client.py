from notion_client import Client
from .config import settings
from .logger_setup import get_logger
import time

logger = get_logger("notion_client", settings.LOG_LEVEL)

class NotionSync:
    def __init__(self, token):
        self.client = Client(auth=token)

    # utility
    def find_page_by_property(self, db_id, prop_name, prop_value, max_pages=50):
        """Find pages in a database by property value."""
        try:
            if prop_name.lower() == "offer link" or "url" in prop_name.lower():
                filter_config = {
                    "property": prop_name,
                    "url": {"equals": prop_value}
                }
            else:
                filter_config = {
                    "property": prop_name,
                    "rich_text": {"contains": prop_value}
                }
            # Use the request method directly
            query_body = {
                "filter": filter_config,
                "page_size": min(max_pages, 100)
            }
            res = self.client.request(
                path=f"databases/{db_id}/query",
                method="POST",
                body=query_body
            )
            return res.get("results", [])
        except Exception as e:
            logger.exception("Erreur query Notion: %s", e)
            return []

    def create_company(self, company_name, website=None, industry=None, country=None, description=None):
        """Create a new company page in the companies database."""
        props = {
            "Name": {"title":[{"text": {"content": company_name}}]},
        }
        if website:
            props["Website"] = {"url": website}
        if industry:
            props["Industry"] = {"select": {"name": industry}}
        if country:
            props["Country"] = {"rich_text":[{"text":{"content":country}}]}
        if description:
            props["Description"] = {"rich_text":[{"text":{"content":description[:2000]}}]}

        try:
            page_data = {
                "parent": {"database_id": settings.DB_COMPANIES},
                "properties": props
            }
            page = self.client.request(
                path="pages",
                method="POST", 
                body=page_data
            )
            logger.info("Created company: %s", company_name)
            return page
        except Exception as e:
            logger.exception("Failed to create company %s: %s", company_name, e)
            return None

    def create_offer(self, job):
        """Create a new job offer page in the offers database."""
        props = {
            "Offer Title": {"title":[{"text":{"content": job["title"]}}]},
            "Status": {"select": {"name": "Open"}},
            "Created On": {"date": {"start": time.strftime("%Y-%m-%d")}},
            "Location": {"rich_text":[{"text":{"content": job["location"] or ""}}]}
        }
        
        # Add URL if available
        if job.get("url"):
            props["Offer Link"] = {"url": job["url"]}
        
        # Add description (truncate to avoid Notion limits)
        if job.get("description"):
            description_text = job["description"][:1900]
            props["Description"] = {"rich_text":[{"text":{"content": description_text}}]}

        try:
            page_data = {
                "parent": {"database_id": settings.DB_OFFERS},
                "properties": props
            }
            page = self.client.request(
                path="pages",
                method="POST",
                body=page_data
            )
            logger.info("Created offer: %s at %s", job["title"], job["company"])
            return page
        except Exception as e:
            logger.exception("Failed to create offer %s: %s", job["title"], e)
            return None

    # helper high-level flows
    def ensure_company_and_offer(self, job):
        """Ensure both company and offer exist in Notion databases."""
        # Check company existence by name
        results = self.find_page_by_property(settings.DB_COMPANIES, "Name", job["company"])
        if results:
            company_page = results[0]
            logger.info("Company exists: %s", job["company"])
        else:
            company_page = self.create_company(job["company"])
            if not company_page:
                logger.error("Failed to create company, skipping offer creation")
                return None
        
        # Check if offer already exists by URL
        if job.get("url"):
            offer_exists = self.find_page_by_property(settings.DB_OFFERS, "Offer Link", job["url"])
            if offer_exists:
                logger.info("Offer already exists: %s", job["url"])
                return offer_exists[0]
        
        # Create new offer
        return self.create_offer(job)