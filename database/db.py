import sqlite3
from contextlib import closing
from utils.logger import setup_logger

logger = setup_logger('database')

def init_db():
    logger.info("Initializing database...")
    with closing(sqlite3.connect("medical_chatbot.db")) as conn:
        c = conn.cursor()
        
        # Create medical_data table
        c.execute('''CREATE TABLE IF NOT EXISTS medical_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        data_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        analysis TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
        
        # Create chat_history table
        c.execute('''CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        chat_type TEXT NOT NULL,
                        user_input TEXT NOT NULL,
                        response TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )''')
        
        conn.commit()
        logger.info("Database initialized successfully")

def save_medical_data(name, data_type, content, analysis):
    logger.info(f"Saving medical data for {name} of type {data_type}")
    # Add content validation
    if isinstance(content, bytes):
        content = content.decode('utf-8')
        
    with closing(sqlite3.connect("medical_chatbot.db")) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO medical_data 
                    (name, data_type, content, analysis)
                    VALUES (?, ?, ?, ?)''',
                (name, data_type, str(content), str(analysis)))
        last_id = c.lastrowid
        conn.commit()
        logger.info(f"Medical data saved successfully with ID: {last_id}")
        return last_id

def get_medical_data_by_id(id, data_type=None):
  
    logger.info(f"Retrieving medical data for ID: {id}" + (f" of type {data_type}" if data_type else ""))
    with closing(sqlite3.connect("medical_chatbot.db")) as conn:
        c = conn.cursor()
        # First get the patient name associated with this ID
        c.execute("SELECT DISTINCT name FROM medical_data WHERE id = ?", (id,))
        name_result = c.fetchone()
        
        if name_result:
            name = name_result[0]
            if data_type:
                c.execute("""SELECT * FROM medical_data 
                           WHERE name = ? AND data_type = ? 
                           ORDER BY timestamp DESC""", (name, data_type))
            else:
                c.execute("""SELECT * FROM medical_data 
                           WHERE name = ? 
                           ORDER BY timestamp DESC""", (name,))
            data = c.fetchall()
            return data, name
        return None, None

def save_chat(name, chat_type, user_input, response):
    logger.info(f"Saving chat for {name} of type {chat_type}")
    conn = sqlite3.connect("medical_chatbot.db")
    c = conn.cursor()
    c.execute('''INSERT INTO chat_history (name, chat_type, user_input, response)
                 VALUES (?, ?, ?, ?)''',
              (name, chat_type, user_input, response))
    last_id = c.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Chat saved successfully with ID: {last_id}")
    return last_id