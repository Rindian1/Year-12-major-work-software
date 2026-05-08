#!/usr/bin/env python3
"""
Migration 005: Expand ML data to 200+ rows for better training
This migration adds:
1. 80+ additional user profiles with diverse survey data
2. 40+ additional products with guitar-specific attributes
3. 200+ additional user interactions for comprehensive training data
"""

import sqlite3
import os
import sys
import json
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_path():
    """Get the database path from the main app"""
    # Use the same path as app.py
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'cart.db')

def generate_user_profiles():
    """Generate diverse user profiles with survey data"""
    skill_levels = ['beginner', 'intermediate', 'advanced', 'professional']
    instrument_types = ['acoustic', 'electric', 'both']
    genres = ['rock', 'blues', 'jazz', 'classical', 'metal', 'pop', 'country', 'folk', 'indie']
    budget_ranges = ['under_500', '500_1000', '1000_2000', '2000_5000', 'over_5000']
    
    users = []
    
    # Generate 80 additional users (total 100 with original 20)
    for i in range(21, 101):
        user_id = i
        username = f"user_{user_id:03d}"
        email = f"user{user_id}@example.com"
        password_hash = f"hashed_password_{user_id}"
        
        # Randomly assign attributes with some bias towards realistic combinations
        skill_level = random.choice(skill_levels)
        instrument_type = random.choice(instrument_types)
        
        # Select 1-3 genres per user
        num_genres = random.randint(1, 3)
        preferred_genres = json.dumps(random.sample(genres, num_genres))
        
        budget_range = random.choice(budget_ranges)
        
        users.append({
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'skill_level': skill_level,
            'instrument_type': instrument_type,
            'preferred_genres': preferred_genres,
            'budget_range': budget_range
        })
    
    return users

