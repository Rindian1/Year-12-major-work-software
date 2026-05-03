# Machine Learning Implementation - Recommended Products Feature

## Overview
This document outlines the implementation of a machine learning-powered "Recommended Products" panel that provides personalized product recommendations to users based on their browsing history and survey responses.

## Feature Description
The recommended products system will analyze:
1. **Recently viewed products** - User's browsing patterns and product interactions
2. **User survey responses** - Preferences collected during account creation
3. **Collaborative filtering** - Similar users' behavior patterns
4. **Content-based filtering** - Product attribute similarities

## Machine Learning Approaches

### Option 1: K-Nearest Neighbors (KNN) Algorithm
**Best for**: Finding similar users and products based on behavior patterns

#### Implementation Details:
```python
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import pandas as pd

class KNNRecommender:
    def __init__(self, n_neighbors=5):
        self.n_neighbors = n_neighbors
        self.scaler = StandardScaler()
        self.knn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        
    def train(self, user_product_matrix):
        """Train KNN on user-product interaction matrix"""
        scaled_data = self.scaler.fit_transform(user_product_matrix)
        self.knn.fit(scaled_data)
        
    def get_recommendations(self, user_id, n_recommendations=5):
        """Get product recommendations for a specific user"""
        user_vector = self.scaler.transform([user_product_matrix[user_id]])
        distances, indices = self.knn.kneighbors(user_vector)
        return self._recommend_products(indices, distances)
```

#### Advantages:
- Simple to implement and understand
- Works well with collaborative filtering
- No training time required (lazy learning)

#### Disadvantages:
- Performance issues with large datasets
- Requires careful feature scaling
- Memory intensive

### Option 2: Decision Trees / Random Forest
**Best for**: Rule-based recommendations based on guitar user attributes and preferences

