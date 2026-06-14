import sqlite3
import os

# Database file ka naam
DB_NAME = "resume_analyzer.db"

def get_connection():
    """Database se connect karne ke liye helper function"""
    conn = sqlite3.connect(DB_NAME)
    # Isse data dictionary format (column name ke sath) me fetch hota hai
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Database aur Tables create karne ke liye function"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table (Agar login system chahiye ho)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')
    
    # 2. History Table (Upload kiye gaye resumes ka data save karne ke liye)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            filename TEXT NOT NULL,
            job_description TEXT,
            match_score REAL,
            skills_found TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database Initialized Successfully!")

def save_analysis(filename, job_description, match_score, skills_found):
    """Analysis ka result database me save karne ke liye"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analysis_history (filename, job_description, match_score, skills_found)
            VALUES (?, ?, ?, ?)
        ''', (filename, job_description, match_score, str(skills_found)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving to database: {e}")
        return False

def get_history():
    """Pura purana history data fetch karne ke liye (Streamlit dashboard par dikhane ke liye)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM analysis_history ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Jab is file ko direct run karein toh table automatic ban jaye
if __name__ == "__main__":
    init_db()