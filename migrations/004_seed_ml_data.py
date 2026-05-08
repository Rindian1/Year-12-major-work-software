#!/usr/bin/env python3
"""
Migration 004: Seed ML data with sample users, surveys, products, and interactions
This migration populates the database with:
1. 20 sample user profiles with survey responses
2. Enhanced product data with guitar-specific attributes
3. User interaction data for ML training
"""

import sqlite3
import os
import sys
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_path():
    """Get the database path from the main app"""
    # Use the same path as app.py
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'cart.db')

def seed_ml_data():
    """Seed database with ML training data"""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Sample user profiles with survey data
        sample_users = [
            {
                'username': 'rock_mike',
                'email': 'mike@example.com',
                'password_hash': 'hashed_password_1',
                'skill_level': 'intermediate',
                'instrument_type': 'electric',
                'preferred_genres': '["rock", "blues"]',
                'budget_range': '1000_2000'
            },
            {
                'username': 'acoustic_sarah',
                'email': 'sarah@example.com',
                'password_hash': 'hashed_password_2',
                'skill_level': 'beginner',
                'instrument_type': 'acoustic',
                'preferred_genres': '["folk", "indie"]',
                'budget_range': '500_1000'
            },
            {
                'username': 'jazz_tom',
                'email': 'tom@example.com',
                'password_hash': 'hashed_password_3',
                'skill_level': 'professional',
                'instrument_type': 'both',
                'preferred_genres': '["jazz", "blues"]',
                'budget_range': 'over_5000'
            },
            {
                'username': 'metal_alex',
                'email': 'alex@example.com',
                'password_hash': 'hashed_password_4',
                'skill_level': 'advanced',
                'instrument_type': 'electric',
                'preferred_genres': '["metal", "rock"]',
                'budget_range': '2000_5000'
            },
            {
                'username': 'country_jenny',
                'email': 'jenny@example.com',
                'password_hash': 'hashed_password_5',
                'skill_level': 'intermediate',
                'instrument_type': 'both',
                'preferred_genres': '["country", "folk"]',
                'budget_range': '1000_2000'
            },
            {
                'username': 'classical_maria',
                'email': 'maria@example.com',
                'password_hash': 'hashed_password_6',
                'skill_level': 'intermediate',
                'instrument_type': 'acoustic',
                'preferred_genres': '["classical", "folk"]',
                'budget_range': '1000_2000'
            },
            {
                'username': 'punk_dave',
                'email': 'dave@example.com',
                'password_hash': 'hashed_password_7',
                'skill_level': 'beginner',
                'instrument_type': 'electric',
                'preferred_genres': '["punk", "rock"]',
                'budget_range': 'under_500'
            },
            {
                'username': 'blues_robert',
                'email': 'robert@example.com',
                'password_hash': 'hashed_password_8',
                'skill_level': 'advanced',
                'instrument_type': 'electric',
                'preferred_genres': '["blues", "rock"]',
                'budget_range': '2000_5000'
            },
            {
                'username': 'pop_emma',
                'email': 'emma@example.com',
                'password_hash': 'hashed_password_9',
                'skill_level': 'beginner',
                'instrument_type': 'both',
                'preferred_genres': '["pop", "indie"]',
                'budget_range': '500_1000'
            },
            {
                'username': 'fusion_carlos',
                'email': 'carlos@example.com',
                'password_hash': 'hashed_password_10',
                'skill_level': 'professional',
                'instrument_type': 'electric',
                'preferred_genres': '["jazz", "rock", "metal"]',
                'budget_range': 'over_5000'
            },
            {
                'username': 'folk_lisa',
                'email': 'lisa@example.com',
                'password_hash': 'hashed_password_11',
                'skill_level': 'intermediate',
                'instrument_type': 'acoustic',
                'preferred_genres': '["folk", "country"]',
                'budget_range': '1000_2000'
            },
            {
                'username': 'metal_james',
                'email': 'james@example.com',
                'password_hash': 'hashed_password_12',
                'skill_level': 'advanced',
                'instrument_type': 'electric',
                'preferred_genres': '["metal", "hard_rock"]',
                'budget_range': '2000_5000'
            },
            {
                'username': 'indie_amy',
                'email': 'amy@example.com',
                'password_hash': 'hashed_password_13',
                'skill_level': 'beginner',
                'instrument_type': 'acoustic',
                'preferred_genres': '["indie", "pop"]',
                'budget_range': '500_1000'
            },
            {
                'username': 'rock_kevin',
                'email': 'kevin@example.com',
                'password_hash': 'hashed_password_14',
                'skill_level': 'intermediate',
                'instrument_type': 'electric',
                'preferred_genres': '["rock", "pop"]',
                'budget_range': '1000_2000'
            },
            {
                'username': 'jazz_susan',
                'email': 'susan@example.com',
                'password_hash': 'hashed_password_15',
                'skill_level': 'professional',
                'instrument_type': 'both',
                'preferred_genres': '["jazz", "classical"]',
                'budget_range': 'over_5000'
            },
            {
                'username': 'country_mark',
                'email': 'mark@example.com',
                'password_hash': 'hashed_password_16',
                'skill_level': 'advanced',
                'instrument_type': 'electric',
                'preferred_genres': '["country", "rock"]',
                'budget_range': '2000_5000'
            },
            {
                'username': 'beginner_tim',
                'email': 'tim@example.com',
                'password_hash': 'hashed_password_17',
                'skill_level': 'beginner',
                'instrument_type': 'acoustic',
                'preferred_genres': '["pop", "rock"]',
                'budget_range': 'under_500'
            },
            {
                'username': 'progressive_steve',
                'email': 'steve@example.com',
                'password_hash': 'hashed_password_18',
                'skill_level': 'advanced',
                'instrument_type': 'electric',
                'preferred_genres': '["metal", "progressive", "jazz"]',
                'budget_range': '2000_5000'
            },
            {
                'username': 'singer_rachel',
                'email': 'rachel@example.com',
                'password_hash': 'hashed_password_19',
                'skill_level': 'intermediate',
                'instrument_type': 'acoustic',
                'preferred_genres': '["folk", "pop", "indie"]',
                'budget_range': '1000_2000'
            },
            {
                'username': 'studio_john',
                'email': 'john@example.com',
                'password_hash': 'hashed_password_20',
                'skill_level': 'professional',
                'instrument_type': 'both',
                'preferred_genres': '["rock", "pop", "jazz", "country"]',
                'budget_range': 'over_5000'
            }
        ]
        
        print("Seeding users and survey data...")
        for i, user in enumerate(sample_users, 1):
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password_hash) VALUES (?, ?, ?)
            ''', (user['username'], user['email'], user['password_hash']))
            
            # Get the user ID
            cursor.execute('SELECT id FROM users WHERE username = ?', (user['username'],))
            user_result = cursor.fetchone()
            
            if user_result:
                user_id = user_result[0]
                cursor.execute('''
                    INSERT OR REPLACE INTO user_surveys 
                    (user_id, skill_level, instrument_type, preferred_genres, budget_range)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, user['skill_level'], user['instrument_type'], 
                      user['preferred_genres'], user['budget_range']))
                
                print(f"  ✓ Seeded user {i}/20: {user['username']}")
        
        # Enhanced product data with guitar-specific attributes
        enhanced_products = [
            {
                'name': 'Gibson SG Standard',
                'category': 'guitars',
                'price': 1299.99,
                'description': 'Classic electric guitar with mahogany body and humbucker pickups',
                'image_url': '/static/Images/gibson_sg.jpg',
                'stock': 5,
                'skill_level': 'intermediate',
                'genre_suitability': '["rock", "blues", "hard_rock"]',
                'instrument_type': 'electric',
                'price_range': '1000_2000'
            },
            {
                'name': 'Fender Stratocaster',
                'category': 'guitars',
                'price': 1499.99,
                'description': 'Iconic electric guitar with three single-coil pickups',
                'image_url': '/static/Images/fender_strat.jpg',
                'stock': 8,
                'skill_level': 'intermediate',
                'genre_suitability': '["rock", "blues", "pop", "country"]',
                'instrument_type': 'electric',
                'price_range': '1000_2000'
            },
            {
                'name': 'Ibanez RG550',
                'category': 'guitars',
                'price': 899.99,
                'description': 'High-performance electric guitar for rock and metal',
                'image_url': '/static/Images/ibanez_rg550.jpg',
                'stock': 6,
                'skill_level': 'advanced',
                'genre_suitability': '["metal", "rock", "hard_rock"]',
                'instrument_type': 'electric',
                'price_range': '500_1000'
            },
            {
                'name': 'Gibson ES-175',
                'category': 'guitars',
                'price': 4499.99,
                'description': 'Classic hollow body electric guitar for jazz',
                'image_url': '/static/Images/gibson_es175.jpg',
                'stock': 3,
                'skill_level': 'professional',
                'genre_suitability': '["jazz", "blues", "classical"]',
                'instrument_type': 'electric',
                'price_range': '2000_5000'
            },
            {
                'name': 'Martin DXE',
                'category': 'guitars',
                'price': 599.99,
                'description': 'Affordable acoustic guitar with rich tone',
                'image_url': '/static/Images/martin_dxe.jpg',
                'stock': 10,
                'skill_level': 'beginner',
                'genre_suitability': '["folk", "country", "indie"]',
                'instrument_type': 'acoustic',
                'price_range': '500_1000'
            },
            {
                'name': 'Taylor 214ce',
                'category': 'guitars',
                'price': 1199.99,
                'description': 'Premium acoustic guitar with electronics',
                'image_url': '/static/Images/taylor_214ce.jpg',
                'stock': 4,
                'skill_level': 'intermediate',
                'genre_suitability': '["folk", "pop", "country"]',
                'instrument_type': 'acoustic',
                'price_range': '1000_2000'
            },
            {
                'name': 'Marshall JCM800',
                'category': 'amplifiers',
                'price': 1599.99,
                'description': 'Iconic tube amplifier for rock',
                'image_url': '/static/Images/marshall_jcm800.jpg',
                'stock': 7,
                'skill_level': 'advanced',
                'genre_suitability': '["rock", "hard_rock", "metal"]',
                'instrument_type': 'electric',
                'price_range': '1000_2000'
            },
            {
                'name': 'Boss DS-1 Distortion',
                'category': 'effects',
                'price': 49.99,
                'description': 'Classic distortion pedal for rock and metal',
                'image_url': '/static/Images/boss_ds1.jpg',
                'stock': 15,
                'skill_level': 'beginner',
                'genre_suitability': '["rock", "metal", "hard_rock"]',
                'instrument_type': 'electric',
                'price_range': 'under_500'
            },
            {
                'name': 'Ibanez Tube Screamer',
                'category': 'effects',
                'price': 89.99,
                'description': 'Classic overdrive pedal for blues and rock',
                'image_url': '/static/Images/ibanez_ts9.jpg',
                'stock': 12,
                'skill_level': 'intermediate',
                'genre_suitability': '["rock", "blues", "pop"]',
                'instrument_type': 'electric',
                'price_range': 'under_500'
            },
            {
                'name': 'Strymon Timeline',
                'category': 'effects',
                'price': 449.99,
                'description': 'Professional delay pedal with multiple delay types',
                'image_url': '/static/Images/strymon_timeline.jpg',
                'stock': 5,
                'skill_level': 'professional',
                'genre_suitability': '["jazz", "rock", "ambient"]',
                'instrument_type': 'both',
                'price_range': '2000_5000'
            }
        ]
        
        print("Seeding enhanced product data...")
        for product in enhanced_products:
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (name, category, price, description, image_url, stock, 
                 skill_level, genre_suitability, instrument_type, price_range)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (product['name'], product['category'], product['price'], 
                  product['description'], product['image_url'], product['stock'],
                  product['skill_level'], product['genre_suitability'], 
                  product['instrument_type'], product['price_range']))
        
        # Create sample user interactions for ML training
        print("Creating sample user interactions...")
        sample_interactions = [
            # Mike's interactions (rock/blues intermediate)
            (1, 1, 'view', '2024-01-15 10:00:00', 120, 1),
            (1, 1, 'add_to_cart', '2024-01-15 10:02:00', 0, 1),
            (1, 1, 'purchase', '2024-01-16 14:30:00', 0, 1),
            (1, 10, 'view', '2024-01-17 09:00:00', 180, 1),
            
            # Sarah's interactions (folk/indie beginner)
            (2, 5, 'view', '2024-01-18 11:00:00', 90, 1),
            (2, 5, 'view', '2024-01-18 11:05:00', 150, 1),
            (2, 6, 'add_to_cart', '2024-01-18 11:10:00', 0, 1),
            (2, 5, 'purchase', '2024-01-20 16:00:00', 0, 1),
            
            # Tom's interactions (jazz professional)
            (3, 4, 'view', '2024-01-22 08:30:00', 240, 1),
            (3, 4, 'view', '2024-01-22 08:35:00', 300, 1),
            (3, 4, 'purchase', '2024-01-25 13:00:00', 0, 1),
            (3, 11, 'view', '2024-01-26 10:00:00', 180, 1),
            
            # Alex's interactions (metal advanced)
            (4, 3, 'view', '2024-01-28 14:00:00', 60, 1),
            (4, 3, 'add_to_cart', '2024-01-28 14:02:00', 0, 1),
            (4, 3, 'purchase', '2024-01-30 19:00:00', 0, 1),
            (4, 2, 'view', '2024-02-01 15:00:00', 90, 1),
            
            # Additional interactions for variety
            (5, 7, 'view', '2024-02-03 10:00:00', 120, 1),
            (5, 7, 'purchase', '2024-02-05 17:00:00', 0, 1),
            (6, 8, 'view', '2024-02-07 09:00:00', 200, 1),
            (6, 8, 'add_to_cart', '2024-02-07 09:05:00', 0, 1),
            (7, 9, 'view', '2024-02-09 14:00:00', 45, 1),
            (7, 1, 'view', '2024-02-10 11:00:00', 180, 1),
            (8, 10, 'view', '2024-02-12 16:00:00', 150, 1),
            (8, 10, 'purchase', '2024-02-14 20:00:00', 0, 1),
            (9, 11, 'view', '2024-02-16 13:00:00', 80, 1),
            (9, 2, 'view', '2024-02-16 13:05:00', 120, 1),
            (10, 12, 'view', '2024-02-18 10:00:00', 300, 1),
            (10, 12, 'purchase', '2024-02-20 15:00:00', 0, 1)
        ]
        
        for interaction in sample_interactions:
            cursor.execute('''
                INSERT INTO product_interactions 
                (user_id, product_id, action, timestamp, duration, frequency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', interaction)
        
        conn.commit()
        print("✅ ML data seeding completed successfully!")
        print(f"  ✓ Seeded {len(sample_users)} users with survey data")
        print(f"  ✓ Seeded {len(enhanced_products)} enhanced products")
        print(f"  ✓ Seeded {len(sample_interactions)} user interactions")
        
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
    print("Starting migration 004: Seed ML data...")
    success = seed_ml_data()
    if success:
        print("ML data seeding completed successfully!")
    else:
        print("ML data seeding failed!")
        sys.exit(1)