#### Implementation Details:
```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

class GuitarDecisionTreeRecommender:
    def __init__(self, max_depth=10):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=max_depth,
            random_state=42
        )
        self.product_categories = ['guitars', 'amplifiers', 'effects', 'accessories']
        self.genre_weights = {'rock': 1.2, 'blues': 1.1, 'jazz': 1.0, 'classical': 0.9, 'metal': 1.1, 'pop': 1.0, 'country': 0.9, 'folk': 0.8, 'indie': 0.7}
        
    def encode_guitar_features(self, user_data):
        """Encode simplified guitar-specific features for ML model"""
        features = []
        
        # Skill level encoding (0-1 scale)
        skill_map = {'beginner': 0.25, 'intermediate': 0.5, 'advanced': 0.75, 'professional': 1.0}
        features.append(skill_map.get(user_data['skill_level'], 0.5))
        
        # Instrument type encoding
        instrument_map = {'acoustic': 0.33, 'electric': 0.67, 'both': 1.0}
        features.append(instrument_map.get(user_data['instrument_type'], 0.5))
        
        # Genre preferences (weighted)
        genre_vector = [0] * 9  # 9 genres total
        genre_list = ['rock', 'blues', 'jazz', 'classical', 'metal', 'pop', 'country', 'folk', 'indie']
        
        for genre in user_data.get('preferred_genres', []):
            if genre in genre_list:
                idx = genre_list.index(genre)
                genre_vector[idx] = self.genre_weights.get(genre, 1.0)
                
        features.extend(genre_vector)
        
        # Budget range encoding
        budget_map = {'under_500': 0.2, '500_1000': 0.4, '1000_2000': 0.6, '2000_5000': 0.8, 'over_5000': 1.0}
        features.append(budget_map.get(user_data['budget_range'], 0.5))
        
        return np.array(features)
        
    def create_training_data(self, users, products, interactions):
        """Create training data from user interactions and purchases"""
        X = []
        y = []
        
        for user in users:
            user_features = self.encode_guitar_features(user)
            user_interactions = [i for i in interactions if i['user_id'] == user['user_id']]
            
            # For each interaction, create a training example
            for interaction in user_interactions:
                if interaction['action'] == 'purchase':  # Focus on purchases for training
                    # Find the product
                    product = next((p for p in products if p['product_id'] == interaction['product_id']), None)
                    if product:
                        # Create feature vector
                        features = user_features.copy()
                        
                        # Add product-specific features
                        features['product_category'] = self.product_categories.index(product['category'])
                        features['product_price_range'] = product['price_range']
                        features['product_skill_level'] = ['beginner', 'intermediate', 'advanced', 'professional'].index(product['skill_level'])
                        
                        # Add genre compatibility
                        user_genres = set(user.get('preferred_genres', []))
                        product_genres = set(product.get('genre_suitability', []))
                        features['genre_compatibility'] = len(user_genres.intersection(product_genres)) / max(len(user_genres), 1)
                        
                        X.append(features)
                        y.append(1)  # Positive example (purchased)
                        
                        # Add negative examples (products not purchased)
                        other_products = [p for p in products if p['product_id'] != interaction['product_id']]
                        for other_product in other_products[:3]:  # Limit negative examples
                            neg_features = user_features.copy()
                            neg_features['product_category'] = self.product_categories.index(other_product['category'])
                            neg_features['product_price_range'] = other_product['price_range']
                            neg_features['product_skill_level'] = ['beginner', 'intermediate', 'advanced', 'professional'].index(other_product['skill_level'])
                            
                            other_genres = set(other_product.get('genre_suitability', []))
                            neg_features['genre_compatibility'] = len(user_genres.intersection(other_genres)) / max(len(user_genres), 1)
                            
                            X.append(neg_features)
                            y.append(0)  # Negative example (not purchased)
                            
        return pd.DataFrame(X), np.array(y)
        
    def train(self, users, products, interactions):
        """Train decision tree on guitar user-product interactions"""
        X, y = self.create_training_data(users, products, interactions)
        
        # Train the model
        self.model.fit(X, y)
        
        # Store feature names for later use
        self.feature_names = X.columns.tolist()
        
    def predict_product_preference(self, user_data, product):
        """Predict if user will like a specific product"""
        # Encode user features
        user_features = self.encode_guitar_features(user_data)
        
        # Add product features
        user_features['product_category'] = self.product_categories.index(product['category'])
        user_features['product_price_range'] = product['price_range']
        user_features['product_skill_level'] = ['beginner', 'intermediate', 'advanced', 'professional'].index(product['skill_level'])
        
        # Calculate genre compatibility
        user_genres = set(user_data.get('preferred_genres', []))
        product_genres = set(product.get('genre_suitability', []))
        user_features['genre_compatibility'] = len(user_genres.intersection(product_genres)) / max(len(user_genres), 1)
        
        # Create feature vector in correct order
        feature_vector = []
        for feature_name in self.feature_names:
            feature_vector.append(user_features.get(feature_name, 0))
            
        # Predict preference
        probability = self.model.predict_proba([feature_vector])[0][1]  # Probability of positive class
        
        return probability
        
    def get_recommendations(self, user_data, products, n_recommendations=5):
        """Get guitar product recommendations for user"""
        recommendations = []
        
        for product in products:
            # Calculate preference score
            preference_score = self.predict_product_preference(user_data, product)
            
            # Apply additional filters
            if self._is_suitable_for_user(user_data, product):
                final_score = preference_score * product['popularity_score'] / 10
                
                recommendations.append({
                    'product_id': product['product_id'],
                    'score': final_score,
                    'reason': f'decision_tree_prediction_{preference_score:.2f}'
                })
                
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:n_recommendations]
        
    def _is_suitable_for_user(self, user_data, product):
        """Check if product is suitable for user based on basic criteria"""
        # Check skill level compatibility
        user_skill = user_data.get('skill_level', 'intermediate')
        product_skill = product.get('skill_level', 'intermediate')
        
        skill_levels = ['beginner', 'intermediate', 'advanced', 'professional']
        user_level = skill_levels.index(user_skill)
        product_level = skill_levels.index(product_skill)
        
        # Product should not be more than 2 levels above user
        if product_level > user_level + 2:
            return False
            
        # Check instrument type compatibility
        user_instrument = user_data.get('instrument_type', 'electric')
        product_instrument = product.get('instrument_type', 'electric')
        
        if user_instrument != 'both' and product_instrument != 'both' and user_instrument != product_instrument:
            return False
            
        # Check budget compatibility
        user_budget = user_data.get('budget_range', '1000_2000')
        product_price = product.get('price_range', '1000_2000')
        
        budget_levels = ['under_500', '500_1000', '1000_2000', '2000_5000', 'over_5000']
        user_budget_level = budget_levels.index(user_budget)
        product_price_level = budget_levels.index(product_price)
        
        # Product should not be more than 1 level above user's budget
        if product_price_level > user_budget_level + 1:
            return False
            
        return True
        
    def explain_recommendation(self, user_data, product):
        """Explain why a product was recommended"""
        # Get feature importance for this prediction
        user_features = self.encode_guitar_features(user_data)
        user_features['product_category'] = self.product_categories.index(product['category'])
        user_features['product_price_range'] = product['price_range']
        user_features['product_skill_level'] = ['beginner', 'intermediate', 'advanced', 'professional'].index(product['skill_level'])
        
        user_genres = set(user_data.get('preferred_genres', []))
        product_genres = set(product.get('genre_suitability', []))
        user_features['genre_compatibility'] = len(user_genres.intersection(product_genres)) / max(len(user_genres), 1)
        
        # Create feature vector
        feature_vector = []
        for feature_name in self.feature_names:
            feature_vector.append(user_features.get(feature_name, 0))
            
        # Get feature importances
        importances = self.model.feature_importances_
        feature_importance_dict = dict(zip(self.feature_names, importances))
        
        # Find top contributing features
        top_features = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)[:5]
        
        explanation = "Recommended because:\n"
        for feature, importance in top_features:
            if user_features.get(feature, 0) > 0:
                explanation += f"- {feature.replace('_', ' ').title()}: {importance:.3f}\n"
                
        return explanation
```

#### Advantages:
- Interpretable results (can explain recommendations)
- Handles mixed data types well
- Robust to outliers

#### Disadvantages:
- May overfit with complex data
- Less effective for collaborative filtering
- Requires feature engineering

### Option 3: Hybrid Approach (Recommended)
**Combine both KNN and Decision Trees**:

```python
class HybridRecommender:
    def __init__(self):
        self.knn_recommender = KNNRecommender()
        self.tree_recommender = DecisionTreeRecommender()
        self.knn_weight = 0.6  # Weight for collaborative filtering
        self.tree_weight = 0.4  # Weight for content-based filtering
        
    def get_recommendations(self, user_id, user_features, n_recommendations=5):
        """Combine both approaches for better recommendations"""
        knn_recs = self.knn_recommender.get_recommendations(user_id, n_recommendations*2)
        tree_recs = self.tree_recommender.get_recommendations(user_features, n_recommendations*2)
        
        # Weighted combination of recommendations
        combined_scores = self._combine_recommendations(knn_recs, tree_recs)
        return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
```

## Data Requirements

