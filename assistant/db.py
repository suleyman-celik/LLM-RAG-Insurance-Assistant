import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "customer_assistant"),
        user=os.getenv("POSTGRES_USER", "your_username"),
        password=os.getenv("POSTGRES_PASSWORD", "your_password"),
        port=os.getenv("POSTGRES_PORT", 5432),
        cursor_factory=RealDictCursor
    )
    return conn
