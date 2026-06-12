"""
Fix ML data quality issues discovered by diagnose_deep.py:
1. Add metadata (skill_level, instrument_type, genre_suitability) to 24 legacy products
2. Normalize categories to match ML model expectations
3. Fix accessories with NULL metadata
4. Rebalance hybrid weights in config.py
"""
import json
import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "instance", "cart.db")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "ml", "config.py")

LEGACY_METADATA = {
    1: {"skill": "intermediate", "inst": "electric", "genres": ["rock", "blues", "pop", "country"]},
    2: {"skill": "advanced", "inst": "electric", "genres": ["rock", "blues", "hard_rock", "metal"]},
    3: {"skill": "professional", "inst": "acoustic", "genres": ["folk", "country", "classical"]},
    4: {"skill": "intermediate", "inst": "electric", "genres": ["rock", "blues", "funk", "pop"]},
    5: {"skill": "intermediate", "inst": "electric", "genres": ["country", "rock", "blues", "pop"]},
    6: {"skill": "professional", "inst": "acoustic", "genres": ["folk", "pop", "country", "classical"]},
    7: {"skill": "advanced", "inst": "electric", "genres": ["rock", "blues", "jazz", "pop"]},
    8: {"skill": "intermediate", "inst": "electric", "genres": ["hard_rock", "rock", "blues", "metal"]},
    9: {"skill": "beginner", "inst": "acoustic", "genres": ["folk", "country", "indie"]},
    10: {"skill": "beginner", "inst": "electric", "genres": ["rock", "blues", "metal"]},
    11: {"skill": "professional", "inst": "both", "genres": ["jazz", "ambient", "classical", "pop"]},
    12: {"skill": "beginner", "inst": "electric", "genres": ["rock", "blues", "pop"]},
    13: {"skill": "beginner", "inst": "both", "genres": ["pop", "rock", "indie"]},
    14: {"skill": "intermediate", "inst": "electric", "genres": ["rock", "pop", "indie", "alternative"]},
    15: {"skill": "intermediate", "inst": "electric", "genres": ["rock", "blues", "country", "pop"]},
    16: {"skill": "intermediate", "inst": "electric", "genres": ["rock", "metal", "hard_rock"]},
    17: {"skill": "beginner", "inst": "electric", "genres": ["rock", "pop", "metal"]},
    18: {"skill": "beginner", "inst": "both", "genres": []},
    19: {"skill": "beginner", "inst": "electric", "genres": []},
    20: {"skill": "beginner", "inst": "both", "genres": []},
    21: {"skill": "beginner", "inst": "both", "genres": []},
    22: {"skill": "beginner", "inst": "both", "genres": []},
    23: {"skill": "beginner", "inst": "both", "genres": []},
    24: {"skill": "beginner", "inst": "electric", "genres": []},
}

CATEGORY_MAP = {
    "electric": "guitars",
    "acoustic": "guitars",
    "bass": "guitars",
    "acoustic-electric": "guitars",
    "acoustic_electric": "guitars",
    "pedal": "effects",
    "amplifier": "amplifiers",
    "accessory": "accessories",
    "case": "accessories",
}

def fix_products(db):
    c = db.cursor()

    print("=== Fix 1: Metadata for legacy products (ID 1-24) ===")
    for pid, meta in LEGACY_METADATA.items():
        genres_json = json.dumps(meta["genres"])
        c.execute(
            "UPDATE products SET skill_level=?, instrument_type=?, genre_suitability=? WHERE id=?",
            (meta["skill"], meta["inst"], genres_json, pid),
        )
        print(f"  ID {pid}: skill={meta['skill']}, inst={meta['inst']}, genres={genres_json}")

    print("\n=== Fix 2: Normalize categories ===")
    for old_cat, new_cat in CATEGORY_MAP.items():
        c.execute("UPDATE products SET category=? WHERE LOWER(category)=?", (new_cat, old_cat))
        count = c.rowcount
        if count:
            print(f"  {old_cat} -> {new_cat}: {count} products updated")

    print("\n=== Fix 3: Set default metadata for accessories with NULL values ===")
    c.execute("""
        UPDATE products
        SET skill_level = COALESCE(skill_level, 'beginner'),
            instrument_type = COALESCE(instrument_type, 'both')
        WHERE LOWER(category) = 'accessories'
        AND (skill_level IS NULL OR instrument_type IS NULL)
    """)
    print(f"  Fixed {c.rowcount} accessories with NULL skill_level/instrument_type")

    c.execute("""
        UPDATE products
        SET skill_level = COALESCE(skill_level, 'beginner'),
            instrument_type = COALESCE(instrument_type, 'both')
        WHERE LOWER(category) = 'accessories'
        AND (skill_level IS NULL OR instrument_type IS NULL)
    """)
    print(f"  Fixed {c.rowcount} accessories with NULL skill_level/instrument_type")

    db.commit()
    print("\nAll product fixes committed.")

def verify_fixes(db):
    c = db.cursor()
    print("\n=== Verification ===")
    c.execute("""
        SELECT id, name, category, skill_level, instrument_type
        FROM products
        WHERE id <= 25
        ORDER BY id
    """)
    for row in c.fetchall():
        print(f"  ID={row[0]:2d} | {row[1]:35s} | cat={str(row[2]):15s} | skill={str(row[3]):15s} | inst={str(row[4]):15s}")

    c.execute("SELECT COUNT(*) FROM products WHERE skill_level IS NULL OR instrument_type IS NULL OR genre_suitability IS NULL")
    missing = c.fetchone()[0]
    print(f"\nProducts still missing metadata: {missing}")

    c.execute("""
        SELECT DISTINCT LOWER(category)
        FROM products
        WHERE LOWER(category) NOT IN ('guitars', 'amplifiers', 'effects', 'accessories')
    """)
    bad = [r[0] for r in c.fetchall()]
    if bad:
        print(f"Products with non-standard categories: {bad}")
    else:
        print("All categories normalized to standard ML categories.")


def update_config():
    print("\n=== Fix 4: Rebalance hybrid weights ===")
    with open(CONFIG_PATH, "r") as f:
        content = f.read()

    old_weights = "USER_CF_WEIGHT = 0.3\nITEM_CF_WEIGHT = 0.5\nCONTENT_WEIGHT = 0.2"
    new_weights = "USER_CF_WEIGHT = 0.3\nITEM_CF_WEIGHT = 0.3\nCONTENT_WEIGHT = 0.4"
    if old_weights in content:
        content = content.replace(old_weights, new_weights)
        with open(CONFIG_PATH, "w") as f:
            f.write(content)
        print("  Updated: CONTENT_WEIGHT 0.2 -> 0.4, ITEM_CF_WEIGHT 0.5 -> 0.3")
    else:
        print("  Config already updated or format changed - skipping.")


if __name__ == "__main__":
    print(f"Database: {DB_PATH}")
    print(f"Config:   {CONFIG_PATH}")
    db = sqlite3.connect(DB_PATH)
    try:
        fix_products(db)
        verify_fixes(db)
    finally:
        db.close()
    update_config()
    print("\nDone. Run `python3 diagnose_ml_system.py` to verify improvements.")