### 1. User Survey Data
**Simplified Guitar Survey (4 Questions):**
```python
survey_schema = {
    'skill_level': ['beginner', 'intermediate', 'advanced', 'professional'],
    'instrument_type': ['acoustic', 'electric', 'both'],
    'preferred_genres': ['rock', 'blues', 'jazz', 'classical', 'metal', 'pop', 'country', 'folk', 'indie'],
    'budget_range': ['under_500', '500_1000', '1000_2000', '2000_5000', 'over_5000']
}
```

### 2. Product Data Structure
```python
product_schema = {
    'product_id': 'string',
    'name': 'string',
    'category': 'string',  # 'guitars', 'amplifiers', 'effects', 'accessories'
    'subcategory': 'string',  # 'electric', 'acoustic', 'tube_amp', 'solid_state', 'distortion', 'delay', etc.
    'price_range': 'string',
    'brand': 'string',
    'skill_level': 'string',  # 'beginner', 'intermediate', 'advanced', 'professional'
    'genre_suitability': 'list',  # ['rock', 'blues', 'jazz', etc.]
    'instrument_type': 'string',  # 'electric', 'acoustic', 'both'
    'features': 'list',
    'tags': 'list',
    'popularity_score': 'float',
    'rating': 'float',
    'description': 'string'
}
```

### 3. User Interaction Data
```python
interaction_schema = {
    'user_id': 'string',
    'product_id': 'string',
    'action': ['view', 'like', 'add_to_cart', 'purchase', 'compare'],
    'timestamp': 'datetime',
    'duration': 'integer',  # Time spent viewing product
    'frequency': 'integer'   # Number of interactions
}
```

## Sample Data for Guitar Recommendation System

### Sample User Profiles (20 Users)

```python
# User 1: "Rock Mike" - Intermediate Electric Player
user_mike = {
    'user_id': 'user_001',
    'skill_level': 'intermediate',
    'instrument_type': 'electric',
    'preferred_genres': ['rock', 'blues'],
    'budget_range': '1000_2000'
}

# User 2: "Acoustic Sarah" - Beginner Fingerstyle Player
user_sarah = {
    'user_id': 'user_002',
    'skill_level': 'beginner',
    'instrument_type': 'acoustic',
    'preferred_genres': ['folk', 'indie'],
    'budget_range': '500_1000'
}

# User 3: "Jazz Tom" - Advanced Professional
user_tom = {
    'user_id': 'user_003',
    'skill_level': 'professional',
    'instrument_type': 'both',
    'preferred_genres': ['jazz', 'blues'],
    'budget_range': 'over_5000'
}

# User 4: "Metal Alex" - Advanced Metal Player
user_alex = {
    'user_id': 'user_004',
    'skill_level': 'advanced',
    'instrument_type': 'electric',
    'preferred_genres': ['metal', 'rock'],
    'budget_range': '2000_5000'
}

# User 5: "Country Jenny" - Intermediate Country Player
user_jenny = {
    'user_id': 'user_005',
    'skill_level': 'intermediate',
    'instrument_type': 'both',
    'preferred_genres': ['country', 'folk'],
    'budget_range': '1000_2000'
}

# User 6: "Classical Maria" - Intermediate Classical Player
user_maria = {
    'user_id': 'user_006',
    'skill_level': 'intermediate',
    'instrument_type': 'acoustic',
    'preferred_genres': ['classical', 'folk'],
    'budget_range': '1000_2000'
}

# User 7: "Punk Dave" - Beginner Punk Player
user_dave = {
    'user_id': 'user_007',
    'skill_level': 'beginner',
    'instrument_type': 'electric',
    'preferred_genres': ['punk', 'rock'],
    'budget_range': 'under_500'
}

# User 8: "Blues Robert" - Advanced Blues Player
user_robert = {
    'user_id': 'user_008',
    'skill_level': 'advanced',
    'instrument_type': 'electric',
    'preferred_genres': ['blues', 'rock'],
    'budget_range': '2000_5000'
}

# User 9: "Pop Emma" - Beginner Pop Player
user_emma = {
    'user_id': 'user_009',
    'skill_level': 'beginner',
    'instrument_type': 'both',
    'preferred_genres': ['pop', 'indie'],
    'budget_range': '500_1000'
}

# User 10: "Fusion Carlos" - Professional Fusion Player
user_carlos = {
    'user_id': 'user_010',
    'skill_level': 'professional',
    'instrument_type': 'electric',
    'preferred_genres': ['jazz', 'rock', 'metal'],
    'budget_range': 'over_5000'
}

# User 11: "Folk Lisa" - Intermediate Folk Player
user_lisa = {
    'user_id': 'user_011',
    'skill_level': 'intermediate',
    'instrument_type': 'acoustic',
    'preferred_genres': ['folk', 'country'],
    'budget_range': '1000_2000'
}

# User 12: "Metal James" - Advanced Metal Player
user_james = {
    'user_id': 'user_012',
    'skill_level': 'advanced',
    'instrument_type': 'electric',
    'preferred_genres': ['metal', 'hard_rock'],
    'budget_range': '2000_5000'
}

# User 13: "Indie Amy" - Beginner Indie Player
user_amy = {
    'user_id': 'user_013',
    'skill_level': 'beginner',
    'instrument_type': 'acoustic',
    'preferred_genres': ['indie', 'pop'],
    'budget_range': '500_1000'
}

# User 14: "Rock Kevin" - Intermediate Rock Player
user_kevin = {
    'user_id': 'user_014',
    'skill_level': 'intermediate',
    'instrument_type': 'electric',
    'preferred_genres': ['rock', 'pop'],
    'budget_range': '1000_2000'
}

# User 15: "Jazz Susan" - Professional Jazz Player
user_susan = {
    'user_id': 'user_015',
    'skill_level': 'professional',
    'instrument_type': 'both',
    'preferred_genres': ['jazz', 'classical'],
    'budget_range': 'over_5000'
}

# User 16: "Country Mark" - Advanced Country Player
user_mark = {
    'user_id': 'user_016',
    'skill_level': 'advanced',
    'instrument_type': 'electric',
    'preferred_genres': ['country', 'rock'],
    'budget_range': '2000_5000'
}

# User 17: "Beginner Tim" - Complete Beginner
user_tim = {
    'user_id': 'user_017',
    'skill_level': 'beginner',
    'instrument_type': 'acoustic',
    'preferred_genres': ['pop', 'rock'],
    'budget_range': 'under_500'
}

# User 18: "Progressive Steve" - Advanced Progressive Player
user_steve = {
    'user_id': 'user_018',
    'skill_level': 'advanced',
    'instrument_type': 'electric',
    'preferred_genres': ['metal', 'progressive', 'jazz'],
    'budget_range': '2000_5000'
}

# User 19: "Singer Rachel" - Intermediate Singer-Songwriter
user_rachel = {
    'user_id': 'user_019',
    'skill_level': 'intermediate',
    'instrument_type': 'acoustic',
    'preferred_genres': ['folk', 'pop', 'indie'],
    'budget_range': '1000_2000'
}

# User 20: "Studio John" - Professional Studio Musician
user_john = {
    'user_id': 'user_020',
    'skill_level': 'professional',
    'instrument_type': 'both',
    'preferred_genres': ['rock', 'pop', 'jazz', 'country'],
    'budget_range': 'over_5000'
}
```

