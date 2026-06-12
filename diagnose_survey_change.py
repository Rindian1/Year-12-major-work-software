#!/usr/bin/env python3
"""
Diagnose why recommendations don't change when survey is updated.
Simulates the exact flow: submit survey -> refresh -> get recommendations.
"""

import os
import sys
import json
import sqlite3
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_recommender import get_hybrid_recommender, reset_hybrid_recommender_for_tests
from ml.data_loader import DataLoader
from ml.config import USER_CF_WEIGHT, ITEM_CF_WEIGHT, CONTENT_WEIGHT

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "cart.db")


def print_sep(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_user(user_id):
    print_sep(f"TESTING USER {user_id}")
    
    # Step 1: Get current survey and recommendations
    loader = DataLoader(DB)
    survey_before = loader.get_user_survey(user_id)
    print(f"\nCurrent survey: skill={survey_before['skill_level']}, "
          f"instrument={survey_before['instrument_type']}, "
          f"genres={survey_before['preferred_genres']}")
    
    reset_hybrid_recommender_for_tests()
    rec = get_hybrid_recommender(DB)
    
    recs_before = rec.get_recommendations(user_id, n=10)
    print(f"\n▶ Recommendations BEFORE survey change ({len(recs_before)}):")
    for i, r in enumerate(recs_before[:5], 1):
        print(f"  {i}. {r['name'][:40]:40s} | {r['reason'][:45]:45s} | score={r['score']:.3f}")

    # Step 2: Get user's interaction weight
    try:
        user_idx = rec._user_ids.index(user_id)
        user_w = float(rec._inter[user_idx].sum())
    except (ValueError, AttributeError, IndexError):
        user_w = 0.0
    print(f"\nUser interaction weight: {user_w:.2f}")
    print(f"Default weights: u={USER_CF_WEIGHT}, i={ITEM_CF_WEIGHT}, c={CONTENT_WEIGHT}")
    if user_w < 5:
        print(f"→ LOW interaction (< 5): using w_u=0.2, w_i=0.3, w_c=0.5")
    elif user_w > 80:
        print(f"→ HIGH interaction (> 80): using w_u=0.2, w_i=0.5, w_c=0.3")
    else:
        print(f"→ MEDIUM interaction: using defaults")

    # Step 3: Change survey to something very different
    new_instrument = "acoustic" if survey_before["instrument_type"] != "acoustic" else "electric"
    new_skill = "beginner" if survey_before["skill_level"] not in ("beginner",) else "advanced"
    
    # Pick genres that are least similar to current ones
    all_genres = ["rock", "blues", "jazz", "classical", "metal", "pop", "country", "folk", "indie"]
    current = [g.lower() for g in survey_before["preferred_genres"]]
    opposite = [g for g in all_genres if g not in current][:2]
    
    new_survey = {
        "skill_level": new_skill,
        "instrument_type": new_instrument,
        "preferred_genres": opposite
    }
    print(f"\n--- Changing survey to ---")
    print(f"  skill: {survey_before['skill_level']} → {new_survey['skill_level']}")
    print(f"  instrument: {survey_before['instrument_type']} → {new_survey['instrument_type']}")
    print(f"  genres: {survey_before['preferred_genres']} → {new_survey['preferred_genres']}")

    # Step 4: Save the new survey directly to DB (simulating submit_survey)
    conn = sqlite3.connect(DB)
    existing = conn.execute("SELECT id FROM user_surveys WHERE user_id = ?", (user_id,)).fetchone()
    if existing:
        conn.execute("""
            UPDATE user_surveys 
            SET skill_level = ?, instrument_type = ?, preferred_genres = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (new_survey["skill_level"], new_survey["instrument_type"],
              json.dumps(new_survey["preferred_genres"]), user_id))
    else:
        conn.execute("""
            INSERT INTO user_surveys (user_id, skill_level, instrument_type, preferred_genres)
            VALUES (?, ?, ?, ?)
        """, (user_id, new_survey["skill_level"], new_survey["instrument_type"],
              json.dumps(new_survey["preferred_genres"])))
    conn.execute("DELETE FROM recommendation_cache WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    # Step 5: Verify survey was saved correctly
    loader2 = DataLoader(DB)
    survey_after = loader2.get_user_survey(user_id)
    print(f"\nVerified saved survey: {survey_after}")
    
    # Step 6: Refresh the recommender (same as app.submit_survey does)
    print(f"\n--- Calling refresh() ---")
    try:
        rec2 = get_hybrid_recommender(DB)
        rec2.refresh()
        print(f"  ✓ refresh() completed successfully")
    except Exception as e:
        print(f"  ✗ refresh() FAILED: {e}")
        traceback.print_exc()
        return None
    
    # Step 7: Get new recommendations
    recs_after = rec2.get_recommendations(user_id, n=10)
    print(f"\n▶ Recommendations AFTER survey change ({len(recs_after)}):")
    for i, r in enumerate(recs_after[:5], 1):
        print(f"  {i}. {r['name'][:40]:40s} | {r['reason'][:45]:45s} | score={r['score']:.3f}")
    
    # Step 8: Compare
    ids_before = {r["id"] for r in recs_before}
    ids_after = {r["id"] for r in recs_after}
    same = ids_before == ids_after
    overlap = len(ids_before & ids_after)
    
    print(f"\n--- Comparison ---")
    print(f"  Product IDs before: {sorted(ids_before)[:10]}")
    print(f"  Product IDs after:  {sorted(ids_after)[:10]}")
    print(f"  Overlap: {overlap}/{len(ids_before)} products")
    print(f"  {'⚠ IDENTICAL' if same else '✓ DIFFERENT'} - {'Problem: survey change had NO effect!' if same else 'Good: recommendations changed after survey update'}")
    
    # Restore original survey
    conn = sqlite3.connect(DB)
    if existing:
        conn.execute("""
            UPDATE user_surveys 
            SET skill_level = ?, instrument_type = ?, preferred_genres = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (survey_before["skill_level"], survey_before["instrument_type"],
              json.dumps(survey_before["preferred_genres"]), user_id))
    conn.commit()
    conn.close()
    
    return (ids_before, ids_after)


if __name__ == "__main__":
    # Test several users
    conn = sqlite3.connect(DB)
    user_ids = [r[0] for r in conn.execute(
        "SELECT user_id FROM user_surveys ORDER BY RANDOM() LIMIT 3"
    ).fetchall()]
    conn.close()
    
    results = []
    for uid in user_ids:
        result = test_user(uid)
        if result:
            results.append(result)
    
    print_sep("SUMMARY")
    all_same = all(a == b for a, b in results)
    if all_same:
        print("⚠ RECOMMENDATIONS NEVER CHANGE after survey update!")
    else:
        overlap_total = sum(len(a & b) for a, b in results)
        total = sum(len(a) for a, _ in results)
        print(f"✓ Overall overlapping rate: {overlap_total}/{total} products")
    print()
