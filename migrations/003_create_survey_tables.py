#!/usr/bin/env python3
"""
Migration 003: Create tables for ML recommendations and survey data
This migration creates:
1. user_surveys table - stores user survey responses
2. recommendation_cache table - caches ML recommendations
3. product_interactions table - tracks user-product interactions
4. Updates products table with guitar-specific attributes
"""

import sqlite3
import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_path():
    """Get the database path from the main app"""
    # Use the same path as app.py
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'cart.db')

def create_survey_tables():
    """Create tables for survey and ML functionality"""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Creating user_surveys table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill_level VARCHAR(20) NOT NULL,
                instrument_type VARCHAR(20) NOT NULL,
                preferred_genres TEXT NOT NULL,  -- JSON array of genres
                budget_range VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        print("Creating recommendation_cache table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendation_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                score REAL NOT NULL,
                algorithm VARCHAR(50) NOT NULL,
                reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        print("Creating product_interactions table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                action VARCHAR(20) NOT NULL,  -- view, like, add_to_cart, purchase, compare
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration INTEGER DEFAULT 0,  -- Time spent viewing product (seconds)
                frequency INTEGER DEFAULT 1,  -- Number of interactions
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        print("Adding guitar-specific columns to products table...")
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'skill_level' not in columns:
            cursor.execute('ALTER TABLE products ADD COLUMN skill_level VARCHAR(20)')
            print("Added skill_level column to products")
        
        if 'genre_suitability' not in columns:
            cursor.execute('ALTER TABLE products ADD COLUMN genre_suitability TEXT')  -- JSON array
            print("Added genre_suitability column to products")
        
        if 'instrument_type' not in columns:
            cursor.execute('ALTER TABLE products ADD COLUMN instrument_type VARCHAR(20)')
            print("Added instrument_type column to products")
        
        if 'price_range' not in columns:
            cursor.execute('ALTER TABLE products ADD COLUMN price_range VARCHAR(20)')
            print("Added price_range column to products")
        
        conn.commit()
        print("✅ Survey and ML tables created successfully!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == '__main__':
    print("Starting migration 003: Create survey and ML tables...")
    success = create_survey_tables()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
        sys.exit(1)