def generate_additional_products():
    """Generate 40 additional products with guitar-specific attributes"""
    genres = ['rock', 'blues', 'jazz', 'classical', 'metal', 'pop', 'country', 'folk', 'indie']
    
    product_names = {
        'guitars': [
            'Epiphone Les Paul Standard', 'Gretsch White Falcon', 'PRS SE Custom 24',
            'Music Man JP6', 'Rickenbacker 360', 'ESP LTD EC-1000',
            'Charvel Pro-Mod DK24', 'Schecter C-1 Hellraiser', 'Jackson Soloist SL2',
            'Yamaha Pacifica 112V', 'Cort KX5', 'Dean ML XM',
            'Ibanez JEM777', 'Kramer Pacer Vintage', 'Hamer Sunburst',
            'Washburn Dimebag', 'BC Rich Mockingbird', 'Gibson Flying V',
            'Fender Jaguar', 'Gibson Explorer', 'ESP LTD M-1000',
            'Jackson RR24', 'Charvel San Dimas', 'Schecter Hellraiser C-1',
            'Ibanez S Series', 'Paul Reed Smith Custom 24', 'Anderson Guitarworks',
            'Suhr Modern', 'Tom Anderson Guitar', 'James Tyler Variax',
            'Don Grosh Retro Classic', 'Kiesel Guitars', 'Maybach Guitars'
        ],
        'amplifiers': [
            'Fender Blues Junior', 'Vox AC30', 'Orange Rockerverb 50',
            'Mesa Boogie Mark Five', 'Hughes & Kettner Tube R50',
            'Blackstar HT Club 40', 'Laney Lionheart L20H',
            'Bugera V55', 'Egnater Tweaker 40',
            'Marshall DSL40C', 'Fender Hot Rod Deluxe',
            'Peavey 6505+', 'Randall RG75',
            'Diezel VH4', 'Friedman BE-50', 'Bogner Alchemist',
            'Dr. Z Maz 18 NR', 'Two Rock ET100',
            'Morgan PR12', 'Carr Rambler', 'Swart AST Pro',
            'Victory V40 Deluxe', 'Matchless DC30',
            'Kemper Profiler Rack', 'Fractal Audio Axe-Fx III',
            'Line 6 Helix LT', 'Boss GT-1000',
            'Yamaha THR100H', 'Blackstar Studio 10'
        ],
        'effects': [
            'Electro-Harmonix POG2', 'Boss CE-2W Chorus', 'MXR Carbon Copy Delay',
            'Strymon BigSky Reverb', 'EarthQuaker Devices Rainbow Machine',
            'Wampler Tumnus Overdrive', 'Fulltone OCD', 'ProCo RAT2',
            'Ibanez Tube Screamer Mini', 'JHS Pedals Morning Glory',
            'ZVEX Box of Rock', 'EarthQuaker Devices Rainbow Machine',
            'Catalinbread Belle Epoch', 'Malekko Sprague Atom',
            'Keeley Electronics Nova Wah', 'Dunlop Cry Baby Wah',
            'EHX Small Stone', 'Moog Minifooger', 'Death By Audio Audio',
            'Walrus Audio Julia Analog Chorus/Vibrato',
            'Chase Bliss Audio Mood', 'Empress Effects ZOIA',
            'JHS Pedals Colour Box', 'Boss DD-7 Digital Delay',
            'TC Electronic Ditto Looper', 'Strymon El Capistan',
            'EarthQuaker Devices Afterneath', 'Catalinbread Antichron',
            'Wampler Ego Compressor', 'Diamond Compressor',
            'MXR Dyna Comp', 'Keeley 2 Knob Compressor',
            'Boss RC-3 Loop Station', 'TC Electronic Ditto X4 Looper'
        ],
        'accessories': [
            'Dunlop Tortex Standard Picks', 'Ernie Ball Power Slinky Strings',
            'Elixir Nanoweb Strings', 'DAddario EXL110 Strings',
            'GHS Boomers Strings', 'Fender 351 Shape Picks',
            'Jim Dunlop Jazz III Picks', 'Planet Waves Lock-It Straps',
            'Levy\'s Leather Straps', 'Ernie Ball Poly Strap',
            'Gator Cases', 'SKB Cases', 'Hiscox Cases',
            'Pedaltrain Pedalboards', 'Voodoo Lab Pedal Power',
            'Truetone Clean Buffer', 'Boss TU-3 Chromatic Tuner',
            'Peterson StroboStomp HD', 'Korg Pitchblack',
            'Shure SM57 Microphone', 'Sennheiser e906',
            'Audio-Technica AT2020', 'AKG P120',
            'Focusrite Scarlett 2i2', 'M-Audio M-Track',
            'PreSonus AudioBox USB96', 'Steinberg UR12',
            'IK Multimedia iRig HD', 'Line 6 POD HD500X'
        ]
    }
    
    products = []
    product_id = 11  # Start from ID 11 (since we have 10 products already)
    
    for category, names in product_names.items():
        for name in names:
            price = round(random.uniform(29.99, 2499.99), 2)
            stock = random.randint(1, 20)
            
            # Assign guitar-specific attributes based on product type
            if category == 'guitars':
                skill_level = random.choice(['beginner', 'intermediate', 'advanced', 'professional'])
                genre_suitability = json.dumps(random.sample(genres, random.randint(2, 4)))
                instrument_type = 'electric' if 'electric' in name.lower() or random.random() > 0.3 else 'acoustic'
                price_range = 'under_500' if price < 500 else '500_1000' if price < 1000 else '1000_2000' if price < 2000 else '2000_5000' if price < 5000 else 'over_5000'
            elif category == 'amplifiers':
                skill_level = random.choice(['intermediate', 'advanced', 'professional'])
                genre_suitability = json.dumps(['rock', 'blues', 'metal', 'jazz', 'pop'])
                instrument_type = 'electric'
                price_range = '500_1000' if price < 1000 else '1000_2000' if price < 2000 else '2000_5000' if price < 5000 else 'over_5000'
            elif category == 'effects':
                skill_level = random.choice(['beginner', 'intermediate', 'advanced'])
                genre_suitability = json.dumps(['rock', 'blues', 'pop', 'indie', 'metal'])
                instrument_type = 'electric'
                price_range = 'under_500' if price < 500 else '500_1000'
            else:  # accessories
                skill_level = 'beginner'
                genre_suitability = json.dumps(genres)
                instrument_type = 'both'
                price_range = 'under_500'
            
            products.append({
                'name': name,
                'category': category,
                'price': price,
                'description': f'High-quality {category} for musicians',
                'image_url': f'/static/Images/{category.lower()}/{name.lower().replace(" ", "_")}.jpg',
                'stock': stock,
                'skill_level': skill_level,
                'genre_suitability': genre_suitability,
                'instrument_type': instrument_type,
                'price_range': price_range
            })
            
            product_id += 1
    
    return products

