import os
import json
import time
import requests
import logging
from dotenv import load_dotenv
from requests.exceptions import RequestException

# ---------------- Load environment ----------------
load_dotenv()

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("grafana-setup")

# ---------------- Config ----------------
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_USER = os.getenv("GRAFANA_ADMIN_USER", "admin")
GRAFANA_PASSWORD = os.getenv("GRAFANA_ADMIN_PASSWORD", "admin")

PG_DB = os.getenv("POSTGRES_DB", "media_assistant")
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_USER = os.getenv("POSTGRES_USER", "admin")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")

# ---------------- Helpers ----------------
def wait_for_grafana(timeout=60):
    """Wait until Grafana API is reachable."""
    logger.info("⏳ Waiting for Grafana to be ready...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{GRAFANA_URL}/api/health", auth=(GRAFANA_USER, GRAFANA_PASSWORD))
            if r.status_code == 200:
                logger.info("✅ Grafana is up!")
                return True
        except RequestException:
            pass
        time.sleep(3)
    logger.error("❌ Grafana did not start within timeout.")
    return False


def create_api_key():
    """Create (or recreate) a Grafana API key."""
    auth = (GRAFANA_USER, GRAFANA_PASSWORD)
    payload = {"name": "ProgrammaticKey", "role": "Admin"}

    r = requests.post(f"{GRAFANA_URL}/api/auth/keys", json=payload, auth=auth)
    if r.status_code == 200:
        logger.info("🔑 API key created.")
        return r.json()["key"]

    if r.status_code == 409:
        logger.info("API key already exists, replacing...")
        keys = requests.get(f"{GRAFANA_URL}/api/auth/keys", auth=auth).json()
        for key in keys:
            if key["name"] == "ProgrammaticKey":
                requests.delete(f"{GRAFANA_URL}/api/auth/keys/{key['id']}", auth=auth)
        return create_api_key()

    logger.error("Failed to create API key: %s", r.text)
    return None


def create_or_update_datasource(api_key, name="Postgres-Insurance"):
    """Create or update a PostgreSQL datasource in Grafana."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "name": name,
        "type": "postgres",
        "url": f"{PG_HOST}:{PG_PORT}",
        "access": "proxy",
        "user": PG_USER,
        "database": PG_DB,
        "basicAuth": False,
        "isDefault": True,
        "jsonData": {"sslmode": "disable", "postgresVersion": 1300},
        "secureJsonData": {"password": PG_PASSWORD},
    }

    r = requests.get(f"{GRAFANA_URL}/api/datasources/name/{name}", headers=headers)
    if r.status_code == 200:
        ds_id = r.json()["id"]
        logger.info("🔄 Updating datasource '%s' (id=%s)", name, ds_id)
        r = requests.put(f"{GRAFANA_URL}/api/datasources/{ds_id}", json=payload, headers=headers)
    else:
        logger.info("➕ Creating new datasource '%s'", name)
        r = requests.post(f"{GRAFANA_URL}/api/datasources", json=payload, headers=headers)

    if r.status_code in [200, 201]:
        logger.info("✅ Datasource ready.")
        return r.json().get("datasource", {}).get("uid") or r.json().get("uid")

    logger.error("❌ Failed to create/update datasource: %s", r.text)
    return None


def update_datasource_in_panels(dashboard_json, uid):
    """Recursively update all panels/targets with datasource UID."""
    def _update(panel):
        if isinstance(panel.get("datasource"), dict):
            panel["datasource"]["uid"] = uid
        for target in panel.get("targets", []):
            if isinstance(target.get("datasource"), dict):
                target["datasource"]["uid"] = uid
        for nested in panel.get("panels", []):  # rows or nested panels
            _update(nested)

    for p in dashboard_json.get("panels", []):
        _update(p)
    return dashboard_json


def create_or_update_dashboard(api_key, datasource_uid, dashboard_file="dashboard.json"):
    """Create or overwrite a dashboard in Grafana."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        with open(dashboard_file, "r") as f:
            dashboard = json.load(f)
    except Exception as e:
        logger.error("❌ Failed to load dashboard file: %s", e)
        return None

    # Clean up dashboard fields for import
    for k in ["id", "uid", "version"]:
        dashboard.pop(k, None)

    dashboard = update_datasource_in_panels(dashboard, datasource_uid)

    payload = {"dashboard": dashboard, "overwrite": True, "message": "Auto-setup"}
    r = requests.post(f"{GRAFANA_URL}/api/dashboards/db", headers=headers, json=payload)

    if r.status_code == 200:
        logger.info("📊 Dashboard created/updated.")
        return r.json().get("uid")

    logger.error("❌ Failed to create dashboard: %s", r.text)
    return None


def main():
    if not wait_for_grafana():
        return

    api_key = create_api_key()
    if not api_key:
        return

    ds_uid = create_or_update_datasource(api_key)
    if not ds_uid:
        return

    create_or_update_dashboard(api_key, ds_uid)
    logger.info("🎉 Grafana setup complete.")


if __name__ == "__main__":
    main()
