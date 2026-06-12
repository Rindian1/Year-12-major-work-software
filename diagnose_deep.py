#!/usr/bin/env python3
"""
Deep dive: check content-based recommendation differentiation
and product metadata quality.
"""

import os, sys, json
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml.data_loader import DataLoader
from ml.knn_models import ContentBasedRecommender, KNNItemRecommender
from ml.feature_engineering import encode_user_survey_row, encode_product_row
from ml_recommender import get_hybrid_recommender, reset_hybrid_recommender_for_tests

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "cart.db")
loader = DataLoader(DB)
products_df = loader.load_products()

# ===== 1. Check which products have NULL metadata =====
print("=" * 60)
print("  PRODUCT METADATA QUALITY")
print("=" * 60)
null_skill = products_df["skill_level"].isna().sum()
null_inst = products_df["instrument_type"].isna().sum()
null_genre = products_df["genre_suitability"].isna().sum()
print(f"Missing skill_level: {null_skill}/{len(products_df)}")
print(f"Missing instrument_type: {null_inst}/{len(products_df)}")
print(f"Missing genre_suitability: {null_genre}/{len(products_df)}")

# Check categories
cats = products_df["category"].value_counts()
print(f"\nCategory distribution:\n{cats.to_string()}")

# ===== 2. Check what product vectors look like =====
print("\n" + "=" * 60)
print("  SAMPLE PRODUCT ENCODINGS")
print("=" * 60)
for _, row in products_df.head(5).iterrows():
    vec = encode_product_row(row)
    print(f"  {row['name'][:30]:30s} | cat={str(row['category']):20s} | skill={row.get('skill_level')!s:15s} | genres={str(row.get('genres_list'))[:20]:20s} | vec=[{vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f}, ...]")
print("  ...")
for _, row in products_df.tail(5).iterrows():
    vec = encode_product_row(row)
    print(f"  {row['name'][:30]:30s} | cat={str(row['category']):20s} | skill={row.get('skill_level')!s:15s} | genres={str(row.get('genres_list'))[:20]:20s} | vec=[{vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f}, ...]")

# ===== 3. Check content-based differentiation =====
print("\n" + "=" * 60)
print("  CONTENT-BASED DIFFERENTIATION TEST")
print("=" * 60)
reset_hybrid_recommender_for_tests()
hr = get_hybrid_recommender(DB)
products_df = hr._products_df

# Test 3 different survey profiles
profiles = [
    {"skill_level": "advanced", "instrument_type": "electric", "preferred_genres": ["metal", "rock"]},
    {"skill_level": "beginner", "instrument_type": "acoustic", "preferred_genres": ["folk", "classical"]},
    {"skill_level": "professional", "instrument_type": "both", "preferred_genres": ["jazz", "blues"]},
]

all_recs = []
for i, survey in enumerate(profiles):
    cb = ContentBasedRecommender()
    recs = cb.recommend(survey, products_df, exclude=set())
    top10 = sorted(recs.items(), key=lambda x: -x[1][0])[:10]
    names = []
    for pid, (score, reason) in top10:
        row = products_df[products_df["id"] == pid].iloc[0]
        names.append(row["name"][:30])
    all_recs.append(set(n[0] for n in [(p, s) for p, (s, _) in top10]))
    print(f"\nProfile {i+1}: {survey['instrument_type']} {survey['skill_level']}, genres={survey['preferred_genres']}")
    for j, (pid, (score, reason)) in enumerate(top10, 1):
        row = products_df[products_df["id"] == pid].iloc[0]
        print(f"  {j}. [{row['category'][:10]:10s}] {row['name'][:35]:35s} | {reason[:45]:45s} | s={score:.3f}")

# Overlap between extreme profiles
ab = len(all_recs[0] & all_recs[1])
ac = len(all_recs[0] & all_recs[2])
bc = len(all_recs[1] & all_recs[2])
print(f"\n  Overlap: Profile1∩2={ab}, Profile1∩3={ac}, Profile2∩3={bc}")
print(f"  If overlap is high (e.g., >5), content-based model lacks differentiation!")

# ===== 4. Check a specific example: why are mics showing up? =====
print("\n" + "=" * 60)
print("  WHY ARE MICROPHONES GETTING RECOMMENDED?")
print("=" * 60)
mics = products_df[products_df["name"].str.contains("AKG|AT2020|Steinberg", case=False)]
for _, row in mics.iterrows():
    vec = encode_product_row(row)
    print(f"{row['name'][:35]:35s} | cat={row['category']:20s} | skill={str(row.get('skill_level','?')):12s} | inst={str(row.get('instrument_type','?')):10s} | genres_list={str(row.get('genres_list',[]))[:40]:40s}")

# ===== 5. Check Item-CF: interaction-based recommendations don't care about survey =====
print("\n" + "=" * 60)
print("  ITEM-CF DOMINATION CHECK")
print("=" * 60)
item_knn = KNNItemRecommender()
item_knn.fit(hr._inter, hr._product_ids)

for user_id in [3, 12, 97]:
    try:
        user_idx = hr._user_ids.index(user_id)
        user_w = float(hr._inter[user_idx].sum())
        recs = item_knn.recommend(user_idx, hr._inter, top_n=5)
        product_names = []
        for pid in list(recs.keys())[:5]:
            row = products_df[products_df["id"] == pid]
            if not row.empty:
                product_names.append(row.iloc[0]["name"][:35])
        print(f"  User {user_id} (interaction_weight={user_w:.1f}):")
        for name in product_names:
            print(f"    → {name}")
    except (ValueError, IndexError):
        pass

