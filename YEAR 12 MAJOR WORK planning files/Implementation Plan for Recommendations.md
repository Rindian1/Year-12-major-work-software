## Implementation Plan for Recommendations Panel & Survey

### **Current Structure Analysis**
The application has:
- **Base template** with responsive navigation, search functionality, and notification system
- **Dashboard layout** with card-based design for shopping cart and recently viewed items
- **Authentication system** with login/register pages
- **Product grid** with hover effects and filtering
- **Existing notification system** for user feedback

### **1. Survey Implementation Plan**

#### **Location & Integration**
- **Primary placement**: Modify [register.html](cci:7://file:///Users/ryanbhandari/Documents/Year%2012%20major%20work%20software/templates/register.html:0:0-0:0) to include 4-question survey after account creation
- **Secondary placement**: Add survey modal to [index.html](cci:7://file:///Users/ryanbhandari/Documents/Year%2012%20major%20work%20software/templates/index.html:0:0-0:0) for existing users without survey data
- **Trigger**: Show survey immediately after successful registration or on first login if no survey exists

#### **Survey Form Structure**
```html
<!-- Add to register.html after password confirmation -->
<div class="survey-section">
    <h3>Help us recommend the perfect gear for you!</h3>
    
    <!-- Question 1: Skill Level -->
    <div class="form-group">
        <label>What's your guitar skill level?</label>
        <div class="radio-group">
            <label><input type="radio" name="skill_level" value="beginner"> Beginner</label>
            <label><input type="radio" name="skill_level" value="intermediate"> Intermediate</label>
            <label><input type="radio" name="skill_level" value="advanced"> Advanced</label>
            <label><input type="radio" name="skill_level" value="professional"> Professional</label>
        </div>
    </div>
    
    <!-- Question 2: Instrument Type -->
    <div class="form-group">
        <label>What type of guitar do you play?</label>
        <div class="radio-group">
            <label><input type="radio" name="instrument_type" value="acoustic"> Acoustic</label>
            <label><input type="radio" name="instrument_type" value="electric"> Electric</label>
            <label><input type="radio" name="instrument_type" value="both"> Both</label>
        </div>
    </div>
    
    <!-- Question 3: Preferred Genres -->
    <div class="form-group">
        <label>What music genres do you play? (Select all that apply)</label>
        <div class="checkbox-group">
            <label><input type="checkbox" name="preferred_genres" value="rock"> Rock</label>
            <label><input type="checkbox" name="preferred_genres" value="blues"> Blues</label>
            <label><input type="checkbox" name="preferred_genres" value="jazz"> Jazz</label>
            <!-- ... other genres -->
        </div>
    </div>
    
    <!-- Question 4: Budget Range -->
    <div class="form-group">
        <label>What's your typical budget range?</label>
        <select name="budget_range">
            <option value="under_500">Under $500</option>
            <option value="500_1000">$500 - $1,000</option>
            <!-- ... other ranges -->
        </select>
    </div>
</div>
```

#### **Backend Integration**
- **Extend registration route** to handle survey data
- **Create new database table** `user_surveys` with foreign key to users
- **Validate survey inputs** with same security patterns as existing forms
- **Store survey responses** and trigger initial recommendation generation

#### **Styling Integration**
- **Match existing card design** from [index.html](cci:7://file:///Users/ryanbhandari/Documents/Year%2012%20major%20work%20software/templates/index.html:0:0-0:0)
- **Use same color scheme** (#f67280, #b7374a) and border-radius (16px)
- **Implement responsive design** following existing mobile-first approach
- **Add progress indicator** for multi-step survey feel

### **2. Recommendations Panel Implementation Plan**

#### **Location & Integration**
- **Primary placement**: Add third card to [index.html](cci:7://file:///Users/ryanbhandari/Documents/Year%2012%20major%20work%20software/templates/index.html:0:0-0:0) dashboard between shopping cart and recently viewed
- **Secondary placement**: Add recommendations section to [search.html](cci:7://file:///Users/ryanbhandari/Documents/Year%2012%20major%20work%20software/templates/search.html:0:0-0:0) below sort options
- **Conditional display**: Only show for authenticated users with completed surveys

#### **Panel Structure**
```html
<!-- Add to index.html main.dashboard -->
<div class="card recommendations-card">
    <div class="card-header">
        <h2>Recommended for You</h2>
        <button class="refresh-btn" onclick="refreshRecommendations()">🔄</button>
    </div>
    
    <div class="loading-spinner" id="recommendationsLoading">
        <div class="spinner"></div>
        <p>Finding perfect matches...</p>
    </div>
    
    <div class="recommendations-grid" id="recommendationsGrid" style="display: none;">
        <!-- Products dynamically inserted here -->
    </div>
    
    <div class="recommendation-footer">
        <button class="view-all-btn" onclick="viewAllRecommendations()">View All</button>
        <button class="update-preferences-btn" onclick="updateSurvey()">Update Preferences</button>
    </div>
</div>
```

#### **Product Card Integration**
- **Reuse existing product card design** from [search.html](cci:7://file:///Users/ryanbhandari/Documents/Year%2012%20major%20work%20software/templates/search.html:0:0-0:0)
- **Add recommendation-specific elements**:
  - Match score percentage
  - "Recommended because" tooltip
  - Quick add-to-cart buttons
- **Maintain hover effects** and responsive grid layout

#### **JavaScript Integration**
- **Extend existing notification system** for recommendation feedback
- **Add AJAX calls** to fetch recommendations from `/api/recommendations/{user_id}`
- **Implement loading states** matching existing add-to-cart patterns
- **Add error handling** with fallback to recently viewed items

#### **Backend Integration**
- **Create new Flask route** `/api/recommendations/<int:user_id>`
- **Implement hybrid recommender** using existing ML algorithms
- **Cache recommendations** in Redis for performance
- **Update recommendations** when users interact with products

### **3. Database Schema Updates**

#### **New Tables Required**
```sql
-- User survey responses
CREATE TABLE user_surveys (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    skill_level VARCHAR(20),
    instrument_type VARCHAR(20),
    preferred_genres JSON,
    budget_range VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendation cache
CREATE TABLE recommendation_cache (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    score FLOAT,
    algorithm VARCHAR(50),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

#### **Existing Table Modifications**
- **Add recommendation tracking** to `product_interactions` table
- **Add survey completion flag** to `users` table
- **Create indexes** for performance optimization

### **4. CSS Styling Plan**

#### **New CSS Classes Needed**
```css
/* Survey-specific styles */
.survey-section { background: white; border-radius: 16px; padding: 25px; }
.radio-group, .checkbox-group { display: flex; flex-wrap: wrap; gap: 15px; }
.survey-progress { height: 4px; background: #f0f0f0; border-radius: 2px; }

/* Recommendations panel styles */
.recommendations-card { position: relative; min-height: 400px; }
.loading-spinner { text-align: center; padding: 40px; }
.recommendations-grid { display: grid; grid-template-columns: 1fr; gap: 20px; }
.match-score { background: #4caf50; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; }
.refresh-btn { background: none; border: none; cursor: pointer; font-size: 1.2rem; }
```

#### **Responsive Design**
- **Mobile**: Stack recommendations vertically, limit to 3 items
- **Tablet**: Show 2-column grid for recommendations
- **Desktop**: Full recommendations with hover effects

### **5. User Experience Flow**

#### **New User Journey**
1. **Register** → Complete survey → See initial recommendations
2. **Browse products** → Recommendations update based on views
3. **Purchase items** → Future recommendations refined

#### **Existing User Journey**
1. **Login** → Prompt to complete survey if missing
2. **Dashboard** → See personalized recommendations
3. **Update preferences** → Refresh recommendations instantly

### **6. Performance & Security Considerations**

#### **Performance**
- **Lazy load recommendations** after page load
- **Cache results for 1 hour** to reduce API calls
- **Implement pagination** for "View All" functionality
- **Optimize images** in recommendation cards

#### **Security**
Contradictory to the intuitive path of making sure the surey and inputs are as secure as possible, as later in the assignment i will need to create bugfixes to security problems, if the security is perfect, i will be unable to do anything. Therefore, leave a few vulnerabilities in the survey and input validation system, possibly in the form of unsanitised fields that can be exploited.