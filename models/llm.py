import streamlit as st
from models import settings
from prompts.prompt1 import BLOOD_REPORT_PROMPT
from prompts.prompt2 import DNA_ANALYSIS_PROMPT
from utils.logger import setup_logger


logger = setup_logger('llm_model')

def analyze_medical_data(messages, is_vision=True, data_type="blood"):
    logger.info(f"Starting medical data analysis - Vision: {is_vision}, Type: {data_type}")
    try:
        model = settings.VISION_MODEL if is_vision else settings.TEXT_MODEL
        temperature = settings.VISION_TEMPERATURE if is_vision else settings.TEXT_TEMPERATURE
        
        logger.debug(f"Using model: {model} with temperature: {temperature}")
        
        # Add appropriate prompt based on data type
        system_prompt = BLOOD_REPORT_PROMPT if data_type == "blood" else DNA_ANALYSIS_PROMPT
        
        # Insert system prompt at the beginning of messages
        if isinstance(messages[0]["content"], list):
            # For vision analysis, add prompt to text content
            messages[0]["content"][0]["text"] = f"{system_prompt}\n\n{messages[0]['content'][0]['text']}"
        else:
            # For text analysis, insert system message at start
            messages.insert(0, {
                "role": "system",
                "content": system_prompt
            })
        
        logger.debug("Making API call to model")
        response = settings.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=settings.MAX_TOKENS
        )
        
        logger.info("Successfully received model response")
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        st.error(f"Analysis error: {str(e)}")
        return None

def generate_chat_response(messages, chat_type="blood"):
    logger.info(f"Generating chat response for type: {chat_type}")
    try:
        # Add appropriate prompt based on chat type
        system_prompt = BLOOD_REPORT_PROMPT if chat_type == "blood" else DNA_ANALYSIS_PROMPT
        
        # Update system message with appropriate prompt
        if messages[0]["role"] == "system":
            messages[0]["content"] = f"{system_prompt}\n\n{messages[0]['content']}"
        else:
            messages.insert(0, {
                "role": "system",
                "content": system_prompt
            })
        
        logger.debug("Making API call for chat response")
        response = settings.client.chat.completions.create(
            messages=messages,
            model=settings.TEXT_MODEL,
            temperature=settings.TEXT_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        
        logger.info("Successfully received chat response")
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        st.error(f"Chat error: {str(e)}")
        return None