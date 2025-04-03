import streamlit as st
import json
import sys
import importlib
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from analysis_engine import analyze_query  # Import your main function

# from analysis_engine import analyze_query  # Importing the model function directly

# Custom CSS Styling
st.markdown(
    """
    <style>
    body {
        background-color: #f5f7fa;
    }
    .chat-container {
        max-width: 800px;
        margin: auto;
        padding: 20px;
        border-radius: 10px;
        background: white;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    .message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .user {
        background: #007bff;
        color: white;
        text-align: right;
    }
    .bot {
        background: #e9ecef;
        color: black;
        text-align: left;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for storing past responses
if "responses" not in st.session_state:
    st.session_state.responses = []

# Title
st.title("MedBot-Testing")

# Model Selection
model_name = st.selectbox("Choose a model:", ["GEMINI", "MISTRAL", "LLAMA"])

# Ensure session history is initialized
if "history" not in st.session_state:
    st.session_state.history = []

# Caching function to optimize performance
@st.cache_data(ttl=300)  # Cache responses for 5 minutes
def get_response(query, model_name):
    """Fetches response directly from the model"""
    try:
        response = analyze_query(query, model_name)  # Calls the function directly
        return response if response else "No response received"
    except Exception as e:
        return f"Error: {str(e)}"

# User Input
user_query = st.text_area("Am I Alright?:", key="query")

if st.button("Generate Response"):
    if user_query.strip():
        response = get_response(user_query, model_name)
        
        # Store the conversation in session state
        st.session_state.history.append(("You", user_query))
        st.session_state.history.append(("Bot", response))
    else:
        st.warning("Am I Alright?")

# Chat History Display
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for sender, msg in st.session_state.history:
    role_class = "user" if sender == "You" else "bot"
    st.markdown(f'<div class="message {role_class}">{msg}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
