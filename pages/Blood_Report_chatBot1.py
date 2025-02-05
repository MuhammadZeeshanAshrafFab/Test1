import streamlit as st
from database.db import get_medical_data_by_id, save_chat
from models.llm import generate_chat_response
from prompts.prompt1 import BLOOD_REPORT_PROMPT
from utils.logger import setup_logger

logger = setup_logger('blood_chatbot')

st.title("🩸 Blood Report Analysis Chatbot")

if 'processed_name' not in st.session_state or 'current_id' not in st.session_state:
    logger.warning("No processed name or ID found in session state")
    st.warning("Please process reports first")
    st.stop()

current_id = st.session_state.current_id
name = st.session_state.processed_name
logger.info(f"Loading blood reports for user ID: {current_id}")

# Get blood reports
total_reports, _ = get_medical_data_by_id(current_id) or ([], None)

# Filter for blood-related reports
blood_reports = [r for r in total_reports if r[2] == "blood"]
logger.info(f"Found {len(blood_reports)} blood reports")

# Display reports
with st.expander("🔍 View Extracted Blood Data"):
    if blood_reports:
        for report in blood_reports:
            st.write(f"**{report[2].upper()} Report ({report[5]})**")
            st.write(report[4])
            st.divider()
    else:
        logger.warning("No blood reports found")
        st.write("No blood reports found")

# Chat interface
user_input = st.chat_input("Ask about blood analysis...")

if user_input:
    logger.info(f"Processing user input: {user_input[:100]}...")
    context = "\n".join([f"Report {idx+1}:\n{report[4]}" for idx, report in enumerate(blood_reports)])
    
    messages = [{
        "role": "system",
        "content": f"{BLOOD_REPORT_PROMPT}\n\nContext:\n{context}"
    }, {
        "role": "user",
        "content": user_input
    }]
    
    with st.spinner("🔬 Analyzing Blood Report..."):
        response = generate_chat_response(messages, chat_type="blood")
        if response:
            chat_id = save_chat(name, "blood", user_input, response)
            logger.info(f"Saved chat response with ID: {chat_id}")
            st.write(f"**Analysis:** {response}")