### Sample User Interactions
```python
# Mike's typical purchases:
mike_purchases = [
    {'product_id': 'gibson_sg_standard', 'action': 'purchase'},
    {'product_id': 'marshall_jcm800', 'action': 'purchase'},
    {'product_id': 'boss_ds1_distortion', 'action': 'purchase'},
    {'product_id': 'ibanez_ts9_tubescreamer', 'action': 'add_to_cart'}
]

# Sarah's typical purchases:
sarah_purchases = [
    {'product_id': 'martin_dxe', 'action': 'purchase'},
    {'product_id': 'yamaha_thr5_acoustic', 'action': 'purchase'},
    {'product_id': 'boss_ad2_acoustic_preamp', 'action': 'view'},
    {'product_id': 'daddario_exp110_strings', 'action': 'purchase'}
]

# Tom's typical purchases:
tom_purchases = [
    {'product_id': 'gibson_es175', 'action': 'purchase'},
    {'product_id': 'fender_twin_reverb', 'action': 'purchase'},
    {'product_id': 'strymon_timeline_delay', 'action': 'purchase'},
    {'product_id': 'kemper_profiler', 'action': 'purchase'}
]

# Alex's typical purchases:
alex_purchases = [
    {'product_id': 'ibanez_rg550', 'action': 'purchase'},
    {'product_id': 'mesa_boogie_dual_rectifier', 'action': 'purchase'},
    {'product_id': 'proco_rat_distortion', 'action': 'purchase'},
    {'product_id': 'mxr_phase90', 'action': 'purchase'}
]

# Jenny's typical purchases:
jenny_purchases = [
    {'product_id': 'fender_telecaster', 'action': 'purchase'},
    {'product_id': 'fender_deluxe_reverb', 'action': 'purchase'},
    {'product_id': 'boss_ce2_chorus', 'action': 'purchase'},
    {'product_id': 'martin_d15', 'action': 'view'}
]
```

### Sample Product Catalog

#### Electric Guitars
```python
electric_guitars = [
    {
        'product_id': 'gibson_sg_standard',
        'name': 'Gibson SG Standard',
        'category': 'guitars',
        'subcategory': 'electric',
        'price_range': '1000_2000',
        'brand': 'gibson',
        'skill_level': 'intermediate',
        'genre_suitability': ['rock', 'blues', 'metal'],
        'instrument_type': 'electric',
        'features': ['mahogany_body', 'dual_humbuckers', 'set_neck'],
        'tags': ['rock', 'blues', 'sustain', 'lightweight'],
        'popularity_score': 8.5,
        'rating': 4.7,
        'description': 'Classic rock guitar with powerful sustain'
    },
    {
        'product_id': 'fender_stratocaster',
        'name': 'Fender American Professional Stratocaster',
        'category': 'guitars',
        'subcategory': 'electric',
        'price_range': '1000_2000',
        'brand': 'fender',
        'skill_level': 'intermediate',
        'genre_suitability': ['rock', 'blues', 'pop', 'country'],
        'instrument_type': 'electric',
        'features': ['alder_body', 'three_single_coils', 'tremolo'],
        'tags': ['versatile', 'clean_tone', 'strat'],
        'popularity_score': 9.2,
        'rating': 4.8,
        'description': 'Most versatile electric guitar for any genre'
    },
    {
        'product_id': 'ibanez_rg550',
        'name': 'Ibanez RG550 Genesis',
        'category': 'guitars',
        'subcategory': 'electric',
        'price_range': '1000_2000',
        'brand': 'ibanez',
        'skill_level': 'advanced',
        'genre_suitability': ['metal', 'rock', 'shred'],
        'instrument_type': 'electric',
        'features': ['basswood_body', 'hsh_pickups', 'edge_tremolo', 'wizard_neck'],
        'tags': ['metal', 'shred', 'fast_neck', 'floyd_rose'],
        'popularity_score': 7.8,
        'rating': 4.6,
        'description': 'High-performance guitar for metal and shred'
    },
    {
        'product_id': 'gibson_es175',
        'name': 'Gibson ES-175',
        'category': 'guitars',
        'subcategory': 'electric',
        'price_range': '2000_5000',
        'brand': 'gibson',
        'skill_level': 'professional',
        'genre_suitability': ['jazz', 'blues', 'fusion'],
        'instrument_type': 'electric',
        'features': ['hollow_body', 'single_humbucker', 'set_neck'],
        'tags': ['jazz', 'hollow_body', 'warm_tone'],
        'popularity_score': 8.0,
        'rating': 4.9,
        'description': 'Classic jazz guitar with warm, rich tone'
    },
    {
        'product_id': 'fender_telecaster',
        'name': 'Fender American Professional Telecaster',
        'category': 'guitars',
        'subcategory': 'electric',
        'price_range': '1000_2000',
        'brand': 'fender',
        'skill_level': 'intermediate',
        'genre_suitability': ['country', 'rock', 'blues'],
        'instrument_type': 'electric',
        'features': ['alder_body', 'single_coils', 'hardtail_bridge'],
        'tags': ['country', 'twang', 'bright_tone'],
        'popularity_score': 8.8,
        'rating': 4.7,
        'description': 'Iconic guitar for country and rock'
    }
]
```

