import psycopg2
from datetime import datetime


def get_connection():
    """
    PostgreSQL'e bağlanir.
    Bağlanti bilgilerini kendi veritabanina göre güncelleyebilirsin.
    """
    return psycopg2.connect(
        host="localhost",
        database="customer_support",
        user="admin",
        password="admin",
    )


def insert_conversation(
    conn,
    id: str,
    question: str,
    response: str,
    model_used: str,
    response_time: float,
    relevance: str,
    relevance_explanation: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int = None,
    eval_prompt_tokens: int = 0,
    eval_completion_tokens: int = 0,
    eval_total_tokens: int = None,
    timestamp: datetime = None,
):
    """
    Tek bir kaydı conversations tablosuna ekler.
    """
    if total_tokens is None:
        total_tokens = prompt_tokens + completion_tokens
    if eval_total_tokens is None:
        eval_total_tokens = eval_prompt_tokens + eval_completion_tokens
    if timestamp is None:
        timestamp = datetime.now()

    insert_sql = """
        INSERT INTO conversations 
        (id, question, response, model_used, response_time, relevance, 
         relevance_explanation, prompt_tokens, completion_tokens, total_tokens,
         eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    with conn.cursor() as cur:
        cur.execute(
            insert_sql,
            (
                id,
                question,
                response,
                model_used,
                response_time,
                relevance,
                relevance_explanation,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                eval_prompt_tokens,
                eval_completion_tokens,
                eval_total_tokens,
                timestamp,
            ),
        )
    conn.commit()


def add_sample_data():
    """
    Örnek veri ekler (senin paylaştigin 'da0592e6' kaydina göre).
    """
    try:
        conn = get_connection()
        print("Database connection successful!")

        insert_conversation(
            conn,
            id="da0592e6",
            question="i got to receive fucking compensations can i get some ehlp",
            response=(
                "To process your compensation payment for the insurance claim, please adhere to the following steps:\n\n"
                "1. Access your account by visiting {{WEBSITE_URL}}.\n"
                "2. Locate the {{CLAIM_SECTION}} for your specific claim.\n"
                "3. Identify the claim that you wish to be compensated for.\n"
                "4. Opt for the {{RECEIVE_PAYMENT_OPTION}} that best suits your preference.\n"
                "5. Follow the provided instructions to finalize your preferred method of payment and validate the information.\n\n"
                "Should you face any complications during this process, do not hesitate to reach out to our customer support team for immediate assistance."
            ),
            model_used="phi3",
            response_time=0.73,
            relevance="RELEVANT",
            relevance_explanation="Answer directly describes the steps to receive claim payment.",
            prompt_tokens=120,
            completion_tokens=130,
            eval_prompt_tokens=70,
            eval_completion_tokens=45,
        )
        print("Sample data added to conversations table.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    add_sample_data()
