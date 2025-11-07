from .logger_setup import get_logger
logger = get_logger("dedupe")

def dedupe_by_url(jobs):
    seen = set()
    out = []
    for j in jobs:
        url = j.get("url") or j.get("raw", {}).get("id") or None
        if not url:
            out.append(j)
            continue
        if url in seen:
            logger.debug("Skipping duplicate: %s", url)
            continue
        seen.add(url)
        out.append(j)
    return out