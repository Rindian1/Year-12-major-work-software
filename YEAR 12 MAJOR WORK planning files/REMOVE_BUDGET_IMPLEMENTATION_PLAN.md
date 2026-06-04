# Implementation Plan: Remove Budget from ML Model and Remove % Match Indicator

## Overview

This document outlines the steps required to:
1. Remove the budget aspect from the machine learning recommendation system
2. Remove the budget question from the user survey
3. Handle budget data in the database (delete or ignore)
4. Retrain and edit the KNN model to exclude budget from decision making
5. Remove the % match indicator from recommendations

## Current Budget Usage Locations

### Frontend
- **templates/survey.html** (lines 182-193): Budget question form field
- **templates/survey.html** (lines 253-255): Budget progress tracking
- **templates/survey.html** (lines 285, 288, 298): Budget validation in JavaScript
- **templates/survey.html** (lines 749-751): Budget progress tracking in base.html
- **templates/base.html** (line 609): % Match indicator display

### Backend (app.py)
- **Line 865**: budget_range in survey_data dictionary
- **Line 882**: budget_range in required_fields validation
- **Line 890**: valid_budget_ranges array
- **Lines 899-900**: budget_range validation
- **Line 920**: budget_range in UPDATE SQL
- **Line 923**: budget_range parameter in UPDATE
- **Line 927**: budget_range in INSERT SQL
- **Line 930**: budget_range parameter in INSERT
- **Line 1001**: budget_range in survey_data for simple recommendations
- **Lines 1049-1058**: Budget filtering in simple recommendations

### ML Data Layer (ml/data_loader.py)
- **Line 40**: budget_range in SQL SELECT for load_users_with_surveys
- **Line 112**: budget_range in SQL SELECT for get_user_survey
- **Line 127**: budget_range in returned dictionary

### ML Feature Engineering (ml/feature_engineering.py)
- **Lines 25-31**: BUDGET_ORDER dictionary
- **Lines 46-50**: _budget_value function
- **Line 89**: Comment mentioning budget in encode_user_survey_row
- **Line 102**: _budget_value call in encode_user_survey_row
- **Line 116**: _budget_value call in encode_product_row
- **Line 35**: SURVEY_DIM calculation (includes budget)
- **Line 36**: PRODUCT_DIM calculation (includes budget)

### ML Models (ml/knn_models.py)
- **Lines 31-51**: _budget_price_compat function
- **Lines 107-111**: _budget_value_static function
- **Lines 158-161**: _budget_price_compat call in ContentBasedRecommender
- **Line 168**: _budget_value_static call in ContentBasedRecommender
- **Line 179**: Budget score in content-based scoring (0.18 * bud)
- **Line 182**: Reason mentioning budget
- **Line 186**: Reason mentioning budget

### Database Schema
- **user_surveys table**: budget_range VARCHAR(20) column
- **products table**: price_range VARCHAR(20) column (used for budget compatibility)

### Migration Files
- **migrations/003_create_survey_tables.py**: budget_range column definition
- **migrations/003_create_survey_tables_fixed.py**: budget_range column definition

### Seed Data Files
- **migrations/004_seed_ml_data.py**: budget_range in user survey data
- **migrations/005_expand_ml_data.py**: budget_range in user survey data
- **migrations/006_seed_more_surveys.py**: budget_range in user survey data

### Test Files
- **tests/test_ml_recommender.py**: budget_range in test data

## Implementation Steps

### Step 1: Remove Budget from Survey Frontend

**File: templates/survey.html**

**Actions:**
1. Remove Question 4 (lines 182-193):
   - Delete the entire budget range form group:
   ```html
   <!-- Question 4: Budget Range -->
   <div class="form-group survey-question">
       <label class="survey-label">What's your typical budget range?</label>
       <select name="budget_range" class="survey-select" required>
           <option value="">Select your budget range</option>
           <option value="under_500" {% if survey_data and survey_data.budget_range == 'under_500' %}selected{% endif %}>Under $500</option>
           <option value="500_1000" {% if survey_data and survey_data.budget_range == '500_1000' %}selected{% endif %}>$500 - $1,000</option>
           <option value="1000_2000" {% if survey_data and survey_data.budget_range == '1000_2000' %}selected{% endif %}>$1,000 - $2,000</option>
           <option value="2000_5000" {% if survey_data and survey_data.budget_range == '2000_5000' %}selected{% endif %}>$2,000 - $5,000</option>
           <option value="over_5000" {% if survey_data and survey_data.budget_range == 'over_5000' %}selected{% endif %}>Over $5,000</option>
       </select>
   </div>
   ```

