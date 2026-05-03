"""
Database migration to add youtube_links column to products table.

This migration adds a new TEXT column 'youtube_links' to store JSON-encoded
video data for each product.
"""
import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """Create and return a database connection."""
    db_path = os.path.join('instance', 'cart.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def check_column_exists(conn, table, column):
    """Check if a column exists in a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [col[1] for col in cursor.fetchall()]
    return column in columns

def add_youtube_links_column():
    """Add youtube_links column to products table if it doesn't exist."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if column already exists
        if check_column_exists(conn, 'products', 'youtube_links'):
            print("Column 'youtube_links' already exists in 'products' table")
            return
        
        # Add the new column
        print("Adding 'youtube_links' column to 'products' table...")
        cursor.execute('''
            ALTER TABLE products 
            ADD COLUMN youtube_links TEXT DEFAULT NULL
        ''')
        
        # Verify the column was added
        if check_column_exists(conn, 'products', 'youtube_links'):
            conn.commit()
            print("Successfully added 'youtube_links' column to 'products' table")
        else:
            print("Failed to add 'youtube_links' column")
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print(f"\nRunning migration: {os.path.basename(__file__)}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    add_youtube_links_column()
    
    print("\nMigration completed.")
