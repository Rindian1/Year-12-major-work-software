"""
Migration script to populate youtube_links from sound_tests.md to the database.

This script parses the markdown file and updates the products table with
YouTube video data in JSON format.
"""
import re
import json
import sqlite3
import os
from datetime import datetime

# Regular expressions for parsing the markdown file
PRODUCT_PATTERN = r'### (.+)'
VIDEO_PATTERN = r'\\d+\\. \\[(.+?)\\]\\((.+?)\\)(?: - (.+?))?\\s+- Duration: (.+?) • Published: (.+?) • Views: ([\\d,]+)'

class SoundTestParser:
    """Parser for sound_tests.md file."""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.current_product = None
        self.products = {}
    
    def parse(self):
        """Parse the markdown file and extract product video data."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split content into sections for each product
            product_sections = re.split(r'### ', content)[1:]  # Skip the first empty part
            
            for section in product_sections:
                if not section.strip():
                    continue
                
                # Get product name (first line of section)
                lines = [line.strip() for line in section.split('\n') if line.strip()]
                if not lines:
                    continue
                    
                product_name = lines[0].strip()
                self.products[product_name] = []
                
                # Find all video entries in this section
                video_entries = []
                current_entry = []
                
                for line in lines[1:]:  # Skip the product name line
                    if re.match(r'^\d+\.', line):  # New video entry starts with a number
                        if current_entry:  # Save the previous entry if exists
                            video_entries.append(' '.join(current_entry))
                        current_entry = [line]
                    elif current_entry:  # Continue the current entry
                        current_entry.append(line)
                
                # Add the last entry
                if current_entry:
                    video_entries.append(' '.join(current_entry))
                
                # Process each video entry
                for entry in video_entries:
                    # Match the video pattern
                    match = re.search(
                        r'\[(.+?)\]\((.+?)\)(?: - (.+?))?\s*- Duration: (.+?) • Published: (.+?) • Views: ([\d,]+)',
                        entry
                    )
                    
                    if match:
                        title, url, channel, duration, published, views = match.groups()
                        self.products[product_name].append({
                            'title': title.strip(),
                            'url': url.strip(),
                            'channel': (channel or 'Unknown').strip(),
                            'duration': duration.strip(),
                            'published': published.strip(),
                            'views': int(views.replace(',', ''))
                        })
                        
            return self.products
            
        except Exception as e:
            print(f"Error parsing markdown file: {e}")
            return {}

def update_database(products_data):
    """Update the database with the parsed YouTube links."""
    conn = None
    try:
        conn = sqlite3.connect('instance/cart.db')
        cursor = conn.cursor()
        
        updated_count = 0
        
        for product_name, videos in products_data.items():
            # Convert videos to JSON string
            videos_json = json.dumps(videos, ensure_ascii=False)
            
            # Update the product in the database
            cursor.execute(
                "UPDATE products SET youtube_links = ? WHERE name = ?",
                (videos_json, product_name)
            )
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"Updated: {product_name} ({len(videos)} videos)")
            else:
                print(f"Product not found: {product_name}")
        
        conn.commit()
        return updated_count
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()

def main():
    print("\nStarting YouTube links population...")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Parse the markdown file
    parser = SoundTestParser('sound_tests.md')
    products_data = parser.parse()
    
    if not products_data:
        print("No products found in the markdown file or error parsing the file.")
        return
    
    print(f"Found {len(products_data)} products with video data")
    
    # Update the database
    updated_count = update_database(products_data)
    
    print("\nMigration summary:")
    print(f"- Products processed: {len(products_data)}")
    print(f"- Products updated: {updated_count}")
    print(f"- Total videos processed: {sum(len(v) for v in products_data.values())}")

if __name__ == "__main__":
    main()
