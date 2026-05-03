"""Database migration script to add probabilities column"""
import sqlite3

# Connect to database
conn = sqlite3.connect('packaging_data.db')
cursor = conn.cursor()

try:
    # Add probabilities column to predictions table
    cursor.execute("ALTER TABLE predictions ADD COLUMN probabilities TEXT")
    conn.commit()
    print("[OK] Added probabilities column to predictions table")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("[INFO] Column already exists")
    else:
        print(f"[ERROR] {e}")
finally:
    conn.close()

# Made with Bob