def generate_additional_interactions():
    """Generate 200+ additional user interactions"""
    interactions = []
    interaction_types = ['view', 'add_to_cart', 'purchase', 'compare']
    
    # Generate interactions for users 1-100
    for user_id in range(1, 101):
        # Each user has 2-5 interactions on average
        num_interactions = random.randint(2, 5)
        
        for _ in range(num_interactions):
            # Bias towards viewing products, some purchases
            action_weights = [0.5, 0.2, 0.2, 0.1]  # view, add_to_cart, purchase, compare
            action = random.choices(interaction_types, weights=action_weights)[0]
            
            # Random product ID (assuming we have up to 50 products after expansion)
            product_id = random.randint(1, 50)
            
            # Random timestamp within last 30 days
            days_ago = random.randint(0, 30)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            # Duration for views (30 seconds to 10 minutes)
            duration = random.randint(30, 600) if action == 'view' else 0
            
            # Frequency (mostly 1, occasional repeats)
            frequency = random.randint(1, 3)
            
            interactions.append({
                'user_id': user_id,
                'product_id': product_id,
                'action': action,
                'timestamp': timestamp.isoformat(),
                'duration': duration,
                'frequency': frequency
            })
    
    return interactions

def expand_ml_data():
    """Expand ML data to 200+ rows"""
    db_path = get_db_path()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Generate and insert additional users
        print("Generating and inserting additional users...")
        additional_users = generate_user_profiles()
        
        for user in additional_users:
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
        
        # Generate and insert additional products
        print("Generating and inserting additional products...")
        additional_products = generate_additional_products()
        
        for product in additional_products:
            cursor.execute('''
                INSERT OR REPLACE INTO products 
                (name, category, price, description, image_url, stock, 
                 skill_level, genre_suitability, instrument_type, price_range)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (product['name'], product['category'], product['price'], 
                  product['description'], product['image_url'], product['stock'],
                  product['skill_level'], product['genre_suitability'], 
                  product['instrument_type'], product['price_range']))
        
        # Generate and insert additional interactions
        print("Generating and inserting additional interactions...")
        additional_interactions = generate_additional_interactions()
        
        for interaction in additional_interactions:
            cursor.execute('''
                INSERT INTO product_interactions 
                (user_id, product_id, action, timestamp, duration, frequency)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interaction['user_id'], interaction['product_id'], interaction['action'], 
                  interaction['timestamp'], interaction['duration'], interaction['frequency']))
        
        conn.commit()
        print("✅ ML data expansion completed successfully!")
        print(f"  ✓ Added {len(additional_users)} additional users")
        print(f"  ✓ Added {len(additional_products)} additional products") 
        print(f"  ✓ Added {len(additional_interactions)} additional interactions")
        print(f"  ✓ Total users: 100")
        print(f"  ✓ Total products: 50")
        print(f"  ✓ Total interactions: {28 + len(additional_interactions)}")
        
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
    print("Starting migration 005: Expand ML data to 200+ rows...")
    success = expand_ml_data()
    if success:
        print("ML data expansion completed successfully!")
    else:
        print("ML data expansion failed!")
        sys.exit(1)
