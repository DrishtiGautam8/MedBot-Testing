import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials


# Constants
QUERIES_PATH = "response_times_detailed_with_query_no.xlsx"
FEEDBACK_PATH = "feedback_queries.xlsx"
USER_LIMIT = 5
EMAIL_RECEIVER = "drishtig0001@gmail.com"

# Google Sheets setup
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "credentials.json"  # Replace with path to your credentials file

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)

# Google Sheets URLs
QUERIES_SHEET_URL = "https://docs.google.com/spreadsheets/d/1-gksEs15tssUz0hD38xgz1F-xOiMxzaI"
FEEDBACK_SHEET_URL = "https://docs.google.com/spreadsheets/d/1nfH5otANBbsgmUAvBGkJufJ9uh7hs56P"


# Load data
@st.cache_data
def load_data():
    queries_sheet = gc.open_by_url(QUERIES_SHEET_URL)
    feedback_sheet = gc.open_by_url(FEEDBACK_SHEET_URL)

    queries_worksheet = queries_sheet.get_worksheet(0)
    feedback_worksheet = feedback_sheet.get_worksheet(0)

    queries_df = pd.DataFrame(queries_worksheet.get_all_records())

    feedback_records = feedback_worksheet.get_all_records()
    if feedback_records:
        feedback_df = pd.DataFrame(feedback_records)
    else:
        feedback_df = pd.DataFrame(columns=[
            "query_no", "model", "instruction_following",
            "accuracy", "readability", "clarity_of_language",
            "selected_best_model"])

    return queries_df, feedback_df




# Get unrated grouped queries
def get_unrated_queries(queries_df, feedback_df):
    rated_query_nos = feedback_df['query_no'].unique()
    unrated_df = queries_df[~queries_df['query_no'].isin(rated_query_nos)]
    grouped = unrated_df.groupby('query').head(3).reset_index(drop=True)
    unique_queries = grouped['query'].unique()[:USER_LIMIT]
    display_df = grouped[grouped['query'].isin(unique_queries)]
    return display_df

# Save feedback
def update_feedback(new_feedback):
    feedback_sheet = gc.open_by_url(FEEDBACK_SHEET_URL)
    feedback_worksheet = feedback_sheet.get_worksheet(0)

    existing_data = pd.DataFrame(feedback_worksheet.get_all_records())
    combined_df = pd.concat([existing_data, new_feedback], ignore_index=True)
    combined_df.drop_duplicates(subset=["query_no", "model"], keep="last", inplace=True)

    feedback_worksheet.clear()
    feedback_worksheet.update([combined_df.columns.values.tolist()] + combined_df.values.tolist())
    return combined_df


# Send notification email
def send_email():
    sender_email = "your_email@example.com"
    sender_password = "your_password"
    subject = "All queries rated"

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = EMAIL_RECEIVER
    message['Subject'] = subject

    body = "All the queries have now been rated. Please check the feedback sheet."
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, EMAIL_RECEIVER, message.as_string())

# Streamlit UI
st.title("LLM Query Evaluation Tool")

st.markdown("""
### Welcome to the Query Evaluation Interface 👋
Please evaluate the given responses based on the following 5 rubrics:
1. **Instruction Following**
2. **Accuracy**
3. **Readability**
4. **Clarity of Language**
5. **Select the Best Model**

Click **Submit** once you're done or **Reset** to clear your choices. You will be asked to confirm your action.
""")

queries_df, feedback_df = load_data()

# Check if all queries are rated
if set(queries_df['query_no'].unique()).issubset(set(feedback_df['query_no'].unique())):
    st.success("""
    **Note:** All the queries have now been successfully rated,
    thank you so much for your interest.
    """)
    send_email()
    st.stop()

# Confirmation before reload
if st.session_state.get("confirm_reload", False):
    st.stop()
if st.button("Reload 5 New Queries"):
    if st.confirm("Are you sure you want to reload? Your changes will not be saved."):
        st.session_state.confirm_reload = True
        st.experimental_rerun()

display_df = get_unrated_queries(queries_df, feedback_df)

feedback_data = []
st.markdown("---")

for query in display_df['query'].unique():
    st.subheader(f"Query: {query}")
    query_block = display_df[display_df['query'] == query]
    local_feedback = {"query": query}
    for _, row in query_block.iterrows():
        with st.expander(f"Response by {row['model_used']}"):
            st.write(row['model_Response'])
            instr = st.radio(f"Instruction Following - {row['model_used']}", [1, 2, 3, 4, 5], key=f"instr_{row['query_no']}_{row['model_used']}")
            acc = st.radio(f"Accuracy - {row['model_used']}", [1, 2, 3, 4, 5], key=f"acc_{row['query_no']}_{row['model_used']}")
            read = st.radio(f"Readability - {row['model_used']}", [1, 2, 3, 4, 5], key=f"read_{row['query_no']}_{row['model_used']}")
            clarity = st.radio(f"Clarity of Language - {row['model_used']}", [1, 2, 3, 4, 5], key=f"clarity_{row['query_no']}_{row['model_used']}")
            local_feedback[row['model_used']] = {
                "query_no": row['query_no'],
                "model": row['model_used'],
                "instruction_following": instr,
                "accuracy": acc,
                "readability": read,
                "clarity_of_language": clarity
            }
    best_model = st.radio(f"Which model gave the best response for this query?", [row['model_used'] for _, row in query_block.iterrows()], key=f"best_model_{query}")
    for model in local_feedback:
        if model in ["query"]: continue
        feedback_entry = local_feedback[model]
        feedback_entry["selected_best_model"] = best_model
        feedback_data.append(feedback_entry)
    st.markdown("---")

# Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Submit"):
        if st.confirm("Are you sure you want to submit the feedback?"):
            new_df = pd.DataFrame(feedback_data)
            update_feedback(new_df)
            st.success("Feedback submitted successfully!")
            st.experimental_rerun()
with col2:
    if st.button("Reset"):
        if st.confirm("Are you sure you want to reset all feedback fields?"):
            st.experimental_rerun()