2. Update progress tracking (line 238):
   - Change `const totalQuestions = 4;` to `const totalQuestions = 3;`

3. Remove budget progress check (lines 253-255):
   - Delete:
   ```javascript
   // Check budget range
   const budgetRange = surveyForm.querySelector('select[name="budget_range"]');
   if (budgetRange && budgetRange.value) answeredQuestions++;
   ```

4. Update survey_data pre-fill (line 865):
   - Remove `'budget_range': existing_survey['budget_range']` from the dictionary

5. Update JavaScript validation (lines 285, 288, 298):
   - Remove `budgetRange` from validation
   - Remove budget_range from required fields check
   - Remove budget_range from surveyData object

**File: templates/base.html**

**Actions:**
1. Update progress tracking (line 734):
   - Change `const totalQuestions = 4;` to `const totalQuestions = 3;`

2. Remove budget progress check (lines 749-751):
   - Delete:
   ```javascript
   // Check budget range
   const budgetRange = surveyForm.querySelector('select[name="budget_range"]');
   if (budgetRange && budgetRange.value) answeredQuestions++;
   ```

3. Remove % match indicator (line 609):
   - Delete the entire line:
   ```html
   <div class="match-score">${Math.round((Number(product.score) || 0) * 100)}% Match</div>
   ```

### Step 2: Remove Budget from Backend Validation

**File: app.py**

**Actions:**
1. Remove budget_range from required_fields (line 882):
   - Change from:
   ```python
   required_fields = ['skill_level', 'instrument_type', 'preferred_genres', 'budget_range']
   ```
   - To:
   ```python
   required_fields = ['skill_level', 'instrument_type', 'preferred_genres']
   ```

2. Remove valid_budget_ranges array (line 890):
   - Delete the entire line:
   ```python
   valid_budget_ranges = ['under_500', '500_1000', '1000_2000', '2000_5000', 'over_5000']
   ```

3. Remove budget_range validation (lines 899-900):
   - Delete:
   ```python
   if data['budget_range'] not in valid_budget_ranges:
       return jsonify({'success': False, 'error': 'Invalid budget range'}), 400
   ```

4. Remove budget_range from UPDATE SQL (line 920):
   - Change from:
   ```python
   UPDATE user_surveys 
   SET skill_level = ?, instrument_type = ?, preferred_genres = ?, budget_range = ?, updated_at = CURRENT_TIMESTAMP
   WHERE user_id = ?
   ```
   - To:
   ```python
   UPDATE user_surveys 
   SET skill_level = ?, instrument_type = ?, preferred_genres = ?, updated_at = CURRENT_TIMESTAMP
   WHERE user_id = ?
   ```

5. Remove budget_range parameter from UPDATE (line 923):
   - Change from:
   ```python
   (data['skill_level'], data['instrument_type'], json.dumps(data['preferred_genres']), 
    data['budget_range'], current_user.id)
   ```
   - To:
   ```python
   (data['skill_level'], data['instrument_type'], json.dumps(data['preferred_genres']), 
    current_user.id)
   ```

6. Remove budget_range from INSERT SQL (line 927):
   - Change from:
   ```python
   INSERT INTO user_surveys (user_id, skill_level, instrument_type, preferred_genres, budget_range)
   VALUES (?, ?, ?, ?, ?)
   ```
   - To:
   ```python
   INSERT INTO user_surveys (user_id, skill_level, instrument_type, preferred_genres)
   VALUES (?, ?, ?, ?)
   ```

7. Remove budget_range parameter from INSERT (line 930):
   - Change from:
   ```python
   (current_user.id, data['skill_level'], data['instrument_type'], 
    json.dumps(data['preferred_genres']), data['budget_range'])
   ```
   - To:
   ```python
   (current_user.id, data['skill_level'], data['instrument_type'], 
    json.dumps(data['preferred_genres']))
   ```

8. Remove budget_range from survey_data (line 1001):
   - Change from:
   ```python
   survey_data = {
       "skill_level": user_survey["skill_level"],
       "instrument_type": user_survey["instrument_type"],
       "preferred_genres": json.loads(user_survey["preferred_genres"]),
       "budget_range": user_survey["budget_range"],
   }
   ```
   - To:
   ```python
   survey_data = {
       "skill_level": user_survey["skill_level"],
       "instrument_type": user_survey["instrument_type"],
       "preferred_genres": json.loads(user_survey["preferred_genres"]),
   }
   ```

