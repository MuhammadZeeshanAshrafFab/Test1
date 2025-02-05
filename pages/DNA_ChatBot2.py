import streamlit as st
from database.db import get_medical_data_by_id, save_chat
from models.llm import generate_chat_response
from prompts.prompt4 import DNA_ANALYSIS_PROMPT
from utils.logger import setup_logger

logger = setup_logger('dna_chatbot')

st.title("🧬 DNA Analysis Chatbot")

if 'processed_name' not in st.session_state or 'current_id' not in st.session_state:
    logger.warning("No processed name or ID found in session state")
    st.warning("Please process reports first")
    st.stop()

current_id = st.session_state.current_id
name = st.session_state.processed_name
logger.info(f"Loading DNA reports for user ID: {current_id}")

# Get DNA and image reports
dna_reports, _ = get_medical_data_by_id(current_id, data_type="dna") or ([], None)
all_reports, _ = get_medical_data_by_id(current_id) or ([], None)

# Filter image reports that contain DNA data
image_reports = []
if all_reports:
    image_reports = [r for r in all_reports 
                    if r[2] == "image" and 
                    any(kw in (r[4] or "").lower() for kw in ["dna", "genetic", "paternity"])]

all_dna_reports = dna_reports + image_reports
logger.info(f"Found {len(all_dna_reports)} DNA reports")

# Display reports
with st.expander("🔍 View Extracted DNA Data"):
    if all_dna_reports:
        for report in all_dna_reports:
            st.write(f"**{report[2].upper()} Report ({report[5]})**")
            st.write(report[4])
            st.divider()
    else:
        logger.warning("No DNA reports found")
        st.write("No DNA reports found")

# Chat interface
user_input = st.chat_input("Ask about DNA analysis...")

if user_input:
    logger.info(f"Processing user input: {user_input[:100]}...")
    context = "\n".join([f"Report {idx+1}:\n{report[4]}" 
                       for idx, report in enumerate(all_dna_reports)])
    
    messages = [{
        "role": "system",
        "content": f"{DNA_ANALYSIS_PROMPT}\n\nContext:\n{context}"
    }, {
        "role": "user",
        "content": user_input
    }]
    
    with st.spinner("🔬 Analyzing DNA..."):
        response = generate_chat_response(messages, chat_type="dna")
        if response:
            chat_id = save_chat(name, "dna", user_input, response)
            logger.info(f"Saved chat response with ID: {chat_id}")
            st.write(f"**Analysis:** {response}")