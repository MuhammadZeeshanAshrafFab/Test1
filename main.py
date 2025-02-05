import streamlit as st
from database.db import (
    init_db,
    save_medical_data,
    get_medical_data_by_id
)
from models.llm import analyze_medical_data
from process_image.image import preprocess_image, encode_image
from extract_pdf.pdf import encode_pdf
from utils.logger import setup_logger


# Initialize logger
logger = setup_logger('main')

# Initialize database at start
init_db()

st.title("🩺 Medical Data Processor")

# Add ID input at the top
user_id = st.text_input("Enter Patient ID", key="user_id")
existing_data = None

if user_id:
    # Try to fetch existing data using ID
    try:
        user_id = int(user_id)
        data, patient_name = get_medical_data_by_id(user_id)
        if data and patient_name:
            logger.info(f"Found records for Patient ID: {user_id} (Name: {patient_name})")
            st.session_state.processed_name = patient_name
            st.session_state.current_id = user_id  # Store ID in session
            
            # Display existing patient information
            if 'personal_info' in st.session_state:
                st.success("Patient Information:")
                st.write(f"Name: {st.session_state.personal_info['name']}")
                st.write(f"Age: {st.session_state.personal_info['age']}")
                st.write(f"Weight: {st.session_state.personal_info['weight']} kg")
                st.write(f"Height: {st.session_state.personal_info['height']} cm")
                st.write(f"BMI: {st.session_state.personal_info['bmi']:.1f}")
            
            st.write("You can proceed directly to uploading new reports.")
        else:
            logger.info(f"No existing data found for ID: {user_id}")
            st.warning("No existing records found. Please fill in patient information.")
    except ValueError:
        st.error("Please enter a valid numeric ID")
        logger.warning("Invalid ID format entered")

# Show form only if no existing data found
if not existing_data:
    with st.form("upload_form"):
        # Patient Information Section
        logger.info("Rendering patient information form")
        st.subheader("Patient Information")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Patient Full Name", key="name_input")
            age = st.number_input("Patient Age", min_value=0, max_value=120, step=1)
            weight = st.number_input("Patient Weight (kg)", min_value=0.0, max_value=300.0, step=0.1)
        
        with col2:
            height = st.number_input("Patient Height (cm)", min_value=0.0, max_value=300.0, step=0.1)
            if weight > 0 and height > 0:
                bmi = weight / ((height/100) ** 2)
                st.info(f"Patient BMI: {bmi:.1f}")
        
        submitted_info = st.form_submit_button("Save Patient Information")
        
        if submitted_info:
            if not name or age == 0 or weight == 0 or height == 0:
                logger.warning("Incomplete form submission - missing required patient fields")
                st.error("Please fill in all patient information fields")
                st.stop()
            
            # Store patient info in session state
            st.session_state.processed_name = name
            st.session_state.personal_info = {
                "name": name,
                "age": age,
                "weight": weight,
                "height": height,
                "bmi": weight / ((height/100) ** 2)
            }
            logger.info("Patient information stored in session state")
            st.success("Patient information saved! You can now upload reports.")

# File upload section - shown to all users
if 'processed_name' in st.session_state:
    with st.form("file_upload_form"):
        st.subheader("Medical Reports")
        uploaded_files = st.file_uploader(
            "Upload Reports (JPG, PNG, PDF)", 
            type=["jpg", "png", "pdf"], 
            accept_multiple_files=True
        )
        submitted_files = st.form_submit_button("Analyze Reports")

        if submitted_files:
            if not uploaded_files:
                logger.warning("No files uploaded")
                st.error("Please upload at least one file")
                st.stop()
            
            with st.spinner("Extracting medical data..."):
                processed_ids = []  # Store all processed file IDs
                name = st.session_state.processed_name
                patient_info = st.session_state.personal_info
                
                # Create patient context string
                patient_context = (
                    f"Patient Information:\n"
                    f"Name: {patient_info['name']}\n"
                    f"Age: {patient_info['age']}\n"
                    f"Weight: {patient_info['weight']} kg\n"
                    f"Height: {patient_info['height']} cm\n"
                    f"BMI: {patient_info['bmi']:.1f}\n\n"
                    f"Please use this patient information for all analyses and ignore any "
                    f"conflicting demographic information in the reports."
                )
                
                for file in uploaded_files:
                    logger.info(f"Processing file: {file.name}")
                    try:
                        if file.type.startswith('image'):
                            img = preprocess_image(file)
                            if img:
                                base64_image = encode_image(img)
                                initial_analysis = analyze_medical_data(
                                    messages=[{
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": f"{patient_context}\nIs this a DNA/genetic report or a blood test report? Ignore any patient demographics in the report."},
                                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                        ]
                                    }],
                                    is_vision=True
                                )
                                
                                report_type = "blood" if any(kw in initial_analysis.lower() 
                                                         for kw in ["cbc", "hemogloboin", "platelet"]) else "dna"
                                logger.info(f"Detected report type: {report_type}")
                                
                                analysis = analyze_medical_data(
                                    messages=[{
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": f"{patient_context}\nAnalyze this medical report in detail"},
                                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                        ]
                                    }],
                                    is_vision=True,
                                    data_type=report_type
                                )
                                
                                file_id = save_medical_data(name, report_type, f"image_{file.name}", analysis)
                                processed_ids.append((file.name, file_id, report_type))
                                
                        elif file.type == "application/pdf":
                            text = encode_pdf(file)
                            if text:
                                report_type = "blood" if any(kw in text.lower() 
                                                         for kw in ["cbc", "hemoglobin", "platelet"]) else "dna"
                                logger.info(f"Detected report type: {report_type}")
                                
                                analysis = analyze_medical_data(
                                    messages=[{
                                        "role": "user",
                                        "content": f"{patient_context}\n{text}"
                                    }],
                                    is_vision=False,
                                    data_type=report_type
                                )
                                file_id = save_medical_data(name, report_type, text, analysis)
                                processed_ids.append((file.name, file_id, report_type))
                        
                        st.success(f"Processed {file.name} successfully!")
                        
                    except Exception as e:
                        logger.error(f"Error processing {file.name}: {str(e)}", exc_info=True)
                        st.error(f"Error processing {file.name}: {str(e)}")
                
                # Display processed file IDs
                st.write("### Processed Files:")
                for filename, file_id, report_type in processed_ids:
                    st.write(f"- {filename} (ID: {file_id}, Type: {report_type})")
                
                logger.info("All files processed successfully")
                st.success("All files processed! Visit the chat section.")