9. Remove budget filtering from simple recommendations (lines 1049-1058):
   - Delete the entire budget filtering block:
   ```python
   # Add budget filter
   if survey_data['budget_range'] == 'under_500':
       query += ' AND price < 500'
   elif survey_data['budget_range'] == '500_1000':
       query += ' AND price >= 500 AND price <= 1000'
   elif survey_data['budget_range'] == '1000_2000':
       query += ' AND price >= 1000 AND price <= 2000'
   elif survey_data['budget_range'] == '2000_5000':
       query += ' AND price >= 2000 AND price <= 5000'
   elif survey_data['budget_range'] == 'over_5000':
       query += ' AND price > 5000'
   ```

10. Remove budget_range from survey_data pre-fill (line 865):
    - Change from:
    ```python
    survey_data = {
        'skill_level': existing_survey['skill_level'],
        'instrument_type': existing_survey['instrument_type'],
        'preferred_genres': json.loads(existing_survey['preferred_genres']),
        'budget_range': existing_survey['budget_range']
    }
    ```
    - To:
    ```python
    survey_data = {
        'skill_level': existing_survey['skill_level'],
        'instrument_type': existing_survey['instrument_type'],
        'preferred_genres': json.loads(existing_survey['preferred_genres'])
    }
    ```

### Step 3: Remove Budget from ML Data Layer

**File: ml/data_loader.py**

**Actions:**
1. Remove budget_range from load_users_with_surveys SQL (line 40):
   - Change from:
   ```python
   SELECT u.id AS user_id, us.skill_level, us.instrument_type,
          us.preferred_genres, us.budget_range
   FROM users u
   INNER JOIN user_surveys us ON u.id = us.user_id
   ```
   - To:
   ```python
   SELECT u.id AS user_id, us.skill_level, us.instrument_type,
          us.preferred_genres
   FROM users u
   INNER JOIN user_surveys us ON u.id = us.user_id
   ```

2. Remove budget_range from get_user_survey SQL (line 112):
   - Change from:
   ```python
   SELECT skill_level, instrument_type, preferred_genres, budget_range
   FROM user_surveys WHERE user_id = ?
   ```
   - To:
   ```python
   SELECT skill_level, instrument_type, preferred_genres
   FROM user_surveys WHERE user_id = ?
   ```

3. Remove budget_range from returned dictionary (line 127):
   - Change from:
   ```python
   return {
       "skill_level": row["skill_level"],
       "instrument_type": row["instrument_type"],
       "preferred_genres": genres,
       "budget_range": row["budget_range"],
   }
   ```
   - To:
   ```python
   return {
       "skill_level": row["skill_level"],
       "instrument_type": row["instrument_type"],
       "preferred_genres": genres,
   }
   ```

### Step 4: Remove Budget from ML Feature Engineering

**File: ml/feature_engineering.py**

**Actions:**
1. Remove BUDGET_ORDER dictionary (lines 25-31):
   - Delete the entire dictionary:
   ```python
   BUDGET_ORDER = {
       "under_500": 0,
       "500_1000": 1,
       "1000_2000": 2,
       "2000_5000": 3,
       "over_5000": 4,
   }
   ```

2. Remove _budget_value function (lines 46-50):
   - Delete the entire function:
   ```python
   def _budget_value(budget: str | None) -> float:
       if not budget:
           return 0.5
       v = BUDGET_ORDER.get(str(budget).lower(), 2)
       return v / 4.0
   ```

3. Update SURVEY_DIM calculation (line 35):
   - Change from:
   ```python
   SURVEY_DIM = 1 + 3 + 9 + 1  # 14 — user survey has no category
   ```
   - To:
   ```python
   SURVEY_DIM = 1 + 3 + 9  # 13 — user survey has no category, no budget
   ```

4. Update PRODUCT_DIM calculation (line 36):
   - Change from:
   ```python
   PRODUCT_DIM = 1 + 3 + 9 + 1 + 4  # 18
   ```
   - To:
   ```python
   PRODUCT_DIM = 1 + 3 + 9 + 4  # 17 — no budget
   ```

5. Update vector layout comment (line 34):
   - Change from:
   ```python
   # Vector layout: skill(1) + instrument(3) + genres(9) + budget(1) + category(4) = 18
   ```
   - To:
   ```python
   # Vector layout: skill(1) + instrument(3) + genres(9) + category(4) = 17
   ```

6. Update encode_user_survey_row comment (line 89):
   - Change from:
   ```python
   """14-dim vector: skill, instrument one-hot, genre one-hot, budget."""
   ```
   - To:
   ```python
   """13-dim vector: skill, instrument one-hot, genre one-hot."""
   ```

