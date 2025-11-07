import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    DB_COMPANIES = os.getenv("DB_COMPANIES_ID")
    DB_OFFERS = os.getenv("DB_OFFERS_ID")
    DB_APPLICATIONS = os.getenv("DB_APPLICATIONS_ID")
    DB_CONTACTS = os.getenv("DB_CONTACTS_ID")
    DB_DOCUMENTS = os.getenv("DB_DOCUMENTS_ID")
    DB_OFFERS_RECEIVED = os.getenv("DB_OFFERS_RECEIVED_ID")

    SEARCH_TERMS = os.getenv("SEARCH_TERMS", "internship").split(",")
    LOCATIONS = os.getenv("LOCATIONS", "Morocco").split(",")
    RESULTS_WANTED = int(os.getenv("RESULTS_WANTED", "50"))
    DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()