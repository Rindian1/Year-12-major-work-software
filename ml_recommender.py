"""
Hybrid KNN recommender: user-CF + item-CF + content-based.
Used by Flask `get_recommendations`; keeps heavy matrices in memory after `refresh()`.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

from ml.config import (
    CONTENT_WEIGHT,
    ITEM_CF_WEIGHT,
    MAX_RECOMMENDATIONS,
    USER_CF_WEIGHT,
)
from ml.data_loader import DataLoader
from ml.feature_engineering import FeatureEngineer
from ml.knn_models import (
    ContentBasedRecommender,
    KNNItemRecommender,
    KNNUserRecommender,
)

_hybrid_lock = threading.Lock()
_hybrid_instance: Optional["HybridRecommender"] = None


def get_hybrid_recommender(db_path: str) -> "HybridRecommender":
    """Process-wide singleton; call `refresh()` after survey/cart changes."""
    global _hybrid_instance
    with _hybrid_lock:
        if _hybrid_instance is None:
            h = HybridRecommender(db_path)
            h.refresh()
            _hybrid_instance = h
        return _hybrid_instance


def reset_hybrid_recommender_for_tests() -> None:
    global _hybrid_instance
    with _hybrid_lock:
        _hybrid_instance = None


def _minmax_norm(scores: Dict[int, float]) -> Dict[int, float]:
    if not scores:
        return {}
    vals = list(scores.values())
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-12:
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def _redistribute_weights(
    w_u: float, w_i: float, w_c: float, has_u: bool, has_i: bool, has_c: bool
) -> Tuple[float, float, float]:
    wu, wi, wc = w_u, w_i, w_c
    if not has_u:
        wu = 0.0
    if not has_i:
        wi = 0.0
    if not has_c:
        wc = 0.0
    s = wu + wi + wc
    if s < 1e-12:
        return 0.0, 0.0, 1.0
    return wu / s, wi / s, wc / s


def _build_reason(
    user_part: float,
    item_part: float,
    content_part: float,
    content_reason: str,
    user_frag: str,
    item_frag: str,
) -> str:
    parts = [
        (user_part, user_frag),
        (item_part, item_frag),
        (content_part, content_reason),
    ]
    dom = max(parts, key=lambda x: x[0])
    text = dom[1]
    if len(text) > 118:
        text = text[:115] + "..."
    return text


class HybridRecommender:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._loader = DataLoader(db_path)
        self._fe = FeatureEngineer()
        self._content = ContentBasedRecommender()
        self._user_knn = KNNUserRecommender()
        self._item_knn = KNNItemRecommender()
        self._products_df: Optional[pd.DataFrame] = None
        self._user_ids: List[int] = []
        self._product_ids: List[int] = []
        self._inter: Optional[np.ndarray] = None
        self._popularity: Dict[int, float] = {}
        self.last_refresh_iso: Optional[str] = None
        self.last_error: Optional[str] = None

    def refresh(self) -> None:
        """Reload all matrices from SQLite and refit KNN indices."""
        self.last_error = None
        try:
            users_df = self._loader.load_users_with_surveys()
            products_df = self._loader.load_products()
            if users_df.empty or products_df.empty:
                self._user_ids = []
                self._product_ids = []
                self._inter = None
                self._products_df = products_df
                self.last_refresh_iso = datetime.now(timezone.utc).isoformat()
                return

            self._user_ids = users_df["user_id"].astype(int).tolist()
            self._product_ids = products_df["id"].astype(int).tolist()
            self._inter = self._loader.load_user_interaction_matrix(
                self._user_ids, self._product_ids
            ).values
            self._products_df = products_df

            interactions = self._loader.load_interactions()
            if not interactions.empty:
                cnt = interactions.groupby("product_id").size()
                mx = float(cnt.max()) if len(cnt) else 1.0
                self._popularity = {int(k): float(v) / mx for k, v in cnt.items()}
            else:
                self._popularity = {}

            user_survey_scaled, _, _ = self._fe.build_user_feature_matrix(users_df)
            X_user = self._fe.build_user_knn_matrix(user_survey_scaled, self._inter)
            self._user_knn.fit(X_user, self._user_ids, self._inter, self._product_ids)
            self._item_knn.fit(self._inter, self._product_ids)
            self.last_refresh_iso = datetime.now(timezone.utc).isoformat()
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            raise

    def _user_interaction_weight(self, user_id: int) -> float:
        if self._inter is None or user_id not in self._user_ids:
            return 0.0
        idx = self._user_ids.index(user_id)
        return float(self._inter[idx].sum())

    def get_recommendations(self, user_id: int, n: int = MAX_RECOMMENDATIONS) -> List[Dict[str, Any]]:
        """Return API-shaped dicts; scores in [0, 1]."""
        if self._products_df is None or self._inter is None:
            try:
                self.refresh()
            except Exception:  # noqa: BLE001
                return []

        survey = self._loader.get_user_survey(user_id)
        if not survey:
            return []

        exclude = self._loader.get_exclude_product_ids(user_id)
        products_df = self._products_df
        if products_df is None or self._inter is None:
            return []

        try:
            user_idx = self._user_ids.index(user_id)
        except ValueError:
            user_idx = -1

        user_w = self._user_interaction_weight(user_id) if user_idx >= 0 else 0.0
        w_u, w_i, w_c = USER_CF_WEIGHT, ITEM_CF_WEIGHT, CONTENT_WEIGHT
        if user_w < 5:
            # Low interaction: rely more on content & item-based recommendations
            w_u, w_i, w_c = 0.2, 0.3, 0.5
        elif user_w > 80:
            # High interaction: heavily favor item-based (recently viewed) & user-based recommendations
            w_u, w_i, w_c = 0.2, 0.5, 0.3

        raw_user = self._user_knn.recommend(user_id, top_n=40) if len(self._user_ids) > 1 else {}
        raw_item: Dict[int, Tuple[float, str]] = {}
        if user_idx >= 0:
            raw_item = self._item_knn.recommend(user_idx, self._inter, top_n=40)

        raw_content = self._content.recommend(survey, products_df, exclude)

        nu = {k: v[0] for k, v in raw_user.items()}
        ni = {k: v[0] for k, v in raw_item.items()}
        nc = {k: v[0] for k, v in raw_content.items()}
        reason_u = next(iter(raw_user.values()), ("", "Popular with similar shoppers"))[1]
        reason_i = next(iter(raw_item.values()), ("", "Similar to your browsing"))[1]
        # default content reason
        reason_c = "Matches your preferences"
        if raw_content:
            reason_c = next(iter(raw_content.values()))[1]

        nu_n = _minmax_norm(nu)
        ni_n = _minmax_norm(ni)
        nc_n = _minmax_norm(nc)

        has_u, has_i, has_c = bool(nu_n), bool(ni_n), bool(nc_n)
        wu, wi, wc = _redistribute_weights(w_u, w_i, w_c, has_u, has_i, has_c)

        candidates: Set[int] = set(nu_n) | set(ni_n) | set(nc_n)
        if not candidates:
            return []

        final: List[Tuple[int, float, str, int]] = []
        for pid in candidates:
            if pid in exclude:
                continue
            row = products_df.loc[products_df["id"] == pid]
            if row.empty:
                continue
            r0 = row.iloc[0]
            if int(r0.get("stock") or 0) <= 0:
                continue

            u_part = wu * nu_n.get(pid, 0.0)
            i_part = wi * ni_n.get(pid, 0.0)
            c_part = wc * nc_n.get(pid, 0.0)
            pop_boost = 0.05 * self._popularity.get(pid, 0.0)
            acoustic_boost = 0.0
            if (survey.get("instrument_type") or "").lower() == "acoustic":
                p_cat = (r0.get("category") or "").lower()
                p_inst = (r0.get("instrument_type") or "").lower()
                if p_cat == "guitars" and p_inst == "acoustic":
                    acoustic_boost = 0.15
            score = min(1.0, u_part + i_part + c_part + pop_boost + acoustic_boost)

            cr = raw_content.get(pid, (0.0, reason_c))[1]
            ur = raw_user.get(pid, (0.0, reason_u))[1]
            ir = raw_item.get(pid, (0.0, reason_i))[1]
            reason = _build_reason(u_part, i_part, c_part, cr, ur, ir)

            genre_overlap = 0
            u_genres = {g.lower() for g in survey.get("preferred_genres") or []}
            p_genres = set()
            if isinstance(r0.get("genres_list"), list):
                p_genres = {str(x).lower() for x in r0["genres_list"]}
            genre_overlap = len(u_genres & p_genres)

            final.append((pid, score, reason, genre_overlap))

        def _tie_price(t: Tuple[int, float, str, int]) -> float:
            pr = products_df.loc[products_df["id"] == t[0], "price"]
            return float(pr.iloc[0] or 0) if not pr.empty else 0.0

        final.sort(key=lambda x: (-x[1], -x[3], _tie_price(x)))

        out: List[Dict[str, Any]] = []
        for pid, score, reason, _ in final[:n]:
            row = products_df.loc[products_df["id"] == pid].iloc[0]
            out.append(
                {
                    "id": int(pid),
                    "name": str(row["name"]),
                    "category": str(row["category"]),
                    "price": float(row["price"] or 0),
                    "image_url": row["image_url"],
                    "score": float(round(score, 4)),
                    "reason": reason,
                }
            )
        return out
