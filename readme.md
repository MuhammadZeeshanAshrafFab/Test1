# Overview

A Streamlit-based web application for processing and analyzing Blood and DNA reports. The application uses Lalma Vision and Lalma verstile models from GROQ to analyze reports and provides ChatBots with different Prompts to ask qurreis furthers.

## Directory Structure
```
blood_dna_chatbot/
├── database/
│   └── db.py
├── extract_pdf/
│   └── pdf.py
├── logs/
│   └── [auto-generated log files]
├── models/
│   ├── llm.py
│   └── settings.py
├── pages/
│   ├── Blood_report_chatBot1.py
│   ├── Blood_report_chatBot2.py
│   ├── DNA_Chatbot1.py
│   └── DNA_Chatbot2.py
├── process_image/
│   └── image.py
├── prompts/
│   ├── prompt1.py
│   ├── prompt2.py
│   ├── prompt3.py
│   └── prompt4.py
├── utils/
│   └── logger.py
├── main.py
└── requirements.txt
```

## Features
- Upload and process medical reports (PDF, JPG, PNG)
- Automatic detection of report type (Blood/DNA)
- AI-powered analysis of medical reports
- Interactive chat interface for querying analyzed data
- Separate chat interfaces for Blood and DNA analysis
- Comprehensive logging system
- Database storage for medical data and chat history

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd BLood_DNA_ChatBot
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Create a `.streamlit/secrets.toml` file with your GROQ API key:
```toml
GROQ_API_KEY = "your-api-key-here"
```

## Running the Application

1. Start the Streamlit application:
```bash
streamlit run main.py
```

2. Access the application in your web browser at `http://localhost:8501`

## Usage Flow
1. Enter Patient ID or fill in new patient information
2. Upload medical reports (PDF/Images)
3. Wait for AI analysis to complete
4. Navigate to appropriate chat interface:
   - DNA_Chatbot1/2 for genetic analysis
   - Blood_report_chatBot1/2 for blood report analysis
5. Query the analyzed data through the chat interface

## Required Python Packages
- streamlit
- pdfplumber
- Pillow
- sqlite3
- groq
- python-dotenv

## Notes
- Ensure all uploaded files are in supported formats (PDF, JPG, PNG)
- The application creates a SQLite database file named `medical_chatbot.db`
- Log files are automatically generated in the `logs` directory
- Different chat interfaces use different prompts for specialized analysis

## Support
For any issues or questions, please check the logs in the `logs` directory for detailed information about any errors or unexpected behavior.