#### Acoustic Guitars
```python
acoustic_guitars = [
    {
        'product_id': 'martin_dxe',
        'name': 'Martin DXE',
        'category': 'guitars',
        'subcategory': 'acoustic',
        'price_range': '500_1000',
        'brand': 'martin',
        'skill_level': 'beginner',
        'genre_suitability': ['folk', 'country', 'singer_songwriter'],
        'instrument_type': 'acoustic',
        'features': ['hpl_back_sides', 'sitka_spruce_top', 'dreadnought'],
        'tags': ['beginner', 'dreadnought', 'affordable'],
        'popularity_score': 8.2,
        'rating': 4.5,
        'description': 'Affordable Martin dreadnought for beginners'
    },
    {
        'product_id': 'taylor_214ce',
        'name': 'Taylor 214ce Grand Auditorium',
        'category': 'guitars',
        'subcategory': 'acoustic',
        'price_range': '1000_2000',
        'brand': 'taylor',
        'skill_level': 'intermediate',
        'genre_suitability': ['pop', 'folk', 'fingerstyle'],
        'instrument_type': 'acoustic',
        'features': ['grand_auditorium', 'es2_electronics', 'veneer_back_sides'],
        'tags': ['fingerstyle', 'playable_neck', 'electronics'],
        'popularity_score': 8.9,
        'rating': 4.8,
        'description': 'Versatile acoustic for fingerstyle and strumming'
    },
    {
        'product_id': 'martin_d15',
        'name': 'Martin D-15',
        'category': 'guitars',
        'subcategory': 'acoustic',
        'price_range': '1000_2000',
        'brand': 'martin',
        'skill_level': 'intermediate',
        'genre_suitability': ['folk', 'blues', 'country'],
        'instrument_type': 'acoustic',
        'features': ['all_mahogany', 'dreadnought', 'warm_tone'],
        'tags': ['warm_tone', 'mahogany', 'traditional'],
        'popularity_score': 8.4,
        'rating': 4.6,
        'description': 'All-mahogany dreadnought with warm, rich tone'
    }
]
```

#### Effects Pedals
```python
effects_pedals = [
    {
        'product_id': 'boss_ds1_distortion',
        'name': 'Boss DS-1 Distortion',
        'category': 'effects',
        'subcategory': 'distortion',
        'price_range': 'under_500',
        'brand': 'boss',
        'skill_level': 'beginner',
        'genre_suitability': ['rock', 'metal', 'punk'],
        'instrument_type': 'electric',
        'features': ['single_knob', 'true_bypass', 'led_indicator'],
        'tags': ['distortion', 'classic', 'affordable'],
        'popularity_score': 8.7,
        'rating': 4.4,
        'description': 'Classic distortion pedal for rock and metal'
    },
    {
        'product_id': 'ibanez_ts9_tubescreamer',
        'name': 'Ibanez TS9 Tube Screamer',
        'category': 'effects',
        'subcategory': 'overdrive',
        'price_range': 'under_500',
        'brand': 'ibanez',
        'skill_level': 'intermediate',
        'genre_suitability': ['rock', 'blues', 'country'],
        'instrument_type': 'electric',
        'features': ['overdrive', 'mid_boost', 'legendary_tone'],
        'tags': ['overdrive', 'blues', 'classic'],
        'popularity_score': 9.1,
        'rating': 4.7,
        'description': 'Legendary overdrive pedal for blues and rock'
    },
    {
        'product_id': 'proco_rat_distortion',
        'name': 'ProCo RAT 2',
        'category': 'effects',
        'subcategory': 'distortion',
        'price_range': 'under_500',
        'brand': 'proco',
        'skill_level': 'advanced',
        'genre_suitability': ['rock', 'metal', 'punk'],
        'instrument_type': 'electric',
        'features': ['distortion', 'filter_control', 'versatile'],
        'tags': ['distortion', 'metal', 'versatile'],
        'popularity_score': 8.3,
        'rating': 4.5,
        'description': 'Versatile distortion for rock and metal'
    },
    {
        'product_id': 'boss_ce2_chorus',
        'name': 'Boss CE-2 Chorus',
        'category': 'effects',
        'subcategory': 'chorus',
        'price_range': 'under_500',
        'brand': 'boss',
        'skill_level': 'beginner',
        'genre_suitability': ['pop', 'rock', 'country'],
        'instrument_type': 'both',
        'features': ['chorus', 'depth_rate', 'analog'],
        'tags': ['chorus', '80s', 'clean_tone'],
        'popularity_score': 8.0,
        'rating': 4.3,
        'description': 'Classic analog chorus pedal'
    },
    {
        'product_id': 'strymon_timeline_delay',
        'name': 'Strymon Timeline Delay',
        'category': 'effects',
        'subcategory': 'delay',
        'price_range': '2000_5000',
        'brand': 'strymon',
        'skill_level': 'professional',
        'genre_suitability': ['all_genres'],
        'instrument_type': 'both',
        'features': ['multi_delay', 'presets', 'midi', 'high_quality'],
        'tags': ['delay', 'professional', 'studio_quality'],
        'popularity_score': 9.3,
        'rating': 4.9,
        'description': 'Professional multi-delay pedal with studio quality'
    }
]
```