7. Remove _budget_value call from encode_user_survey_row (line 102):
   - Change from:
   ```python
   parts = [
       np.array([_skill_value(row.get("skill_level"))]),
       _instrument_onehot(row.get("instrument_type")),
       _genre_onehot(genres),
       np.array([_budget_value(row.get("budget_range"))]),
   ]
   ```
   - To:
   ```python
   parts = [
       np.array([_skill_value(row.get("skill_level"))]),
       _instrument_onehot(row.get("instrument_type")),
       _genre_onehot(genres),
   ]
   ```

8. Remove _budget_value call from encode_product_row (line 116):
   - Change from:
   ```python
   parts = [
       np.array([_skill_value(row.get("skill_level"))]),
       _instrument_onehot(row.get("instrument_type")),
       _genre_onehot(genres),
       np.array([_budget_value(row.get("price_range"))]),
       _category_onehot(row.get("category")),
   ]
   ```
   - To:
   ```python
   parts = [
       np.array([_skill_value(row.get("skill_level"))]),
       _instrument_onehot(row.get("instrument_type")),
       _genre_onehot(genres),
       _category_onehot(row.get("category")),
   ]
   ```

### Step 5: Remove Budget from ML Models

**File: ml/knn_models.py**

**Actions:**
1. Remove _budget_price_compat function (lines 31-51):
   - Delete the entire function:
   ```python
   def _budget_price_compat(budget: str, price: float) -> float:
       price = float(price or 0)
       if budget == "under_500":
           lo, hi = 0.0, 500.0
       elif budget == "500_1000":
           lo, hi = 500.0, 1000.0
       elif budget == "1000_2000":
           lo, hi = 1000.0, 2000.0
       elif budget == "2000_5000":
           lo, hi = 2000.0, 5000.0
       elif budget == "over_5000":
           lo, hi = 5000.0, 1e9
       else:
           return 0.7
       if lo <= price <= hi:
           return 1.0
       mid = (lo + hi) / 2
       dist = min(abs(price - lo), abs(price - hi), abs(price - mid))
       band = hi - lo if hi > lo else 500.0
       return max(0.35, 1.0 - min(dist / (band + 1e-9), 0.65))
   ```

2. Remove _budget_value_static function (lines 107-111):
   - Delete the entire function:
   ```python
   def _budget_value_static(budget: str | None) -> float:
       from ml.feature_engineering import BUDGET_ORDER

       v = BUDGET_ORDER.get(str(budget or "").lower(), 2)
       return v / 4.0
   ```

3. Remove _budget_price_compat call from ContentBasedRecommender (lines 158-161):
   - Delete:
   ```python
   bud = _budget_price_compat(
       user_survey.get("budget_range") or "",
       float(row.get("price") or 0),
   )
   ```

4. Remove _budget_value_static call from ContentBasedRecommender (line 168):
   - Change from:
   ```python
   p_vec = np.concatenate(
       [
           np.array([_skill_value_static(row.get("skill_level"))]),
           _instrument_oh_static(row.get("instrument_type")),
           _genre_oh_from_set(p_genres),
           np.array([_budget_value_static(row.get("price_range"))]),
       ]
   )
   ```
   - To:
   ```python
   p_vec = np.concatenate(
       [
           np.array([_skill_value_static(row.get("skill_level"))]),
           _instrument_oh_static(row.get("instrument_type")),
           _genre_oh_from_set(p_genres),
       ]
   )
   ```

5. Remove budget from scoring formula (line 179):
   - Change from:
   ```python
   score = (
       0.32 * overlap
       + 0.22 * inst
       + 0.18 * sk
       + 0.18 * bud
       + 0.10 * max(0.0, min(1.0, cos))
   )
   ```
   - To (redistribute budget weight to other factors):
   ```python
   score = (
       0.39 * overlap  # increased from 0.32
       + 0.27 * inst  # increased from 0.22
       + 0.22 * sk    # increased from 0.18
       + 0.12 * max(0.0, min(1.0, cos))  # increased from 0.10
   )
   ```

6. Update reason strings (lines 182, 186):
   - Change from:
   ```python
   reason = "Matches your genres, skill level, and budget"
   if overlap >= 0.5:
       reason = "Strong genre match for your preferences"
   elif inst >= 0.99:
       reason = "Fits your instrument type and budget"
   ```
   - To:
   ```python
   reason = "Matches your genres, skill level, and instrument type"
   if overlap >= 0.5:
       reason = "Strong genre match for your preferences"
   elif inst >= 0.99:
       reason = "Fits your instrument type perfectly"
   ```

