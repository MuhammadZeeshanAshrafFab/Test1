import streamlit as st
from groq import Groq
from utils.logger import setup_logger

logger = setup_logger('settings')

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    logger.info("Successfully loaded GROQ API key")
except Exception as e:
    logger.error("Failed to load GROQ API key", exc_info=True)
    raise

client = Groq(api_key=GROQ_API_KEY)

VISION_MODEL = "llama-3.2-90b-vision-preview"
TEXT_MODEL = "llama3-70b-8192"
VISION_TEMPERATURE = 0.5
TEXT_TEMPERATURE = 0.2
MAX_TOKENS = 1024

logger.info(f"Settings initialized with models: Vision={VISION_MODEL}, Text={TEXT_MODEL}")