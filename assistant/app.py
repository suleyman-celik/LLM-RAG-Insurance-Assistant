import os
import uuid
import logging

from flask import Flask, request, jsonify

import db   # your DB layer (Postgres)
from rag import rag   # your Retrieval-Augmented Generation pipeline

# ---------------- Logging ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------- Flask App ----------------
app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the Insurance RAG Assistant API 🚀",
        "status": "ok"
    }), 200


# ---------------- Question Endpoint ----------------
@app.route("/question", methods=["POST"])
def handle_question():
    """
    Main entrypoint: takes a user insurance question, passes it to RAG pipeline,
    stores conversation in DB, and returns the answer.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        logger.info(f"Incoming question request: {data}")

        question = data.get("question")
        if not question:
            return jsonify({"error": "Question must be a non-empty string"}), 400

        conversation_id = str(uuid.uuid4())

        # Call RAG pipeline
        try:
            answer_data = rag(question)
            if not isinstance(answer_data, dict) or "answer" not in answer_data:
                logger.error(f"Invalid rag() response: {answer_data}")
                return jsonify({"error": "Invalid response from RAG"}), 502
        except Exception:
            logger.exception("Error calling rag()")
            return jsonify({"error": "RAG pipeline not available"}), 503

        result = {
            "conversation_id": conversation_id,
            "question": question,
            "answer": answer_data["answer"],
            "context_docs": answer_data.get("context", []),   # optional: retrieved docs
            "model_used": answer_data.get("model_used", "unknown"),
        }

        # Save conversation to DB
        try:
            db.save_conversation(
                conversation_id=conversation_id,
                question=question,
                answer_data=answer_data,
            )
        except Exception:
            logger.exception("Error saving conversation to DB")
            return jsonify({"error": "Database error"}), 500

        return jsonify(result), 200

    except Exception as e:
        logger.exception("Unexpected error in /question")
        return jsonify({"error": str(e)}), 500


# ---------------- Feedback Endpoint ----------------
@app.route("/feedback", methods=["POST"])
def handle_feedback():
    """
    Collects user feedback (1 = good, -1 = bad) on insurance answers.
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        logger.info(f"Incoming feedback: {data}")

        conversation_id = data.get("conversation_id")
        feedback_raw = data.get("feedback")

        try:
            feedback = int(feedback_raw)
        except (ValueError, TypeError):
            return jsonify({"error": "Feedback must be an integer (1 or -1)."}), 400

        if not conversation_id or feedback not in [1, -1]:
            return jsonify({"error": "Invalid input"}), 400

        db.save_feedback(
            conversation_id=conversation_id,
            feedback=feedback,
        )

        return jsonify({
            "message": f"✅ Feedback received for conversation {conversation_id}: {feedback}"
        }), 200

    except Exception:
        logger.exception("Error saving feedback to DB")
        return jsonify({"error": "Database error"}), 500


# ---------------- Health Check ----------------
@app.route("/health")
def health():
    """
    Healthcheck for API, database, and LLM.
    Useful for Docker Compose and monitoring tools (Grafana/Prometheus).
    """
    status = {"flask": "ok"}

    # Check PostgreSQL
    try:
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        status["postgres"] = "ok"
    except Exception as e:
        status["postgres"] = f"error: {str(e)}"

    # Check Ollama LLM
    try:
        import requests
        ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434/v1/")
        model_name = os.getenv("LLM_MODEL", "phi3")
        payload = {"model": model_name, "messages": [{"role": "user", "content": "ping"}]}
        headers = {"Content-Type": "application/json"}

        r = requests.post(f"{ollama_url}chat/completions", json=payload, headers=headers)
        if r.status_code == 200:
            status["ollama"] = "ok"
        else:
            status["ollama"] = f"error: {r.status_code}"
    except Exception as e:
        status["ollama"] = f"error: {str(e)}"

    http_status = 200 if all(v == "ok" for v in status.values()) else 503
    return jsonify(status), http_status


if __name__ == "__main__":
    print("🚀 Insurance RAG Assistant API starting...")
    app.run(host="0.0.0.0", port=9000, debug=True)
