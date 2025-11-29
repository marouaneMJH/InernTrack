# check_notion_env.py
# Health check pour Notion + configuration scraper

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()  # charge le fichier .env s'il existe


def log_status(ok: bool, label: str, detail: str | None = None) -> None:
    status = "[OK]" if ok else "[FAIL]"
    if detail:
        print(f"{status} {label} - {detail}")
    else:
        print(f"{status} {label}")


def require_env(name: str) -> bool:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        log_status(False, f"ENV {name}", "missing or empty")
        return False
    log_status(True, f"ENV {name}")
    return True


def notion_request(method: str, path: str) -> requests.Response:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN not set")

    base_url = "https://api.notion.com"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }

    response = requests.request(method=method, url=base_url + path, headers=headers)
    return response


def check_env_presence() -> bool:
    print("=== Checking ENV presence ===")
    ok = True

    ok = require_env("NOTION_TOKEN") and ok

    ok = require_env("DB_COMPANIES_ID") and ok
    ok = require_env("DB_OFFERS_ID") and ok
    ok = require_env("DB_APPLICATIONS_ID") and ok
    ok = require_env("DB_CONTACTS_ID") and ok
    ok = require_env("DB_DOCUMENTS_ID") and ok
    ok = require_env("DB_OFFERS_RECEIVED_ID") and ok

    ok = require_env("SEARCH_TERMS") and ok
    ok = require_env("LOCATIONS") and ok
    ok = require_env("RESULTS_WANTED") and ok
    ok = require_env("DRY_RUN") and ok
    ok = require_env("LOG_LEVEL") and ok

    print()
    return ok


def check_notion_token() -> bool:
    print("=== Checking Notion token ===")
    try:
        res = notion_request("GET", "/v1/users/me")
    except Exception as e:
        log_status(False, "Notion token", f"Error: {e}")
        print()
        return False

    if res.status_code == 200:
        data = res.json()
        user_name = data.get("name") or data.get("id") or "unknown user"
        log_status(True, "Notion token", f"user: {user_name}")
        print()
        return True

    if res.status_code == 401:
        log_status(False, "Notion token", "401 Unauthorized (invalid token)")
    elif res.status_code == 403:
        log_status(False, "Notion token", "403 Forbidden (no access to workspace)")
    else:
        log_status(False, "Notion token", f"HTTP {res.status_code} - {res.text}")
    print()
    return False


def check_database(db_id: str, label: str) -> bool:
    try:
        res = notion_request("GET", f"/v1/databases/{db_id}")
    except Exception as e:
        log_status(False, label, f"id={db_id}, Error: {e}")
        return False

    if res.status_code == 200:
        data = res.json()
        title_arr = data.get("title", [])
        if title_arr and isinstance(title_arr, list):
            title = title_arr[0].get("plain_text", "(no title)")
        else:
            title = "(no title)"
        log_status(True, label, f"id={db_id}, title=\"{title}\"")
        return True

    if res.status_code == 404:
        log_status(False, label, f"id={db_id}, 404 Not Found (wrong ID or not a DB)")
    elif res.status_code == 401:
        log_status(False, label, f"id={db_id}, 401 Unauthorized (token issue)")
    elif res.status_code == 403:
        log_status(False, label, f"id={db_id}, 403 Forbidden (no access to this DB)")
    else:
        log_status(False, label, f"id={db_id}, HTTP {res.status_code} - {res.text}")
    return False


def check_databases() -> bool:
    print("=== Checking Notion databases ===")
    ok = True

    db_companies = os.getenv("DB_COMPANIES_ID", "")
    db_offers = os.getenv("DB_OFFERS_ID", "")
    db_applications = os.getenv("DB_APPLICATIONS_ID", "")
    db_contacts = os.getenv("DB_CONTACTS_ID", "")
    db_documents = os.getenv("DB_DOCUMENTS_ID", "")
    db_offers_received = os.getenv("DB_OFFERS_RECEIVED_ID", "")

    ok = check_database(db_companies, "DB_COMPANIES_ID") and ok
    ok = check_database(db_offers, "DB_OFFERS_ID") and ok
    ok = check_database(db_applications, "DB_APPLICATIONS_ID") and ok
    ok = check_database(db_contacts, "DB_CONTACTS_ID") and ok
    ok = check_database(db_documents, "DB_DOCUMENTS_ID") and ok
    ok = check_database(db_offers_received, "DB_OFFERS_RECEIVED_ID") and ok

    print()
    return ok


def check_behaviour() -> bool:
    print("=== Checking scraper behaviour settings ===")
    ok = True

    results_raw = os.getenv("RESULTS_WANTED", "")
    dry_run_raw = os.getenv("DRY_RUN", "")
    log_level_raw = os.getenv("LOG_LEVEL", "")

    # RESULTS_WANTED
    try:
        n = int(results_raw)
        if n <= 0:
            raise ValueError("must be > 0")
        log_status(True, "RESULTS_WANTED", f"parsed value = {n}")
    except Exception:
        log_status(False, "RESULTS_WANTED", "must be a positive integer")
        ok = False

    # DRY_RUN
    dry = dry_run_raw.lower()
    if dry not in ("true", "false"):
        log_status(False, "DRY_RUN", 'must be "true" or "false"')
        ok = False
    else:
        log_status(True, "DRY_RUN", f"parsed value = {dry}")

    # LOG_LEVEL
    allowed_levels = ["DEBUG", "INFO", "WARN", "ERROR"]
    lvl = log_level_raw.upper()
    if lvl not in allowed_levels:
        log_status(False, "LOG_LEVEL", f"must be one of {', '.join(allowed_levels)}")
        ok = False
    else:
        log_status(True, "LOG_LEVEL", f"value = {lvl}")

    print()
    return ok


def main() -> None:
    global_ok = True

    env_ok = check_env_presence()
    global_ok = global_ok and env_ok

    if not env_ok:
        print("Some ENV vars are missing. Fix them before continuing.\n")

    token_ok = check_notion_token()
    global_ok = global_ok and token_ok

    if token_ok:
        db_ok = check_databases()
        global_ok = global_ok and db_ok
    else:
        print("Skipping DB checks because token is not valid.\n")

    behaviour_ok = check_behaviour()
    global_ok = global_ok and behaviour_ok

    print("=== SUMMARY ===")
    if global_ok:
        print("[OK] All checks passed. Configuration looks consistent.")
        sys.exit(0)
    else:
        print("[FAIL] Some checks failed. Review the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
