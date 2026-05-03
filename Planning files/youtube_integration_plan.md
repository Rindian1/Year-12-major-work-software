# YouTube Integration Plan for Product Details

## Overview
This document outlines the strategy for integrating YouTube sound test links into the product details page of the guitar store.

## Current State Analysis
- We have successfully generated `sound_tests.md` containing 3 YouTube links per product
- The `product_detail.html` template currently has 5 placeholder YouTube links
- We need to map the generated YouTube links to the appropriate products

## Data Flow

### 1. Database Schema Update
- **Table**: `products`
- **New Column**: `youtube_links` (TEXT/JSON)
  - Store as JSON array of video objects:
    ```json
    [
      {
        "url": "https://youtube.com/...",
        "title": "Video Title",
        "channel": "Channel Name",
        "duration": "5:30",
        "views": 12345,
        "published": "2023-01-01"
      },
      ...
    ]
    ```

### 2. Update Process
1. **Script to Update Database**
   - Read from `sound_tests.md`
   - Parse product names and their associated YouTube links
   - Update the `products` table with the YouTube links

2. **Backend Changes**
   - Modify the product detail route to include YouTube links in the template context
   - Add error handling for missing YouTube links

3. **Frontend Changes**
   - Update `product_detail.html` to display the YouTube links
   - Implement responsive video embedding
   - Add loading states and error handling

## Implementation Steps

### Phase 1: Database Update
1. Create database migration script
   ```python
   # Example migration
   def upgrade():
       op.add_column('products', sa.Column('youtube_links', sa.Text(), nullable=True))
   ```

2. Create script to populate YouTube links
   - Read from `sound_tests.md`
   - Match products by name
   - Update database with JSON-encoded video data

### Phase 2: Backend Updates
1. Update product model
   ```python
   class Product(db.Model):
       # ... existing fields ...
       youtube_links = db.Column(db.Text)  # JSON-encoded list of video objects
   
       @property
       def youtube_videos(self):
           if self.youtube_links:
               return json.loads(self.youtube_links)
           return []
   ```

2. Update view function
   ```python
   @app.route('/product/<int:product_id>')
   def product_detail(product_id):
       product = Product.query.get_or_404(product_id)
       return render_template('product_detail.html', product=product)
   ```

### Phase 3: Frontend Updates
1. Update `product_detail.html`
   ```html
   <div class="youtube-videos">
       <h3>Sound Demos</h3>
       <div class="video-grid">
           {% for video in product.youtube_videos %}
           <div class="video-item">
               <iframe 
                   width="300" 
                   height="169" 
                   src="https://www.youtube.com/embed/{{ video.url|extract_youtube_id }}" 
                   frameborder="0" 
                   allowfullscreen>
               </iframe>
               <div class="video-info">
                   <a href="{{ video.url }}" target="_blank">{{ video.title }}</a>
                   <div class="video-meta">
                       <span>{{ video.channel }}</span>
                       <span>{{ video.views|number_format }} views</span>
                       <span>{{ video.published|time_ago }}</span>
                   </div>
               </div>
           </div>
           {% endfor %}
       </div>
   </div>
   ```

2. Add CSS for responsive video grid
   ```css
   .video-grid {
       display: grid;
       grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
       gap: 20px;
       margin-top: 20px;
   }
   
   .video-item {
       background: #fff;
       border-radius: 8px;
       overflow: hidden;
       box-shadow: 0 2px 4px rgba(0,0,0,0.1);
   }
   
   .video-item iframe {
       width: 100%;
       aspect-ratio: 16/9;
   }
   
   .video-info {
       padding: 12px;
   }
   
   .video-meta {
       font-size: 0.8em;
       color: #666;
       margin-top: 8px;
   }
   ```

## Testing Plan
1. Unit tests for database operations
2. Integration tests for the product detail endpoint
3. UI tests for video display and interaction
4. Cross-browser testing
5. Mobile responsiveness testing

## Deployment Strategy
1. Deploy database migration
2. Run script to populate YouTube links
3. Deploy backend changes
4. Deploy frontend changes
5. Verify functionality in staging before production

## Future Enhancements
1. Lazy loading for better performance
2. Video thumbnail previews
3. Video categories (e.g., "Clean Tone", "High Gain")
4. User-submitted demos
5. Video rating and feedback system

## Rollback Plan
1. Revert frontend changes
2. Rollback database migration if needed
3. Disable YouTube section via feature flag if issues arise
