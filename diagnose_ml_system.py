#!/usr/bin/env python3
"""
Diagnostic script to verify if the Machine Learning Recommender system
is working properly, personalized, and robust.
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml.data_loader import DataLoader
from ml.feature_engineering import FeatureEngineer, SURVEY_DIM, PRODUCT_DIM
from ml.knn_models import ContentBasedRecommender, KNNUserRecommender, KNNItemRecommender
from ml_recommender import HybridRecommender, get_hybrid_recommender, reset_hybrid_recommender_for_tests


def run_diagnostics():
    print("======================================================================")
    print("                  ML RECOMMENDER DIAGNOSTIC SUITE                    ")
    print("======================================================================\n")

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "cart.db")
    print(f"Database Path: {db_path}")
    if not os.path.exists(db_path):
        print(f"ERROR: Database file does not exist at {db_path}!")
        return

    # 1. Test Data Loader
    print("--- 1. Testing DataLoader ---")
    loader = DataLoader(db_path)
    try:
        users_df = loader.load_users_with_surveys()
        products_df = loader.load_products()
        interactions_df = loader.load_interactions()
        print(f"✔ Users with surveys loaded: {len(users_df)} rows")
        print(f"✔ Products loaded: {len(products_df)} rows")
        print(f"✔ Interactions loaded: {len(interactions_df)} rows")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Test Feature Dimensions and Vector Scaling
    print("\n--- 2. Testing Feature Engineering & Shapes ---")
    fe = FeatureEngineer()
    try:
        user_survey_scaled, user_ids, user_scaler = fe.build_user_feature_matrix(users_df)
        prod_scaled, prod_ids, prod_scaler = fe.build_product_feature_matrix(products_df)
        print(f"✔ Scaled user surveys shape: {user_survey_scaled.shape} (Expected SURVEY_DIM={SURVEY_DIM})")
        print(f"✔ Scaled products shape: {prod_scaled.shape} (Expected PRODUCT_DIM={PRODUCT_DIM})")
        
        # Build interaction matrix
        inter_matrix = loader.load_user_interaction_matrix(user_ids, prod_ids)
        print(f"✔ User-Item Interaction Matrix shape: {inter_matrix.shape}")
        
        # Build user KNN matrix
        X_user = fe.build_user_knn_matrix(user_survey_scaled, inter_matrix.values)
        print(f"✔ Concatenated user KNN matrix shape: {X_user.shape}")
        
        # Check non-zero density of interaction matrix
        non_zero = np.count_nonzero(inter_matrix.values)
        density = (non_zero / (inter_matrix.shape[0] * inter_matrix.shape[1])) * 100
        print(f"✔ Interaction matrix non-zeros: {non_zero} (Density: {density:.4f}%)")
    except Exception as e:
        print(f"✗ Feature engineering error: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Test KNN Recommenders and Cold-Start Compatibility
    print("\n--- 3. Testing Individual Recommenders (User 3) ---")
    try:
        user_id = 3
        user_idx = user_ids.index(user_id)
        
        # Content-Based
        cb = ContentBasedRecommender()
        survey = loader.get_user_survey(user_id)
        exclude = loader.get_exclude_product_ids(user_id)
        cb_recs = cb.recommend(survey, products_df, exclude)
        print(f"✔ Content-Based returned {len(cb_recs)} products")
        
        # User-CF KNN
        user_knn = KNNUserRecommender()
        user_knn.fit(X_user, user_ids, inter_matrix.values, prod_ids)
        u_recs = user_knn.recommend(user_id, top_n=10)
        print(f"✔ User-CF KNN returned {len(u_recs)} products")
        
        # Item-CF KNN
        item_knn = KNNItemRecommender()
        item_knn.fit(inter_matrix.values, prod_ids)
        i_recs = item_knn.recommend(user_idx, inter_matrix.values, top_n=10)
        print(f"✔ Item-CF KNN returned {len(i_recs)} products")
        
    except Exception as e:
        print(f"✗ Individual recommender test failed: {e}")
        import traceback
        traceback.print_exc()

    # 4. Test Hybrid Recommender & Multi-user Personalization Test
    print("\n--- 4. Testing HybridRecommender Personalization ---")
    try:
        reset_hybrid_recommender_for_tests()
        hr = get_hybrid_recommender(db_path)
        
        # We find two users with different surveys to check if recommendation is personalized
        # User A: prefers rock/metal/blues (typically heavy/rock guitars)
        # User B: prefers classical/folk (acoustic guitars)
        # Let's inspect some users
        print("Finding distinct users for comparison...")
        user_a_id = None
        user_b_id = None
        
        for idx, row in users_df.iterrows():
            uid = int(row["user_id"])
            srv = loader.get_user_survey(uid)
            if not srv:
                continue
            genres = [g.lower() for g in srv["preferred_genres"]]
            inst_type = srv["instrument_type"]
            
            if "electric" in inst_type and ("metal" in genres or "rock" in genres) and user_a_id is None:
                user_a_id = uid
            if "acoustic" in inst_type and ("classical" in genres or "folk" in genres) and user_b_id is None:
                user_b_id = uid
                
            if user_a_id is not None and user_b_id is not None:
                break
                
        if user_a_id is None or user_b_id is None:
            # Fallback to index-based choice
            user_a_id = user_ids[0]
            user_b_id = user_ids[min(5, len(user_ids)-1)]
            
        print(f"User A: ID={user_a_id}")
        survey_a = loader.get_user_survey(user_a_id)
        print(f"  Preferences: skill={survey_a['skill_level']}, instrument={survey_a['instrument_type']}, genres={survey_a['preferred_genres']}")
        
        print(f"User B: ID={user_b_id}")
        survey_b = loader.get_user_survey(user_b_id)
        print(f"  Preferences: skill={survey_b['skill_level']}, instrument={survey_b['instrument_type']}, genres={survey_b['preferred_genres']}")
        
        recs_a = hr.get_recommendations(user_a_id, n=10)
        recs_b = hr.get_recommendations(user_b_id, n=10)
        
        p_ids_a = [r["id"] for r in recs_a]
        p_ids_b = [r["id"] for r in recs_b]
        
        print(f"\nUser A Recommendations: {p_ids_a}")
        for idx, r in enumerate(recs_a[:3], 1):
            print(f"  {idx}. {r['name']} (${r['price']}) - Reason: {r['reason']}")
            
        print(f"\nUser B Recommendations: {p_ids_b}")
        for idx, r in enumerate(recs_b[:3], 1):
            print(f"  {idx}. {r['name']} (${r['price']}) - Reason: {r['reason']}")
            
        # Compute overlap
        set_a = set(p_ids_a)
        set_b = set(p_ids_b)
        overlap = set_a & set_b
        jaccard = len(overlap) / len(set_a | set_b) if len(set_a | set_b) else 0
        
        print(f"\n✔ Overlap between recommendations: {len(overlap)}/10 products")
        print(f"✔ Jaccard Similarity index: {jaccard:.4f}")
        if jaccard < 0.4:
            print("✔ Success: The recommendations are HIGHLY PERSONALIZED!")
        else:
            print("⚠ Warning: Low personalization. Recommendations are too similar!")
            
    except Exception as e:
        print(f"✗ Hybrid Recommender or personalization test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n======================================================================")
    print("                     DIAGNOSTICS COMPLETE                            ")
    print("======================================================================")


if __name__ == "__main__":
    run_diagnostics()