#### Amplifiers
```python
amplifiers = [
    {
        'product_id': 'marshall_jcm800',
        'name': 'Marshall JCM800 2203',
        'category': 'amplifiers',
        'subcategory': 'tube_amp',
        'price_range': '1000_2000',
        'brand': 'marshall',
        'skill_level': 'intermediate',
        'genre_suitability': ['rock', 'metal', 'hard_rock'],
        'instrument_type': 'electric',
        'features': ['tube', '100_watts', 'master_volume', 'classic_marshall'],
        'tags': ['marshall', 'tube', 'rock', 'classic'],
        'popularity_score': 9.0,
        'rating': 4.8,
        'description': 'Classic Marshall tube amp for rock and metal'
    },
    {
        'product_id': 'fender_twin_reverb',
        'name': 'Fender \'65 Twin Reverb',
        'category': 'amplifiers',
        'subcategory': 'tube_amp',
        'price_range': '1000_2000',
        'brand': 'fender',
        'skill_level': 'professional',
        'genre_suitability': ['jazz', 'blues', 'country', 'rock'],
        'instrument_type': 'electric',
        'features': ['tube', '85_watts', 'reverb', 'vibrato', 'clean_tone'],
        'tags': ['fender', 'clean_tone', 'reverb', 'jazz'],
        'popularity_score': 8.8,
        'rating': 4.9,
        'description': 'Iconic Fender amp with pristine clean tone'
    },
    {
        'product_id': 'mesa_boogie_dual_rectifier',
        'name': 'Mesa/Boogie Dual Rectifier',
        'category': 'amplifiers',
        'subcategory': 'tube_amp',
        'price_range': '2000_5000',
        'brand': 'mesa_boogie',
        'skill_level': 'advanced',
        'genre_suitability': ['metal', 'hard_rock', 'progressive'],
        'instrument_type': 'electric',
        'features': ['tube', '100_watts', 'rectifier', 'high_gain'],
        'tags': ['metal', 'high_gain', 'boogie', 'modern'],
        'popularity_score': 8.6,
        'rating': 4.7,
        'description': 'High-gain tube amp for modern metal'
    },
    {
        'product_id': 'yamaha_thr5_acoustic',
        'name': 'Yamaha THR5A Acoustic',
        'category': 'amplifiers',
        'subcategory': 'solid_state',
        'price_range': 'under_500',
        'brand': 'yamaha',
        'skill_level': 'beginner',
        'genre_suitability': ['acoustic', 'folk', 'country'],
        'instrument_type': 'acoustic',
        'features': ['solid_state', 'portable', 'battery_power', 'effects'],
        'tags': ['acoustic', 'portable', 'practice', 'battery'],
        'popularity_score': 8.1,
        'rating': 4.5,
        'description': 'Portable acoustic amp for practice and small venues'
    },
    {
        'product_id': 'fender_deluxe_reverb',
        'name': 'Fender \'65 Deluxe Reverb',
        'category': 'amplifiers',
        'subcategory': 'tube_amp',
        'price_range': '1000_2000',
        'brand': 'fender',
        'skill_level': 'intermediate',
        'genre_suitability': ['country', 'blues', 'rock', 'jazz'],
        'instrument_type': 'electric',
        'features': ['tube', '22_watts', 'reverb', 'vibrato', 'breakup'],
        'tags': ['fender', 'deluxe', 'versatile', 'recording'],
        'popularity_score': 9.2,
        'rating': 4.8,
        'description': 'Versatile tube amp perfect for recording and small venues'
    }
]
```

### Sample User-Product Interaction Patterns

#### Mike's Recommendation Profile
```python
mike_recommendations = {
    'high_confidence': [
        {'product_id': 'gibson_les_paul_standard', 'score': 0.95, 'reason': 'matches_rock_preference'},
        {'product_id': 'boss_sd1_overdrive', 'score': 0.92, 'reason': 'complements_distortion'},
        {'product_id': 'marshall_1959slp', 'score': 0.88, 'reason': 'upgraded_marshall'}
    ],
    'medium_confidence': [
        {'product_id': 'fender_jaguar', 'score': 0.75, 'reason': 'alternative_rock_option'},
        {'product_id': 'electro_harmonix_big_muff', 'score': 0.72, 'reason': 'fuzz_for_metal'}
    ]
}
```

#### Sarah's Recommendation Profile
```python
sarah_recommendations = {
    'high_confidence': [
        {'product_id': 'taylor_gs_mini', 'score': 0.93, 'reason': 'perfect_fingerstarter'},
        {'product_id': 'fishman_aura_spectrum', 'score': 0.89, 'reason': 'acoustic_enhancement'},
        {'product_id': 'daddario_exp12_strings', 'score': 0.87, 'reason': 'string_maintenance'}
    ],
    'medium_confidence': [
        {'product_id': 'yamaha_fg830', 'score': 0.78, 'reason': 'affordable_upgrade'},
        {'product_id': 'boss_ad3_acoustic', 'score': 0.74, 'reason': 'acoustic_effects'}
    ]
}
```

