"""Remove budget_range column from user_surveys table."""

import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'cart.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if budget_range column exists
        cursor.execute("PRAGMA table_info(user_surveys)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'budget_range' in columns:
            # SQLite doesn't support DROP COLUMN directly, need to recreate table
            cursor.execute('''
                CREATE TABLE user_surveys_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    skill_level VARCHAR(20) NOT NULL,
                    instrument_type VARCHAR(20) NOT NULL,
                    preferred_genres TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Copy data (excluding budget_range)
            cursor.execute('''
                INSERT INTO user_surveys_new (id, user_id, skill_level, instrument_type, preferred_genres, created_at, updated_at)
                SELECT id, user_id, skill_level, instrument_type, preferred_genres, created_at, updated_at
                FROM user_surveys
            ''')
            
            # Drop old table
            cursor.execute('DROP TABLE user_surveys')
            
            # Rename new table
            cursor.execute('ALTER TABLE user_surveys_new RENAME TO user_surveys')
            
            # Recreate indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_surveys_user_id ON user_surveys(user_id)')
            
            print("Successfully removed budget_range column from user_surveys")
        else:
            print("budget_range column does not exist in user_surveys")
            
        conn.commit()
    except Exception as e:
        print(f"Error removing budget_range: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
