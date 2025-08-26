import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Metabase URL
METABASE_URL = os.getenv("METABASE_URL", "http://localhost:3000")

# Admin credentials (set in docker-compose env)
MB_USER = os.getenv("METABASE_ADMIN_USER")
MB_PASSWORD = os.getenv("METABASE_ADMIN_PASSWORD")

# Postgres connection info
PG_HOST = os.getenv("POSTGRES_HOST", "postgres")
PG_DB = os.getenv("POSTGRES_DB")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD")
PG_PORT = os.getenv("POSTGRES_PORT", 5432)


def get_session_token():
    payload = {"username": MB_USER, "password": MB_PASSWORD}
    response = requests.post(f"{METABASE_URL}/api/session", json=payload)

    if response.status_code == 200:
        print("✅ Metabase session created successfully")
        return response.json()["id"]
    else:
        print(f"❌ Failed to authenticate: {response.text}")
        return None


def create_or_update_database(session_token):
    headers = {"X-Metabase-Session": session_token}
    payload = {
        "name": "Postgres DB",
        "engine": "postgres",
        "details": {
            "host": PG_HOST,
            "port": PG_PORT,
            "dbname": PG_DB,
            "user": PG_USER,
            "password": PG_PASSWORD,
            "ssl": False,
        },
    }

    # Check if database exists
    response = requests.get(f"{METABASE_URL}/api/database", headers=headers)
    if response.status_code == 200:
        databases = response.json()
        for db in databases:
            if db["name"] == "Postgres DB":
                db_id = db["id"]
                print(f"🔄 Updating existing database (id={db_id})")
                response = requests.put(
                    f"{METABASE_URL}/api/database/{db_id}",
                    headers=headers,
                    json=payload,
                )
                return db_id

    # If not found, create new one
    print("➕ Creating new database in Metabase")
    response = requests.post(f"{METABASE_URL}/api/database", headers=headers, json=payload)

    if response.status_code in [200, 201]:
        db_id = response.json()["id"]
        print(f"✅ Database created with id={db_id}")
        return db_id
    else:
        print(f"❌ Failed to create/update database: {response.text}")
        return None


def create_dashboard(session_token, db_id):
    headers = {"X-Metabase-Session": session_token}

    dashboard_file = "dashboard.json"
    try:
        with open(dashboard_file, "r") as f:
            dashboard_json = json.load(f)
    except FileNotFoundError:
        print(f"❌ {dashboard_file} not found")
        return None

    # Minimal example: dashboard with title and empty cards
    payload = {
        "name": dashboard_json.get("title", "Customer Assistant Dashboard"),
        "description": dashboard_json.get("description", ""),
    }

    response = requests.post(f"{METABASE_URL}/api/dashboard", headers=headers, json=payload)

    if response.status_code in [200, 201]:
        dash_id = response.json()["id"]
        print(f"✅ Dashboard created with id={dash_id}")
        return dash_id
    else:
        print(f"❌ Failed to create dashboard: {response.text}")
        return None


def main():
    session_token = get_session_token()
    if not session_token:
        return

    db_id = create_or_update_database(session_token)
    if not db_id:
        return

    create_dashboard(session_token, db_id)


if __name__ == "__main__":
    main()
