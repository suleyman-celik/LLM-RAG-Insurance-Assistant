# cli.py
import json
import uuid
import argparse
import requests
import questionary
import pandas as pd

# Function: pick a random question from the CSV (ground-truth data file)
def get_random_question(file_path):
    df = pd.read_csv(file_path)
    return df.sample(n=1).iloc[0]["question"]

# Function: send question to your backend API
def ask_question(url, question):
    data = {"question": question}
    response = requests.post(url, json=data)
    return response.json()

# Function: send feedback (+1 / -1) back to the API
def send_feedback(url, conversation_id, feedback):
    feedback_data = {"conversation_id": conversation_id, "feedback": feedback}
    response = requests.post(f"{url}/feedback", json=feedback_data)
    return response.status_code

def main():
    parser = argparse.ArgumentParser(description="Interactive CLI app for Q&A with feedback")
    parser.add_argument(
        "--random", action="store_true", help="Pick random questions from CSV"
    )
    args = parser.parse_args()

    # URL of your app container (port matches APP_PORT in .env/docker-compose.yml)
    base_url = "http://localhost:9000"
    csv_file = "./Data/ground-truth-data.csv"

    print("Welcome to CLI Q&A! Type questions or use --random mode.\n")

    while True:
        if args.random:
            question = get_random_question(csv_file)
            print(f"\nRandom question: {question}")
        else:
            question = questionary.text("Enter your question:").ask()

        # Call backend
        response = ask_question(f"{base_url}/question", question)
        print("\nAnswer:", response.get("answer", "No answer provided"))

        # Extract conversation_id (or generate if missing)
        conversation_id = response.get("conversation_id", str(uuid.uuid4()))

        # Ask user for feedback
        feedback = questionary.select(
            "How would you rate this response?",
            choices=["+1 (Positive)", "-1 (Negative)", "Pass (Skip feedback)"],
        ).ask()

        if feedback != "Pass (Skip feedback)":
            feedback_value = 1 if feedback == "+1 (Positive)" else -1
            status = send_feedback(base_url, conversation_id, feedback_value)
            print(f"✅ Feedback sent. Status code: {status}")
        else:
            print("⚠️ Feedback skipped.")

        # Continue or exit
        if not questionary.confirm("Do you want to continue?").ask():
            print("Bye 👋")
            break

if __name__ == "__main__":
    main()
