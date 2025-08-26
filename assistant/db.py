import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from zoneinfo import ZoneInfo


# Timezone & config
TZ_INFO = os.getenv("TZ", "Europe/Istanbul")
tz = ZoneInfo(TZ_INFO)


def get_db_connection():
    """
    Create a new PostgreSQL connection using environment variables.
    """
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "customer_assistant"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin"),
        port=os.getenv("POSTGRES_PORT", 5432),
    )


def init_db():
    """
    Initialize the database schema.
    WARNING: Drops existing tables before creating new ones.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")

            cur.execute("""
                CREATE TABLE conversations (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    response TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    response_time FLOAT NOT NULL,
                    relevance TEXT NOT NULL,
                    relevance_explanation TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    eval_prompt_tokens INTEGER NOT NULL,
                    eval_completion_tokens INTEGER NOT NULL,
                    eval_total_tokens INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id TEXT REFERENCES conversations(id),
                    feedback INTEGER NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
        conn.commit()
    finally:
        conn.close()


def save_conversation(conversation_id, question, answer_data, timestamp=None):
    """
    Save a conversation entry into the database.
    """
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO conversations 
                (id, question, response, model_used, response_time, relevance, 
                 relevance_explanation, prompt_tokens, completion_tokens, total_tokens,
                 eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                conversation_id,
                question,
                answer_data["answer"],
                answer_data["model_used"],
                answer_data["response_time"],
                answer_data["relevance"],
                answer_data["relevance_explanation"],
                answer_data["prompt_tokens"],
                answer_data["completion_tokens"],
                answer_data["total_tokens"],
                answer_data["eval_prompt_tokens"],
                answer_data["eval_completion_tokens"],
                answer_data["eval_total_tokens"],
                timestamp
            ))
        conn.commit()
    finally:
        conn.close()


def save_feedback(conversation_id, feedback, timestamp=None):
    """
    Save feedback for a given conversation.
    """
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO feedback (conversation_id, feedback, timestamp) 
                VALUES (%s, %s, %s)
            """, (conversation_id, feedback, timestamp))
        conn.commit()
    finally:
        conn.close()


def get_recent_conversations(limit=5, relevance=None):
    """
    Retrieve recent conversations (optionally filtered by relevance).
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT c.*, f.feedback
                FROM conversations c
                LEFT JOIN feedback f ON c.id = f.conversation_id
            """
            if relevance:
                query += " WHERE c.relevance = %s"
                params = (relevance, limit)
            else:
                params = (limit,)
            query += " ORDER BY c.timestamp DESC LIMIT %s"

            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()


def get_feedback_stats():
    """
    Get feedback statistics (thumbs up vs thumbs down).
    """
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT 
                    SUM(CASE WHEN feedback > 0 THEN 1 ELSE 0 END) as thumbs_up,
                    SUM(CASE WHEN feedback < 0 THEN 1 ELSE 0 END) as thumbs_down
                FROM feedback
            """)
            return cur.fetchone()
    finally:
        conn.close()


def check_timezone():
    """
    Utility to print database vs Python timezone. 
    Only for debugging – not used in production.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW timezone;")
            print("Database timezone:", cur.fetchone()[0])

            cur.execute("SELECT current_timestamp;")
            db_time_utc = cur.fetchone()[0]
            print("Database current time (UTC):", db_time_utc)
            print("Database current time ({TZ_INFO}):", db_time_utc.astimezone(tz))
            print("Python current time:", datetime.now(tz))
    finally:
        conn.close()
