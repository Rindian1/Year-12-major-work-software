#!/usr/bin/env python3
"""
YouTube Sound Test Link Generator for Guitar Store

This script searches YouTube for sound demos of products in the store
generates a markdown file with links to the top 3 videos for each product.
"""

import os
import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('youtube_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == 'your_api_key_here':
    logger.error("Please set up your YouTube API key in the .env file")
    logger.info("1. Create a .env file based on .env.example")
    logger.info("2. Get an API key from Google Cloud Console")
    logger.info("3. Enable YouTube Data API v3 for your project")
    exit(1)

@dataclass
class VideoResult:
    """Container for YouTube video search results."""
    title: str
    video_id: str
    channel: str
    published_at: str
    duration: str = ""
    view_count: int = 0

class YouTubeSearcher:
    """Handles YouTube searches and result processing."""
    
    def __init__(self, api_key: str):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.quota_remaining = 10000  # Default quota, will be updated
    
    def search_videos(self, query: str, max_results: int = 3) -> List[VideoResult]:
        """Search YouTube for videos matching the query."""
        try:
            # First search for videos
            search_response = self.youtube.search().list(
                q=f"{query} sound demo",
                part='id,snippet',
                maxResults=max_results,
                type='video',
                videoDuration='medium',
                order='relevance',
                safeSearch='strict'
            ).execute()
            
            # Get video details for the found videos
            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            if not video_ids:
                return []
                
            # Get video details including duration and view count
            video_response = self.youtube.videos().list(
                part='contentDetails,statistics',
                id=','.join(video_ids)
            ).execute()
            
            # Process results
            videos = []
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']
                video_info = next(
                    (v for v in video_response.get('items', []) if v['id'] == video_id), 
                    None
                )
                
                if not video_info:
                    continue
                    
                # Parse duration (ISO 8601 format to MM:SS)
                duration = self._parse_duration(video_info['contentDetails']['duration'])
                
                videos.append(VideoResult(
                    title=item['snippet']['title'],
                    video_id=video_id,
                    channel=item['snippet']['channelTitle'],
                    published_at=item['snippet']['publishedAt'].split('T')[0],
                    duration=duration,
                    view_count=int(video_info['statistics'].get('viewCount', 0))
                ))
                
            return videos
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            if e.resp.status == 403 and 'quota' in str(e).lower():
                logger.error("YouTube API quota exceeded")
            return []
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    @staticmethod
    def _parse_duration(duration: str) -> str:
        """Convert ISO 8601 duration to MM:SS format."""
        # Remove 'PT' prefix
        duration = duration[2:]
        minutes = '0'
        seconds = '00'
        
        if 'M' in duration:
            minutes, duration = duration.split('M')
        if 'S' in duration:
            seconds = duration.split('S')[0].zfill(2)
            
        return f"{minutes}:{seconds}"


def get_products(db_path: str) -> List[Tuple[str, str]]:
    """Fetch all products from the database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, category FROM products")
        products = cursor.fetchall()
        return [(name, category) for name, category in products]
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


def generate_markdown(products: Dict[str, Dict[str, List[VideoResult]]]) -> str:
    """Generate markdown content from search results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    markdown = [
        "# Guitar Store - Sound Test Links",
        f"*Generated on: {timestamp}*\n"
    ]
    
    for category, category_products in products.items():
        markdown.append(f"## {category}\n")
        
        for product_name, videos in category_products.items():
            if not videos:
                continue
                
            markdown.append(f"### {product_name}\n")
            
            for i, video in enumerate(videos[:3], 1):
                markdown.append(
                    f"{i}. [{video.title}](https://youtu.be/{video.video_id}) - {video.channel}\n"
                    f"   - Duration: {video.duration} • Published: {video.published_at} • Views: {video.view_count:,}\n"
                )
            
            markdown.append("")
    
    return "\n".join(markdown)


def main():
    """Main function to execute the script."""
    # Initialize YouTube searcher
    searcher = YouTubeSearcher(YOUTUBE_API_KEY)
    
    # Get products from database
    db_path = os.path.join('instance', 'cart.db')
    products = get_products(db_path)
    
    if not products:
        logger.error("No products found in the database")
        return
    
    logger.info(f"Found {len(products)} products to process")
    
    # Organize products by category
    categories = {}
    for name, category in products:
        if category not in categories:
            categories[category] = []
        categories[category].append(name)
    
    # Search for videos
    results = {}
    for category, product_names in categories.items():
        results[category] = {}
        for product in product_names:
            logger.info(f"Searching for: {product}")
            videos = searcher.search_videos(product)
            results[category][product] = videos
    
    # Generate markdown
    markdown_content = generate_markdown(results)
    
    # Write to file
    output_file = 'sound_tests.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    logger.info(f"Successfully generated {output_file}")


if __name__ == "__main__":
    main()
