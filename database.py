# database.py
import sqlite3
import os

# Render par file path ka issue na ho, isliye absolute path handle kiya hai
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "results.db")

def init_db():
    """Create the results table if it doesn't already exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate TEXT NOT NULL,
            score INTEGER NOT NULL,
            match_pct REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_NAME)

def save_result(candidate, score, match_pct):
    """Insert a single candidate's result into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (candidate, score, match_pct) VALUES (?, ?, ?)",
        (candidate, int(score), float(match_pct))
    )
    conn.commit()
    conn.close()

def get_all_results():
    """Fetch all stored results, most recent first."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT candidate, score, match_pct, created_at FROM results ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Testing ke liye agar is file ko direct run karein
if __name__ == "__main__":
  init_db()