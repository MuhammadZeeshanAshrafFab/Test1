import base64
from io import BytesIO
import streamlit as st
from PIL import Image, ImageEnhance
from utils.logger import setup_logger


logger = setup_logger('image_processor')

def preprocess_image(file):
    logger.info(f"Starting image preprocessing for file: {file.name}")
    try:
        image = Image.open(file)
        logger.debug(f"Original image size: {image.size}")
        
        image = image.convert("L")
        logger.debug("Converted image to grayscale")
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        logger.debug("Enhanced image contrast")
        
        image = image.resize((1024, 1024))
        logger.debug("Resized image to 1024x1024")
        
        logger.info(f"Successfully preprocessed image: {file.name}")
        return image
    except Exception as e:
        logger.error(f"Error preprocessing image {file.name}: {str(e)}", exc_info=True)
        st.error(f"Error preprocessing image: {e}")
        return None

def encode_image(image):
    logger.info("Starting image encoding")
    try:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        buffered.seek(0)
        encoded = base64.b64encode(buffered.read()).decode("utf-8")
        logger.info("Successfully encoded image")
        return encoded
    except Exception as e:
        logger.error(f"Error encoding image: {str(e)}", exc_info=True)
        st.error(f"Error encoding image: {e}")
        return None