#### Tom's Recommendation Profile
```python
tom_recommendations = {
    'high_confidence': [
        {'product_id': 'paul_reed_smith_hollowbody_ii', 'score': 0.96, 'reason': 'professional_jazz'},
        {'product_id': 'victoria_20112', 'score': 0.94, 'reason': 'vintage_tone'},
        {'product_id': 'catalinbread_belle_epoch', 'score': 0.91, 'reason': 'tape_echo'}
    ],
    'medium_confidence': [
        {'product_id': 'collings_i35_lc', 'score': 0.82, 'reason': 'boutique_option'},
        {'product_id': 'two_notes torpedo_cab', 'score': 0.79, 'reason': 'recording_solution'}
    ]
}
```

## Database Schema Design

### Tables Required:

```sql
-- User survey responses
CREATE TABLE user_surveys (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    age_range VARCHAR(20),
    gender VARCHAR(20),
    income_range VARCHAR(20),
    interests JSON,
    shopping_frequency VARCHAR(20),
    price_sensitivity VARCHAR(20),
    brand_preference VARCHAR(20),
    preferred_categories JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product interactions tracking
CREATE TABLE product_interactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    action VARCHAR(20),
    duration INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendation cache (for performance)
CREATE TABLE recommendation_cache (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    score FLOAT,
    algorithm VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
```

## Flask Integration

### 1. New Routes Required
```python
@app.route('/api/recommendations/<int:user_id>')
def get_recommendations(user_id):
    """Get personalized recommendations for user"""
    try:
        # Get user features from survey
        user_features = get_user_features(user_id)
        
        # Get recent interactions
        recent_products = get_recent_products(user_id, limit=10)
        
        # Generate recommendations
        recommendations = hybrid_recommender.get_recommendations(
            user_id, user_features, n_recommendations=10
        )
        
        return jsonify({
            'recommendations': recommendations,
            'algorithm': 'hybrid_knn_decision_tree',
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/survey', methods=['POST'])
def submit_survey():
    """Handle user survey submission"""
    try:
        survey_data = request.get_json()
        user_id = current_user.id
        
        # Validate and store survey responses
        store_user_survey(user_id, survey_data)
        
        # Trigger recommendation model update
        update_user_recommendations(user_id)
        
        return jsonify({'message': 'Survey submitted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 2. Model Training Service
```python
class RecommendationService:
    def __init__(self):
        self.hybrid_recommender = HybridRecommender()
        self.model_trained = False
        
    def train_models(self):
        """Train recommendation models with current data"""
        try:
            # Load data from database
            user_product_matrix = self._build_user_product_matrix()
            user_features, product_labels = self._prepare_training_data()
            
            # Train both models
            self.hybrid_recommender.knn_recommender.train(user_product_matrix)
            self.hybrid_recommender.tree_recommender.train(user_features, product_labels)
            
            self.model_trained = True
            logger.info("Recommendation models trained successfully")
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            raise
            
    def update_recommendations_for_user(self, user_id):
        """Update cached recommendations for specific user"""
        user_features = get_user_features(user_id)
        recommendations = self.hybrid_recommender.get_recommendations(
            user_id, user_features
        )
        
        # Cache recommendations
        cache_recommendations(user_id, recommendations)
        return recommendations
```

## Frontend Implementation

### 1. Recommended Products Panel Component
```html
<div class="recommended-products-panel" id="recommendedPanel">
    <h3>Recommended for You</h3>
    <div class="loading-spinner" id="recommendationsLoading">
        <div class="spinner"></div>
        <p>Finding perfect matches for you...</p>
    </div>
    <div class="recommendations-grid" id="recommendationsGrid" style="display: none;">
        <!-- Products will be dynamically inserted here -->
    </div>
    <div class="refresh-button">
        <button onclick="refreshRecommendations()" class="btn-secondary">
            <i class="fas fa-sync-alt"></i> Refresh Recommendations
        </button>
    </div>
</div>
```

### 2. JavaScript Integration
```javascript
class RecommendationPanel {
    constructor() {
        this.userId = getCurrentUserId();
        this.recommendations = [];
        this.loading = false;
    }
    
    async loadRecommendations() {
        try {
            this.setLoading(true);
            
            const response = await fetch(`/api/recommendations/${this.userId}`);
            const data = await response.json();
            
            if (data.recommendations) {
                this.recommendations = data.recommendations;
                this.renderRecommendations();
            }
            
        } catch (error) {
            console.error('Failed to load recommendations:', error);
            this.showError();
        } finally {
            this.setLoading(false);
        }
    }
    
    renderRecommendations() {
        const grid = document.getElementById('recommendationsGrid');
        grid.innerHTML = '';
        
        this.recommendations.forEach(product => {
            const productCard = this.createProductCard(product);
            grid.appendChild(productCard);
        });
        
        grid.style.display = 'grid';
        document.getElementById('recommendationsLoading').style.display = 'none';
    }
    
    createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <img src="${product.image_url}" alt="${product.name}" class="product-image">
            <div class="product-info">
                <h4 class="product-name">${product.name}</h4>
                <p class="product-price">$${product.price}</p>
                <div class="product-rating">
                    ${this.renderStars(product.rating)}
                    <span class="rating-text">(${product.reviews})</span>
                </div>
                <div class="recommendation-score">
                    <span class="score-label">Match: </span>
                    <span class="score-value">${Math.round(product.score * 100)}%</span>
                </div>
            </div>
            <div class="product-actions">
                <button onclick="viewProduct(${product.id})" class="btn-primary">View Details</button>
                <button onclick="addToWishlist(${product.id})" class="btn-secondary">
                    <i class="fas fa-heart"></i>
                </button>
            </div>
        `;
        return card;
    }
}

// Initialize recommendation panel
document.addEventListener('DOMContentLoaded', () => {
    const recommendationPanel = new RecommendationPanel();
    recommendationPanel.loadRecommendations();
});
```

## Security Considerations

### 1. Data Privacy
- **User Consent**: Implement clear consent for data collection
- **Data Minimization**: Only collect necessary survey data
- **Anonymization**: Anonymize data for model training where possible
- **GDPR Compliance**: Follow data protection regulations

### 2. Input Validation
```python
def validate_survey_data(survey_data):
    """Validate survey responses before processing"""
    required_fields = ['age_range', 'gender', 'interests']
    
    for field in required_fields:
        if field not in survey_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate age range
    valid_ages = ['18-24', '25-34', '35-44', '45-54', '55+']
    if survey_data['age_range'] not in valid_ages:
        raise ValueError("Invalid age range")
    
    # Sanitize string inputs
    for key, value in survey_data.items():
        if isinstance(value, str):
            survey_data[key] = sanitize_input(value)
    
    return survey_data
```

### 3. SQL Injection Prevention
```python
def get_user_features(user_id):
    """Safely retrieve user features from database"""
    try:
        user_id = int(user_id)  # Validate input type
        
        query = """
        SELECT age_range, gender, interests, price_sensitivity, brand_preference
        FROM user_surveys 
        WHERE user_id = %s
        """
        
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
        
    except (ValueError, psycopg2.Error) as e:
        logger.error(f"Database error in get_user_features: {e}")
        return None
```

## Performance Optimization

### 1. Caching Strategy
```python
import redis
from datetime import datetime, timedelta

class RecommendationCache:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = 3600  # 1 hour
        
    def get_cached_recommendations(self, user_id):
        """Get cached recommendations if available"""
        cache_key = f"recommendations:{user_id}"
        cached_data = self.redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
        
    def cache_recommendations(self, user_id, recommendations):
        """Cache recommendations for user"""
        cache_key = f"recommendations:{user_id}"
        self.redis_client.setex(
            cache_key, 
            self.cache_ttl, 
            json.dumps(recommendations)
        )
```

### 2. Batch Processing
```python
def batch_update_recommendations():
    """Update recommendations for all users in batches"""
    users = get_all_active_users()
    batch_size = 100
    
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        
        for user in batch:
            try:
                update_user_recommendations(user['id'])
            except Exception as e:
                logger.error(f"Failed to update recommendations for user {user['id']}: {e}")
        
        # Small delay to prevent overwhelming the system
        time.sleep(0.1)
```

## Testing Strategy

### 1. Unit Tests
```python
import unittest
from unittest.mock import Mock, patch

class TestRecommendationSystem(unittest.TestCase):
    def setUp(self):
        self.recommender = HybridRecommender()
        self.mock_user_data = self._create_mock_user_data()
        
    def test_knn_recommendations(self):
        """Test KNN recommendation generation"""
        recommendations = self.recommender.knn_recommender.get_recommendations(
            user_id=1, n_recommendations=5
        )
        
        self.assertEqual(len(recommendations), 5)
        self.assertTrue(all(isinstance(rec, dict) for rec in recommendations))
        
    def test_survey_validation(self):
        """Test survey data validation"""
        valid_survey = {
            'age_range': '25-34',
            'gender': 'male',
            'interests': ['technology', 'sports']
        }
        
        self.assertTrue(validate_survey_data(valid_survey))
        
    @patch('database.get_user_features')
    def test_recommendation_api(self, mock_get_features):
        """Test recommendation API endpoint"""
        mock_get_features.return_value = self.mock_user_data
        
        response = self.client.get('/api/recommendations/1')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('recommendations', data)
```

### 2. Integration Tests
```python
def test_end_to_end_recommendations():
    """Test complete recommendation pipeline"""
    # 1. Create test user
    user_id = create_test_user()
    
    # 2. Submit survey
    survey_data = generate_test_survey()
    response = client.post('/api/user/survey', json=survey_data)
    assert response.status_code == 200
    
    # 3. Add product interactions
    add_test_interactions(user_id)
    
    # 4. Get recommendations
    response = client.get(f'/api/recommendations/{user_id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data['recommendations']) > 0
```

## Implementation Timeline

### Phase 1: Data Collection (Week 1-2)
- Design and implement user survey
- Create database schema
- Set up data collection infrastructure
- Implement input validation and security measures

### Phase 2: Model Development (Week 3-4)
- Implement KNN recommender
- Implement Decision Tree recommender
- Create hybrid approach
- Develop training pipeline

### Phase 3: Integration (Week 5-6)
- Integrate with Flask backend
- Develop API endpoints
- Implement caching system
- Create frontend components

### Phase 4: Testing & Optimization (Week 7-8)
- Unit and integration testing
- Performance optimization
- Security testing
- User acceptance testing

## Success Metrics

### Technical Metrics
- **Recommendation Accuracy**: >70% user satisfaction with recommendations
- **Response Time**: <500ms for recommendation generation
- **Cache Hit Rate**: >80% of recommendations served from cache
- **Model Training Time**: <5 minutes for full model retraining

### Business Metrics
- **Click-Through Rate**: >15% on recommended products
- **Conversion Rate**: >5% from recommendations to purchases
- **User Engagement**: 20% increase in time spent on site
- **Survey Completion**: >80% of new users complete survey


---

*This implementation plan provides a comprehensive roadmap for integrating machine learning-powered product recommendations into your Flask application, with strong emphasis on security, performance, and user experience.*
