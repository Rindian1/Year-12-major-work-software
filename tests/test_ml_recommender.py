"""Unit tests for ML recommender (stdlib unittest, no pytest required)."""

import json
import sqlite3
import unittest
from pathlib import Path
import tempfile

import pandas as pd

from ml.feature_engineering import encode_user_survey_row
from ml_recommender import HybridRecommender, reset_hybrid_recommender_for_tests


def _create_fixture_db(path: str) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL
        );
        CREATE TABLE user_surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_level VARCHAR(20) NOT NULL,
            instrument_type VARCHAR(20) NOT NULL,
            preferred_genres TEXT NOT NULL
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL,
            description TEXT,
            image_url TEXT,
            skill_level VARCHAR(20),
            genre_suitability TEXT,
            instrument_type VARCHAR(20),
            price_range VARCHAR(20)
        );
        CREATE TABLE product_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            action VARCHAR(20) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration INTEGER DEFAULT 0,
            frequency INTEGER DEFAULT 1
        );
        """
    )
    conn.execute("INSERT INTO users (username) VALUES ('a'), ('b')")
    conn.execute(
        """INSERT INTO user_surveys (user_id, skill_level, instrument_type, preferred_genres)
           VALUES (1, 'beginner', 'electric', ?),
                  (2, 'beginner', 'electric', ?)""",
        (json.dumps(["rock"]), json.dumps(["rock"])),
    )
    conn.execute(
        """INSERT INTO products (name, category, price, stock, skill_level, genre_suitability, instrument_type, price_range)
           VALUES ('P1', 'guitars', 400, 2, 'beginner', ?, 'electric', 'under_500'),
                  ('P2', 'guitars', 450, 1, 'beginner', ?, 'electric', 'under_500'),
                  ('P3', 'effects', 80, 5, 'beginner', ?, 'electric', 'under_500')""",
        (
            json.dumps(["rock"]),
            json.dumps(["rock"]),
            json.dumps(["blues"]),
        ),
    )
    conn.execute(
        """INSERT INTO product_interactions (user_id, product_id, action, frequency)
           VALUES (2, 1, 'purchase', 1), (2, 2, 'view', 1), (1, 1, 'view', 2)"""
    )
    conn.commit()
    conn.close()


class TestMLRecommender(unittest.TestCase):
    def tearDown(self):
        reset_hybrid_recommender_for_tests()

    def test_encode_user_survey_vector_length(self):
        row = pd.Series(
            {
                "skill_level": "beginner",
                "instrument_type": "electric",
                "preferred_genres": ["rock"],
            }
        )
        v = encode_user_survey_row(row)
        self.assertEqual(v.shape, (13,))
        self.assertEqual(v[1 + 1], 1.0)

    def test_hybrid_returns_recommendations(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "t.db")
            _create_fixture_db(db_path)
            h = HybridRecommender(db_path)
            h.refresh()
            recs = h.get_recommendations(1, n=10)
            self.assertTrue(len(recs) >= 1)
            for r in recs:
                self.assertIn("id", r)
                self.assertIn("score", r)
                self.assertIn("reason", r)
                self.assertIsInstance(r["price"], float)
            ids = {r["id"] for r in recs}
            self.assertTrue(ids.issubset({1, 2, 3}))


if __name__ == "__main__":
    unittest.main()
