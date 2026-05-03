# YouTube Sound Test Integration Plan

## Overview
This document outlines the plan to automatically generate sound test links for products in the guitar store by integrating with the YouTube Data API.

## Prerequisites
1. Google Cloud Project with YouTube Data API v3 enabled
2. API key for YouTube Data API v3
3. Python environment with required packages

## Implementation Steps

### 1. Database Analysis
- [ ] Analyze the `products` table structure in `cart.db`
- [ ] Identify relevant fields (product name, category, etc.)
- [ ] Document any special cases or edge cases

### 2. YouTube API Setup
- [ ] Create a new project in Google Cloud Console
- [ ] Enable YouTube Data API v3
- [ ] Generate API credentials (API key)
- [ ] Set up API key storage (environment variable or config file)

### 3. Python Script Development
- [ ] Create `youtube_search.py` with the following components:
  - [ ] Database connection function
  - [ ] YouTube API search function
  - [ ] Result processing and formatting
  - [ ] Error handling and rate limiting
  - [ ] Markdown generation

### 4. Search Logic
- [ ] For each product:
  - [ ] Construct search query (e.g., "Fender Stratocaster sound demo")
  - [ ] Filter for relevant video content (e.g., duration, quality, channel reputation)
  - [ ] Extract video title, URL, and channel information
  - [ ] Store top 3 results

### 5. Output Format
- [ ] Generate organized markdown output:
  ```markdown
  ## [Category]
  ### [Product Name]
  1. [Video Title](URL) - [Channel Name]
     - Duration: XX:XX
     - Published: YYYY-MM-DD
     - View count: X,XXX,XXX
  ```

### 6. Error Handling
- [ ] Handle API quota limits
- [ ] Handle missing or no results
- [ ] Log errors and warnings
- [ ] Implement retry mechanism for failed requests

### 7. Testing
- [ ] Test with sample product list
- [ ] Verify video relevance
- [ ] Check for any content restrictions or age-gated videos
- [ ] Test error scenarios

### 8. Documentation
- [ ] Document API key setup
- [ ] Add usage instructions
- [ ] Include example output

## Dependencies
- Python 3.8+
- google-api-python-client
- python-dotenv (for environment variables)
- sqlite3 (built-in)

## Future Enhancements
- Cache search results to reduce API calls
- Add support for multiple search terms per product
- Include video thumbnails in the output
- Add command-line arguments for customization
- Create a web interface for manual review and selection
