# database.py
import sqlite3

DB_NAME = "results.db"


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


def save_result(candidate, score, match_pct):
    """Insert a single candidate's result into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (candidate, score, match_pct) VALUES (?, ?, ?)",
        (candidate, score, match_pct)
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