import os
import pandas as pd
import json
import minsearch


DATA_PATH = os.getenv("DATA_PATH", "../Data/documents-with-ids.json")


def load_index(data_path=DATA_PATH):
    
    with open(data_path, 'rt') as f_in:
        documents = json.load(f_in)

    index = minsearch.Index(
                            text_fields=['intent', 'question', 'response', 'category'],
                            keyword_fields=['id']
                            )

    index.fit(documents)
    return index

import pandas as pd
from db import get_db_connection

def ingest_csv(path="Data/data.csv"):
    df = pd.read_csv(path)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            question TEXT,
            response TEXT,
            model_used TEXT,
            response_time FLOAT,
            relevance TEXT,
            relevance_explanation TEXT,
            prompt_tokens INT,
            completion_tokens INT,
            total_tokens INT,
            eval_prompt_tokens INT,
            eval_completion_tokens INT,
            eval_total_tokens INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO conversations (
                id, question, response, model_used, response_time, relevance,
                relevance_explanation, prompt_tokens, completion_tokens, total_tokens,
                eval_prompt_tokens, eval_completion_tokens, eval_total_tokens
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (
            row.get("id"),
            row.get("question"),
            row.get("response"),
            row.get("model_used", "phi3"),
            row.get("response_time", 0.0),
            row.get("relevance"),
            row.get("relevance_explanation"),
            row.get("prompt_tokens", 0),
            row.get("completion_tokens", 0),
            row.get("total_tokens", 0),
            row.get("eval_prompt_tokens", 0),
            row.get("eval_completion_tokens", 0),
            row.get("eval_total_tokens", 0),
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ CSV verileri yüklendi!")

if __name__ == "__main__":
    ingest_csv()
