"""Load recommendation training data from SQLite."""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Optional, Set

import pandas as pd

from ml.config import ACTION_WEIGHTS


def _parse_genres(raw: Any) -> list:
    if raw is None or raw == "":
        return []
    if isinstance(raw, list):
        return raw
    try:
        out = json.loads(raw)
        return out if isinstance(out, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


class DataLoader:
    """Read-only access to survey, product, and interaction tables."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def load_users_with_surveys(self) -> pd.DataFrame:
        sql = """
            SELECT u.id AS user_id, us.skill_level, us.instrument_type,
                   us.preferred_genres
            FROM users u
            INNER JOIN user_surveys us ON u.id = us.user_id
        """
        conn = self._connect()
        try:
            df = pd.read_sql_query(sql, conn)
        finally:
            conn.close()
        return df

    def load_products(self) -> pd.DataFrame:
        sql = """
            SELECT id, name, category, price, stock, description, image_url,
                   skill_level, genre_suitability, instrument_type, price_range
            FROM products
        """
        conn = self._connect()
        try:
            df = pd.read_sql_query(sql, conn)
        finally:
            conn.close()
        df["genres_list"] = df["genre_suitability"].apply(_parse_genres)
        return df

    def load_interactions(self) -> pd.DataFrame:
        sql = """
            SELECT user_id, product_id, action, timestamp, duration, frequency
            FROM product_interactions
            ORDER BY timestamp DESC
        """
        conn = self._connect()
        try:
            df = pd.read_sql_query(sql, conn)
        finally:
            conn.close()
        if df.empty:
            return df
        df["action"] = df["action"].astype(str)
        df["frequency"] = pd.to_numeric(df["frequency"], errors="coerce").fillna(1).astype(int)
        df["duration"] = pd.to_numeric(df["duration"], errors="coerce").fillna(0).astype(int)
        return df

    def load_user_interaction_matrix(self, user_ids: list, product_ids: list) -> pd.DataFrame:
        """
        Rows: user_id, Columns: product_id, values: aggregated action weights.
        """
        interactions = self.load_interactions()
        if interactions.empty:
            return pd.DataFrame(0.0, index=user_ids, columns=product_ids)

        def row_weight(row) -> float:
            w = ACTION_WEIGHTS.get(row["action"], 0)
            return float(w) * max(row["frequency"], 1)

        interactions = interactions.copy()
        interactions["_w"] = interactions.apply(row_weight, axis=1)
        interactions = interactions.sort_values("_w", ascending=False)
        interactions = interactions.drop_duplicates(subset=["user_id", "product_id"], keep="first")

        pivot = interactions.pivot_table(
            index="user_id",
            columns="product_id",
            values="_w",
            aggfunc="sum",
            fill_value=0.0,
        )
        pivot = pivot.reindex(index=user_ids, columns=product_ids, fill_value=0.0)
        return pivot

    def get_user_survey(self, user_id: int) -> Optional[dict]:
        sql = """
            SELECT skill_level, instrument_type, preferred_genres
            FROM user_surveys WHERE user_id = ?
        """
        conn = self._connect()
        try:
            row = conn.execute(sql, (user_id,)).fetchone()
        finally:
            conn.close()
        if not row:
            return None
        genres = _parse_genres(row["preferred_genres"])
        return {
            "skill_level": row["skill_level"],
            "instrument_type": row["instrument_type"],
            "preferred_genres": genres,
        }

    def get_exclude_product_ids(self, user_id: int) -> Set[int]:
        """Exclude products user purchased or added to cart (strong signals)."""
        sql = """
            SELECT DISTINCT product_id FROM product_interactions
            WHERE user_id = ? AND action IN ('purchase', 'add_to_cart')
        """
        conn = self._connect()
        try:
            rows = conn.execute(sql, (user_id,)).fetchall()
        finally:
            conn.close()
        return {int(r["product_id"]) for r in rows}
