#!/usr/bin/env python3
"""
Migration 006: Seed 200 more user survey entries
This migration adds 200 additional user survey records to expand the ML training data
"""

import sqlite3
import os
import sys
import json
import random

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_path():
    """Get the database path from the main app"""
    # Use the same path as app.py
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'cart.db')

def generate_additional_surveys():
    """Generate 200 additional user survey records"""
    skill_levels = ['beginner', 'intermediate', 'advanced', 'professional']
    instrument_types = ['acoustic', 'electric', 'both']
    genres = ['rock', 'blues', 'jazz', 'classical', 'metal', 'pop', 'country', 'folk', 'indie']
    budget_ranges = ['under_500', '500_1000', '1000_2000', '2000_5000', 'over_5000']
    
    surveys = []
    
    # Generate 200 additional survey records
    for i in range(101, 301):  # Continue from user ID 101
        # Create realistic combinations with some patterns
        
        # Skill level distribution - more beginners and intermediates
        skill_weights = [0.35, 0.35, 0.20, 0.10]  # beginner, intermediate, advanced, professional
        skill_level = random.choices(skill_levels, weights=skill_weights)[0]
        
        # Instrument type distribution - slight preference for electric
        instrument_weights = [0.30, 0.50, 0.20]  # acoustic, electric, both
        instrument_type = random.choices(instrument_types, weights=instrument_weights)[0]
        
        # Genre preferences - realistic combinations
        num_genres = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        preferred_genres = random.sample(genres, num_genres)
        
        # Budget range distribution - more mid-range budgets
        budget_weights = [0.20, 0.30, 0.25, 0.15, 0.10]  # under_500, 500_1000, 1000_2000, 2000_5000, over_5000
        budget_range = random.choices(budget_ranges, weights=budget_weights)[0]
        
        surveys.append({
            'user_id': i,
            'skill_level': skill_level,
            'instrument_type': instrument_type,
            'preferred_genres': json.dumps(preferred_genres),
            'budget_range': budget_range
        })
    
    return surveys

def seed_more_surveys():
    """Seed 200 additional user survey records"""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current survey count
        cursor.execute('SELECT COUNT(*) FROM user_surveys')
        current_count = cursor.fetchone()[0]
        print(f"Current survey count: {current_count}")
        
        # Generate additional surveys
        additional_surveys = generate_additional_surveys()
        
        print("Seeding 200 additional user surveys...")
        
        # First, create additional users if needed
        cursor.execute('SELECT MAX(id) FROM users')
        max_user_result = cursor.fetchone()[0]
        max_user_id = max_user_result if max_user_result is not None else 100
        
        users_to_create = []
        for survey in additional_surveys:
            if survey['user_id'] > max_user_id:
                users_to_create.append({
                    'id': survey['user_id'],
                    'username': f"user_{survey['user_id']:03d}",
                    'email': f"user{survey['user_id']}@example.com",
                    'password_hash': f"hashed_password_{survey['user_id']}"
                })
        
        # Create additional users
        for user in users_to_create:
            cursor.execute('''
                INSERT OR IGNORE INTO users (id, username, email, password_hash) VALUES (?, ?, ?, ?)
            ''', (user['id'], user['username'], user['email'], user['password_hash']))
        
        # Insert survey data
        inserted_count = 0
        for survey in additional_surveys:
            cursor.execute('''
                INSERT OR REPLACE INTO user_surveys 
                (user_id, skill_level, instrument_type, preferred_genres, budget_range)
                VALUES (?, ?, ?, ?, ?)
            ''', (survey['user_id'], survey['skill_level'], survey['instrument_type'], 
                  survey['preferred_genres'], survey['budget_range']))
            inserted_count += 1
        
        conn.commit()
        
        # Verify final count
        cursor.execute('SELECT COUNT(*) FROM user_surveys')
        final_count = cursor.fetchone()[0]
        
        print("✅ Additional survey seeding completed successfully!")
        print(f"  ✓ Added {inserted_count} new survey records")
        print(f"  ✓ Created {len(users_to_create)} new users")
        print(f"  ✓ Total survey records: {final_count}")
        
        # Show distribution statistics
        cursor.execute('''
            SELECT skill_level, COUNT(*) 
            FROM user_surveys 
            GROUP BY skill_level 
            ORDER BY COUNT(*) DESC
        ''')
        skill_dist = cursor.fetchall()
        print(f"  ✓ Skill level distribution: {skill_dist}")
        
        cursor.execute('''
            SELECT instrument_type, COUNT(*) 
            FROM user_surveys 
            GROUP BY instrument_type 
            ORDER BY COUNT(*) DESC
        ''')
        instrument_dist = cursor.fetchall()
        print(f"  ✓ Instrument type distribution: {instrument_dist}")
        
        cursor.execute('''
            SELECT budget_range, COUNT(*) 
            FROM user_surveys 
            GROUP BY budget_range 
            ORDER BY COUNT(*) DESC
        ''')
        budget_dist = cursor.fetchall()
        print(f"  ✓ Budget range distribution: {budget_dist}")
        
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
    print("Starting migration 006: Seed 200 additional user surveys...")
    success = seed_more_surveys()
    if success:
        print("Additional survey seeding completed successfully!")
    else:
        print("Additional survey seeding failed!")
        sys.exit(1)
