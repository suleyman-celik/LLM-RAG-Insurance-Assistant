# import os
# import json
# import openai
# import pandas as pd
# from sqlalchemy import create_engine, text
# from sqlalchemy.exc import SQLAlchemyError
# from typing import List, Dict, Any
# from openai import OpenAI
from flask import Flask, request, jsonify
from rag import rag

app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    """
    Endpoint: POST /ask
    Body: {"question": "Your question here"}
    """
    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        answer_data = rag(question)
        return jsonify({"question": question, **answer_data})
    except Exception as e:
        # Hata mesajını loglayabilirsin, burada sadece geri dönüyoruz
        return jsonify({"error": f"Failed to get answer: {str(e)}"}), 500

@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # Debug yalnızca local geliştirme için, production'da gunicorn kullanılacak
    app.run(host="0.0.0.0", port=5001, debug=True)

#################################################################
# Below is the mine app.py content for reference
#################################################################   
    # from flask import Flask, request, jsonify
    # from rag import rag_pipeline
    # from db import get_connection

    # app = Flask(__name__)

    # @app.route("/ask", methods=["POST"])
    # def ask():
    #     data = request.get_json()
    #     question = data.get("question", "")
    #     if not question:
    #         return jsonify({"error": "Question is required"}), 400

    #     answer = rag_pipeline(question)
    #     return jsonify({"question": question, "answer": answer})

    # @app.route("/conversations", methods=["GET"])
    # def get_conversations():
    #     conn = get_connection()
    #     cur = conn.cursor()
    #     cur.execute("SELECT * FROM conversations LIMIT 50;")
    #     rows = cur.fetchall()
    #     conn.close()
    #     return jsonify(rows)

    # if __name__ == "__main__":
    #     app.run(host="0.0.0.0", port=5000, debug=True)

