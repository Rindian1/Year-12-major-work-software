# AI Prompt: Create Comprehensive Machine Learning Implementation Guide

## Task Overview

You are to create a comprehensive markdown document that provides exact and specific instructions for implementing a K-Nearest Neighbors (KNN) machine learning recommendation system for a Flask-based guitar e-commerce application. The document should NOT provide exact code, but should give detailed, step-by-step instructions on what needs to be done.

## Project Context

### Application Summary
This is a Flask-based e-commerce application for selling guitars, amplifiers, effects pedals, and accessories. The application currently has:
- User authentication (registration, login, logout)
- Product browsing and search
- Shopping cart functionality
- A basic survey system that collects user preferences
- A simple recommendation system based on survey responses

The goal is to replace the simple recommendation system with a sophisticated KNN-based machine learning recommendation system that provides personalized product recommendations based on:
1. User survey responses (skill level, instrument type, preferred genres)
2. User-product interaction history (views, likes, add-to-cart, purchases)
3. Collaborative filtering (similar users' behavior)
4. Content-based filtering (product attribute similarities)

### Project Directory Structure

```
/Users/ryanbhandari/Documents/Year 12 major work software/
├── .env.example
├── .gitignore
├── .venv/ (virtual environment)
├── instance/
│   └── cart.db (SQLite database)
├── migrations/
│   ├── 001_add_youtube_links.py
│   ├── 002_populate_youtube_links.py
│   ├── 003_create_survey_tables.py
│   ├── 003_create_survey_tables_fixed.py
│   ├── 004_seed_ml_data.py (seeds 100 users, 50 products, 364+ interactions)
│   ├── 005_expand_ml_data.py
│   └── 006_seed_more_surveys.py
├── static/
│   ├── Images/ (product images)
│   └── style.css
├── templates/
│   ├── base.html
│   ├── index.html (dashboard with recommendations panel)
│   ├── login.html
│   ├── product_detail.html
│   ├── register.html
│   ├── search.html
│   ├── shopping_cart.html
│   ├── style.md
│   └── survey.html (4-question guitar survey)
├── app.py (main Flask application - 1023 lines)
├── requirements.txt
├── requirements-youtube.txt
├── README.md
├── youtube_search.py
└── YEAR 12 MAJOR WORK planning files/
    ├── Implementation Plan for Recommendations.md
    ├── machine-learning-implementation.md (existing ML planning document)
    └── task-description.md
```

### Current Implementation Status

**Already Implemented:**
1. Database tables for ML functionality:
   - `user_surveys` - stores user survey responses (skill_level, instrument_type, preferred_genres)
   - `recommendation_cache` - caches ML recommendations with expiration
   - `product_interactions` - tracks user-product interactions (action, timestamp, duration, frequency)
   - `products` table has guitar-specific columns: skill_level, genre_suitability, instrument_type, price_range

2. API endpoints in app.py:
   - `POST /api/user/survey` - handles survey submission with validation
   - `GET /api/recommendations/<user_id>` - returns recommendations (currently uses simple algorithm)
   - `GET /survey` - survey page for updating preferences

3. Frontend components:
   - Survey page with 3 questions
   - Recommendations panel on dashboard
   - Survey integrated into registration flow

4. Data seeding:
   - 100 user profiles with diverse survey data
   - 50 products with guitar-specific attributes
   - 364+ user interactions for ML training

**Current Recommendation Algorithm:**
The current system uses a simple content-based filtering approach:
- Filters products by instrument type and skill level
- Scores based on genre compatibility
- Returns random products matching criteria
- Caches results for 24 hours

**What Needs to be Implemented:**
Replace the simple algorithm with a sophisticated KNN-based system that:
- Uses user-user collaborative filtering
- Uses item-item collaborative filtering
- Uses content-based filtering
- Combines all three approaches with weighted scoring
- Provides explainable recommendations
- Handles cold-start problems
- Scales with the dataset

## Database Schema

### Tables Relevant to ML Implementation

#### 1. users table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
```

#### 2. products table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    description TEXT,
    image_url TEXT,
    -- Guitar-specific columns added by migration:
    skill_level VARCHAR(20),
    genre_suitability TEXT,  -- JSON array of genres
    instrument_type VARCHAR(20),
    price_range VARCHAR(20)
)
```

#### 3. user_surveys table
```sql
CREATE TABLE user_surveys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skill_level VARCHAR(20) NOT NULL,
    instrument_type VARCHAR(20) NOT NULL,
    preferred_genres TEXT NOT NULL,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

#### 4. recommendation_cache table
```sql
CREATE TABLE recommendation_cache (
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
```

#### 5. product_interactions table
```sql
CREATE TABLE product_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration INTEGER DEFAULT 0,
    frequency INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
)
```

### Valid Values for Fields

**skill_level:** 'beginner', 'intermediate', 'advanced', 'professional'

**instrument_type:** 'acoustic', 'electric', 'both'

**preferred_genres:** Array containing any of: 'rock', 'blues', 'jazz', 'classical', 'metal', 'pop', 'country', 'folk', 'indie'


**category:** 'guitars', 'amplifiers', 'effects', 'accessories'

**action (in product_interactions):** 'view', 'like', 'add_to_cart', 'purchase', 'compare'

## Existing ML Implementation Document

There is an existing document at `YEAR 12 MAJOR WORK planning files/machine-learning-implementation.md` that contains:
- A detailed KNN implementation with code examples
- Data requirements and sample data
- Database schema design
- Flask integration examples
- Frontend implementation examples
- Security considerations
- Performance optimization strategies
- Testing strategies
- Implementation status tracking

**Important:** This document already contains a complete KNN implementation with actual code. Your task is NOT to reproduce this code, but to create a new document that provides step-by-step INSTRUCTIONS on how to implement the system, without providing the actual code.

## What Your Document Should Include

Your document should be structured as follows:

### 1. Executive Summary
- Brief overview of what the ML system will do
- Why KNN is the chosen approach
- Expected benefits over the current simple system

### 2. Prerequisites and Dependencies
- List all required Python packages (scikit-learn, pandas, numpy, etc.)
- Instructions for adding them to requirements.txt
- Any system requirements

### 3. Architecture Overview
- High-level architecture diagram (described in text)
- How the KNN system integrates with the existing Flask app
- Data flow from user interaction to recommendation

### 4. Implementation Steps

#### Step 1: Create ML Module Structure
- Instructions on where to create new Python files (e.g., create a `ml_recommender.py` file in the project root)
- What classes and functions need to be created
- How to organize the code (separation of concerns)

#### Step 2: Data Loading and Preprocessing
- Instructions on how to load data from SQLite database
- How to query user_surveys, products, and product_interactions tables
- How to handle missing data
- How to encode categorical variables (skill level, instrument type, genres)
- How to create user-product interaction matrices
- How to scale/normalize features

#### Step 3: Feature Engineering
- Instructions on encoding user survey features into numerical vectors
- Instructions on encoding product features into numerical vectors
- How to handle genre preferences (one-hot encoding)
- How to handle categorical variables (skill level, instrument type)
- How to incorporate popularity scores

#### Step 4: KNN Model Implementation
- Instructions on implementing user-user collaborative filtering
- Instructions on implementing item-item collaborative filtering
- Instructions on implementing content-based filtering
- How to choose distance metrics (cosine, euclidean, etc.)
- How to determine optimal k (number of neighbors)
- How to weight different recommendation sources

#### Step 5: Training the Model
- Instructions on when to train the model (on startup, on schedule, on demand)
- How to handle model persistence (save/load trained models)
- How to handle incremental updates when new data arrives
- How to handle cold-start problems (new users with no interaction history)

#### Step 6: Generating Recommendations
- Instructions on the recommendation generation process
- How to combine user-based, item-based, and content-based filtering
- How to apply weighting to different recommendation sources
- How to filter out already-interacted products
- How to generate human-readable recommendation reasons
- How to normalize and rank final recommendations

#### Step 7: Integration with Flask App
- Instructions on modifying the existing `get_recommendations()` endpoint in app.py
- How to instantiate and use the KNN recommender
- How to handle errors gracefully
- How to update the recommendation caching logic
- How to trigger model retraining

#### Step 8: Frontend Integration
- Instructions on updating the recommendations panel in templates/index.html
- How to display match scores
- How to display recommendation reasons
- How to handle loading states
- How to refresh recommendations

#### Step 9: Testing and Validation
- Instructions on unit testing the ML module
- Instructions on integration testing with the Flask app
- How to validate recommendation quality
- How to measure performance metrics
- How to test edge cases (new users, no interactions, etc.)

#### Step 10: Performance Optimization
- Instructions on implementing caching strategies
- How to optimize database queries
- How to handle large datasets efficiently
- When to use batch processing
- How to monitor system performance

### 5. Configuration and Tuning
- Instructions on configuring KNN parameters (n_neighbors, metric, weights)
- How to tune hyperparameters
- How to A/B test different configurations
- How to monitor recommendation accuracy over time

### 6. Security Considerations
- Instructions on validating user input
- How to prevent SQL injection in ML queries
- How to handle user privacy
- How to secure model data

### 7. Deployment Considerations
- Instructions on deploying the ML system
- How to handle model versioning
- How to rollback if issues occur
- How to monitor system health in production

### 8. Troubleshooting Guide
- Common issues and how to resolve them
- How to debug recommendation quality issues
- How to handle database connection errors
- How to handle memory issues with large datasets

### 9. Success Metrics
- How to measure recommendation accuracy
- How to measure user engagement with recommendations
- How to measure click-through rates
- How to measure conversion rates

## Important Guidelines

1. **Do NOT provide exact code** - Provide detailed instructions on what to do, but not the actual implementation
2. **Be specific** - Don't say "implement a function", say "create a function that takes X as input and returns Y, handling Z edge cases"
3. **Reference existing code** - Point to specific lines in app.py or migration files where integration is needed
4. **Use concrete examples** - Use actual field names, table names, and valid values from the schema
5. **Consider edge cases** - Address what happens with new users, missing data, empty results, etc.
6. **Provide rationale** - Explain WHY certain approaches are recommended
7. **Include file paths** - Specify exactly where new files should be created and existing files should be modified
8. **Reference existing data** - Mention the seeded data (100 users, 50 products, 364+ interactions) that can be used for testing

## Output Format

Your output should be a single markdown file saved as:
`YEAR 12 MAJOR WORK planning files/ML_IMPLEMENTATION_GUIDE.md`

The document should be well-structured with clear headings, numbered steps, and bullet points. It should be comprehensive enough that a developer could follow it step-by-step to implement the entire KNN recommendation system without needing additional guidance.

## Additional Context

- The application currently runs on port 5006 (changed from 5001)
- The database is SQLite located at `instance/cart.db`
- The app uses Flask-Login for authentication
- The survey is already integrated into the registration flow
- There is already a recommendations panel on the dashboard that needs to be updated
- The existing simple recommendation algorithm is in the `generate_simple_recommendations()` function in app.py (lines 966-1020)

Your task is to create a comprehensive implementation guide that replaces this simple algorithm with a sophisticated KNN-based system.
