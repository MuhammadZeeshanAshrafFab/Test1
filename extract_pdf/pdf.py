import pdfplumber
import streamlit as st
from utils.logger import setup_logger


logger = setup_logger('pdf_extractor')

def encode_pdf(file):
    logger.info(f"Starting PDF extraction for file: {file.name}")
    try:
        text = ""
        with pdfplumber.open(file) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                logger.debug(f"Processing page {page_num}")
                text += page.extract_text()
        logger.info(f"Successfully extracted text from PDF: {file.name}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file.name}: {str(e)}", exc_info=True)
        st.error(f"Error extracting text from PDF: {e}")
        return None