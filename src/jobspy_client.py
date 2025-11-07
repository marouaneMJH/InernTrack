from jobspy import scrape_jobs   # si le package diffère, adapte l'import
from .logger_setup import get_logger
from .config import settings

logger = get_logger("jobspy_client", settings.LOG_LEVEL)

def fetch_jobs():
    """Retourne une liste d'objets job bruts depuis JobSpy."""
    queries = []
    for term in settings.SEARCH_TERMS:
        for loc in settings.LOCATIONS:
            queries.append((term.strip(), loc.strip()))
    all_jobs = []
    for term, loc in queries:
        logger.info(f"Scraping '{term}' in '{loc}' ...")
        try:
            jobs = scrape_jobs(
                site_name=["indeed","linkedin","glassdoor"],  # adapte selon disponibilité
                search_term=term,
                location=loc,
                results_wanted=settings.RESULTS_WANTED,
                job_type="internship"
            )
            logger.info(f"Fetched {len(jobs)} results for ({term}, {loc})")
            all_jobs.extend(jobs.to_dict('records') if hasattr(jobs, 'to_dict') else jobs)
        except Exception as e:
            logger.exception("Erreur lors du scraping JobSpy: %s", e)
    # optional: unique by url or id
    return all_jobs