import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ebooks.db')
db_path = os.path.abspath(db_path)

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(books)")
    book_columns = [col[1] for col in cursor.fetchall()]
    
    cursor.execute("PRAGMA table_info(generation_history)")
    history_columns = [col[1] for col in cursor.fetchall()]
    
    if 'language' not in book_columns:
        cursor.execute("ALTER TABLE books ADD COLUMN language TEXT")
        print("Added 'language' column to books table")
    else:
        print("'language' column already exists in books table")
    
    if 'language' not in history_columns:
        cursor.execute("ALTER TABLE generation_history ADD COLUMN language TEXT")
        print("Added 'language' column to generation_history table")
    else:
        print("'language' column already exists in generation_history table")
    
    conn.commit()
    conn.close()
    print("Database migration completed successfully")
else:
    print("Database file not found, will be created on startup")
