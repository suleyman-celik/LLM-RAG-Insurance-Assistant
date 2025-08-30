# streamlit.py
import streamlit as st
import requests
import uuid

# Page setup
st.set_page_config(page_title="Customer Assistant", page_icon="🤖", layout="wide")
st.title("Customer Assistant Q&A")

# API URL (match with app service port in docker-compose)
base_url = "http://localhost:9000"

# Keep session state variables
if "question" not in st.session_state:
    st.session_state.question = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

# Function: call /question endpoint
def ask_question(url, question):
    data = {"question": question}
    response = requests.post(f"{url}/question", json=data)
    return response.json()

# Function: call /feedback endpoint
def send_feedback(url, conversation_id, feedback):
    feedback_data = {"conversation_id": conversation_id, "feedback": feedback}
    response = requests.post(f"{url}/feedback", json=feedback_data)
    return response.status_code

# Input text
st.session_state.question = st.text_input("Ask your question:", value=st.session_state.question)

# Ask button
if st.button("Get Answer"):
    if st.session_state.question:
        with st.spinner("Thinking... 🤔"):
            response = ask_question(base_url, st.session_state.question)

        st.session_state.answer = response.get("answer", "No answer provided")
        st.session_state.conversation_id = response.get("conversation_id", str(uuid.uuid4()))

# Display answer
if st.session_state.answer:
    st.subheader("Answer")
    st.write(st.session_state.answer)

    # Feedback buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👍 Positive"):
            status = send_feedback(base_url, st.session_state.conversation_id, 1)
            st.success(f"Positive feedback sent (status {status})")
    with col2:
        if st.button("👎 Negative"):
            status = send_feedback(base_url, st.session_state.conversation_id, -1)
            st.error(f"Negative feedback sent (status {status})")
    with col3:
        if st.button("⏭️ Skip feedback"):
            st.info("Feedback skipped.")
else:
    st.info("Enter a question and press 'Get Answer'.")
