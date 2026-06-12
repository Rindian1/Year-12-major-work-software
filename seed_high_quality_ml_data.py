"""
Seed high-quality product interactions aligned with user survey preferences.
Creates realistic domain-aware interactions so Item-CF (0.3 weight) reinforces
user preferences instead of working against survey-based recommendations.
"""
import json
import random
import sqlite3
from datetime import datetime, timedelta

random.seed(42)

DB_PATH = "instance/cart.db"

ACTION_WEIGHTS = {"view": 1.0, "like": 2.0, "add_to_cart": 3.0, "purchase": 5.0}

TARGET_INTERACTIONS_PER_USER = 3
MAX_INTERACTIONS_BEFORE_SKIP = 10

GENRE_PRODUCT_MAP = {
    "rock": [1, 2, 5, 8, 12, 16, 25, 26, 27, 31, 33, 37, 38, 46, 50, 56],
    "blues": [1, 2, 5, 8, 12, 15, 25, 26, 28, 33, 39, 46, 57, 60, 73],
    "jazz": [11, 28, 34, 39, 61, 73, 76, 77, 78, 79, 82, 83],
    "classical": [3, 6, 11, 29, 30, 41, 70, 77, 83, 85],
    "metal": [2, 8, 10, 16, 27, 31, 32, 42, 44, 46, 47, 48, 50, 56, 62],
    "pop": [1, 5, 6, 7, 13, 17, 26, 30, 33, 35, 55, 58, 60, 64, 73, 80],
    "country": [1, 3, 5, 6, 9, 15, 16, 29, 30, 35, 57, 65, 69, 71],
    "folk": [3, 6, 9, 29, 30, 41, 65, 69, 70, 71],
    "indie": [9, 13, 14, 29, 41, 55, 64, 65, 70, 71, 85, 90, 102],
}

ACTIONS = ["view", "view", "view", "like", "like", "add_to_cart"]


def get_connected_products(db, user_survey):
    """Find product IDs that match a user's survey profile."""
    c = db.cursor()
    skill = user_survey.get("skill_level", "intermediate")
    inst = user_survey.get("instrument_type", "both")
    genres = user_survey.get("preferred_genres", [])

    skill_order = {"beginner": 0, "intermediate": 1, "advanced": 2, "professional": 3}
    user_skill_level = skill_order.get(skill, 1)

    results = set()
    for g in genres:
        for pid in GENRE_PRODUCT_MAP.get(g, []):
            results.add(pid)

    c.execute("SELECT id, skill_level, instrument_type, genre_suitability FROM products")
    all_products = c.fetchall()

    scored = []
    for pid, p_skill, p_inst, p_genres_str in all_products:
        if pid in results or not results:
            p_skill_level = skill_order.get(p_inst, 1)
            if p_skill and skill_order.get(p_skill, 1) <= user_skill_level + 1:
                p_inst_clean = (p_inst or "").lower()
                u_inst_clean = inst.lower()
                if u_inst_clean == "both" or p_inst_clean == "both" or u_inst_clean == p_inst_clean:
                    genre_overlap = 0
                    try:
                        p_genres = json.loads(p_genres_str) if p_genres_str else []
                        genre_overlap = len(set(genres) & set(p_genres))
                    except (json.JSONDecodeError, TypeError):
                        pass
                    scored.append((pid, genre_overlap))

    scored.sort(key=lambda x: -x[1])
    return [pid for pid, _ in scored[:20]]


def main():
    random.seed(42)
    db = sqlite3.connect(DB_PATH)
    c = db.cursor()

    c.execute("""
        SELECT u.id, us.skill_level, us.instrument_type, us.preferred_genres
        FROM users u
        INNER JOIN user_surveys us ON u.id = us.user_id
    """)

    all_users = []
    for row in c.fetchall():
        try:
            genres = json.loads(row[3]) if row[3] else []
        except (json.JSONDecodeError, TypeError):
            genres = []
        all_users.append({
            "id": row[0],
            "skill_level": row[1],
            "instrument_type": row[2],
            "preferred_genres": genres,
        })

    c.execute("SELECT user_id, COUNT(*) FROM product_interactions GROUP BY user_id")
    existing_counts = dict(c.fetchall())

    total_new = 0
    now = datetime.utcnow()

    for u in all_users:
        uid = u["id"]
        existing = existing_counts.get(uid, 0)
        if existing >= MAX_INTERACTIONS_BEFORE_SKIP:
            continue

        need = TARGET_INTERACTIONS_PER_USER
        if random.random() < 0.3:
            need = 4 + random.randint(0, 2)
        elif random.random() < 0.5:
            need = 2

        need = min(need, MAX_INTERACTIONS_BEFORE_SKIP - existing)
        if need <= 0:
            continue

        candidates = get_connected_products(db, u)
        if not candidates:
            continue

        c.execute(
            "SELECT product_id FROM product_interactions WHERE user_id = ?",
            (uid,),
        )
        existing_pids = {r[0] for r in c.fetchall()}

        candidates = [pid for pid in candidates if pid not in existing_pids]
        if not candidates:
            continue

        chosen = random.sample(candidates, min(need, len(candidates)))

        for pid in chosen:
            action = random.choice(ACTIONS)
            ts = (now - timedelta(days=random.randint(0, 60))).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            freq = 1 if random.random() < 0.7 else 2

            c.execute(
                """INSERT OR IGNORE INTO product_interactions
                   (user_id, product_id, action, timestamp, frequency)
                   VALUES (?, ?, ?, ?, ?)""",
                (uid, pid, action, ts, freq),
            )
            if c.rowcount:
                total_new += 1

        if total_new % 50 == 0 and total_new > 0:
            db.commit()

    db.commit()
    db.close()

    print(f"Seeded {total_new} new domain-aware interactions.")
    print(f"Now running refresh() to update ML model...")

    from ml_recommender import reset_hybrid_recommender_for_tests, get_hybrid_recommender
    reset_hybrid_recommender_for_tests()
    hr = get_hybrid_recommender(DB_PATH)
    hr.refresh()

    print("ML model refreshed with new interaction data.")


if __name__ == "__main__":
    main()