### Step 6: Database Schema Changes

**Option A: Delete budget_range column (Recommended)**

Create a new migration file: `migrations/007_remove_budget_from_surveys.py`

```python
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
```

**Option B: Ignore budget_range column (Alternative)**

If you prefer to keep the column in the database but ignore it in the application, skip the migration step. The existing data will remain but won't be used by the ML model.

### Step 7: Update Seed Data (Optional)

If you want to regenerate seed data without budget:

**File: migrations/004_seed_ml_data.py**

Remove budget_range from all user survey data entries.

**File: migrations/005_expand_ml_data.py**

Remove budget_range from all user survey data entries.

**File: migrations/006_seed_more_surveys.py**

Remove budget_range from all user survey data entries.

Alternatively, you can leave these files as-is and just not use the budget data.

### Step 8: Update Tests

**File: tests/test_ml_recommender.py**

Remove budget_range from test data and update test expectations.

### Step 9: Retrain ML Model

After making all code changes, the ML model will automatically retrain when:

1. The application restarts
2. A user updates their survey
3. The recommendation cache is cleared

To force immediate retraining:

1. Clear the recommendation cache:
   ```python
   DELETE FROM recommendation_cache
   ```

2. Restart the Flask application

3. The HybridRecommender will call `refresh()` on first access, which will:
   - Load user data (without budget)
   - Load product data
   - Build feature vectors (13-dim for users, 17-dim for products)
   - Train KNN models with new dimensions
   - Store in memory

### Step 10: Update Documentation

**File: YEAR 12 MAJOR WORK planning files/KNN_MODEL_EXPLANATION.md**

Update the document to reflect:
- User survey vector is now 13 dimensions (not 14)
- Product vector is now 17 dimensions (not 18)
- Budget is no longer a factor in recommendations
- Content-based scoring formula has been updated
- Survey has 3 questions instead of 4

**File: YEAR 12 MAJOR WORK planning files/ML_IMPLEMENTATION_PROMPT.md**

Update the prompt to reflect:
- Survey has 3 questions (skill, instrument, genres)
- No budget question
- No budget filtering in recommendations
- Updated feature dimensions

## Verification Steps

After implementation, verify:

1. **Survey:**
   - Survey page shows only 3 questions
   - Progress bar shows 100% after answering 3 questions
   - Survey submission succeeds without budget
   - Survey data is saved to database (without budget)

2. **ML Model:**
   - HybridRecommender.refresh() succeeds
   - User feature vectors are 13 dimensions
   - Product feature vectors are 17 dimensions
   - KNN models train successfully
   - Recommendations are generated

3. **Recommendations:**
   - Recommendations display without % match indicator
   - Recommendation reasons don't mention budget
   - Recommendations are based on skill, instrument, and genres only

4. **Fallback:**
   - Simple recommendations work without budget filtering
   - No budget-related errors in logs

5. **Database:**
   - user_surveys table either has no budget_range column or it's ignored
   - Existing survey data still works (if column exists but is ignored)

## Rollback Plan

If issues arise, rollback steps:

1. Restore survey.html from backup
2. Restore app.py from backup
3. Restore ml/feature_engineering.py from backup
4. Restore ml/knn_models.py from backup
5. Restore ml/data_loader.py from backup
6. Restore base.html from backup
7. If migration was run, restore database from backup
8. Restart application

## Summary of Changes

**Files to modify:**
1. templates/survey.html - Remove budget question
2. templates/base.html - Remove % match indicator, update progress
3. app.py - Remove budget validation and filtering
4. ml/data_loader.py - Remove budget from SQL queries
5. ml/feature_engineering.py - Remove budget encoding
6. ml/knn_models.py - Remove budget from content-based filtering
7. migrations/007_remove_budget_from_surveys.py - Create new migration (optional)

**Files to optionally update:**
1. migrations/004_seed_ml_data.py - Remove budget from seed data
2. migrations/005_expand_ml_data.py - Remove budget from seed data
3. migrations/006_seed_more_surveys.py - Remove budget from seed data
4. tests/test_ml_recommender.py - Update tests

**Documentation to update:**
1. YEAR 12 MAJOR WORK planning files/KNN_MODEL_EXPLANATION.md
2. YEAR 12 MAJOR WORK planning files/ML_IMPLEMENTATION_PROMPT.md

**Expected outcomes:**
- Survey has 3 questions instead of 4
- ML model uses 13-dim user vectors and 17-dim product vectors
- Recommendations don't consider budget
- No % match indicator displayed
- Content-based scoring redistributed to other factors
