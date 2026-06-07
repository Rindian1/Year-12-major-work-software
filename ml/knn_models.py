"""KNN user-CF, item-CF, and content-based recommenders."""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from ml.config import (
    ITEM_CF_MIN_USER_WEIGHT,
    ITEM_N_NEIGHBORS,
    ITEM_SEED_TOP,
    N_NEIGHBORS,
)
from ml.feature_engineering import GENRES, SKILL_ORDER, encode_user_survey_row


def _minmax_norm(scores: Dict[int, float]) -> Dict[int, float]:
    if not scores:
        return {}
    vals = list(scores.values())
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-12:
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}




def _instrument_allowed(u_inst: str, p_inst: str) -> bool:
    u = (u_inst or "").lower()
    p = (p_inst or "").lower()
    if not u or not p:
        return True
    return u == "both" or p == "both" or u == p


def _instrument_match_score(u_inst: str, p_inst: str) -> float:
    if _instrument_allowed(u_inst, p_inst):
        return 1.0
    return 0.4


def _skill_compat(u_skill: str, p_skill: str) -> float:
    uo = SKILL_ORDER.get((u_skill or "").lower(), 1)
    po = SKILL_ORDER.get((p_skill or "").lower(), 1)
    diff = abs(uo - po)
    if diff == 0:
        return 1.0
    if diff == 1:
        return 0.85
    if po == 0 and uo > po:
        return 0.72
    if uo > po + 1:
        return 0.35
    return 0.55


def _genre_oh_from_set(gset: set) -> np.ndarray:
    vec = np.zeros(len(GENRES), dtype=np.float64)
    for i, g in enumerate(GENRES):
        if g in gset:
            vec[i] = 1.0
    return vec


def _instrument_oh_static(inst: str | None) -> np.ndarray:
    from ml.feature_engineering import INSTRUMENT_ORDER

    vec = np.zeros(3, dtype=np.float64)
    key = str(inst or "").lower()
    if key in INSTRUMENT_ORDER:
        vec[INSTRUMENT_ORDER.index(key)] = 1.0
    else:
        vec[:] = 1.0 / 3.0
    return vec


def _skill_value_static(skill: str | None) -> float:
    v = SKILL_ORDER.get(str(skill or "").lower(), 1)
    return v / 3.0




class ContentBasedRecommender:
    def recommend(
        self,
        user_survey: dict,
        products_df: pd.DataFrame,
        exclude: Set[int],
    ) -> Dict[int, Tuple[float, str]]:
        u_genres = {g.lower() for g in user_survey.get("preferred_genres") or []}
        out: Dict[int, Tuple[float, str]] = {}
        u_series = pd.Series(user_survey)
        u_vec = encode_user_survey_row(u_series)

        for _, row in products_df.iterrows():
            pid = int(row["id"])
            if pid in exclude:
                continue
            stock = int(row["stock"] or 0)
            if stock <= 0:
                continue
            if not _instrument_allowed(
                user_survey.get("instrument_type") or "",
                row.get("instrument_type") or "",
            ):
                continue

            p_genres: set = set()
            gs = row.get("genres_list")
            if isinstance(gs, list):
                p_genres = {str(x).lower() for x in gs}
            elif row.get("genre_suitability"):
                try:
                    p_genres = {str(x).lower() for x in json.loads(row["genre_suitability"])}
                except (json.JSONDecodeError, TypeError):
                    p_genres = set()

            overlap = len(u_genres & p_genres) / max(len(u_genres), 1)
            inst = _instrument_match_score(
                user_survey.get("instrument_type") or "",
                row.get("instrument_type") or "",
            )
            sk = _skill_compat(
                user_survey.get("skill_level") or "",
                row.get("skill_level") or "",
            )

            p_vec = np.concatenate(
                [
                    np.array([_skill_value_static(row.get("skill_level"))]),
                    _instrument_oh_static(row.get("instrument_type")),
                    _genre_oh_from_set(p_genres),
                ]
            )
            cos = float(
                np.dot(u_vec, p_vec) / (np.linalg.norm(u_vec) * np.linalg.norm(p_vec) + 1e-9)
            )

            score = (
                0.39 * overlap  # increased from 0.32
                + 0.27 * inst  # increased from 0.22
                + 0.22 * sk    # increased from 0.18
                + 0.12 * max(0.0, min(1.0, cos))  # increased from 0.10
            )
            reason = "Matches your genres, skill level, and instrument type"
            if overlap >= 0.5:
                reason = "Strong genre match for your preferences"
            elif inst >= 0.99:
                reason = "Fits your instrument type perfectly"
            out[pid] = (score, reason)
        return out


class KNNUserRecommender:
    def __init__(self, n_neighbors: int = N_NEIGHBORS):
        self.n_neighbors = n_neighbors
        self._nn: Optional[NearestNeighbors] = None
        self._user_ids: List[int] = []
        self._product_ids: List[int] = []
        self._inter: Optional[np.ndarray] = None
        self._X: Optional[np.ndarray] = None

    def fit(
        self,
        X: np.ndarray,
        user_ids: List[int],
        interaction_matrix: np.ndarray,
        product_ids: List[int],
    ) -> None:
        self._X = np.asarray(X, dtype=np.float64)
        self._user_ids = list(user_ids)
        self._product_ids = list(product_ids)
        self._inter = np.asarray(interaction_matrix, dtype=np.float64)
        n = len(user_ids)
        k = min(max(1, min(self.n_neighbors + 1, n)), n)
        self._nn = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")
        self._nn.fit(self._X)

    def recommend(self, user_id: int, top_n: int = 30) -> Dict[int, Tuple[float, str]]:
        if self._nn is None or self._inter is None or self._X is None:
            return {}
        try:
            idx = self._user_ids.index(user_id)
        except ValueError:
            return {}
        dist, ind = self._nn.kneighbors(X=self._X[idx : idx + 1], return_distance=True)
        scores: Dict[int, float] = {}
        for j, nb in enumerate(ind[0]):
            d = float(dist[0][j])
            if self._user_ids[nb] == user_id:
                continue
            w = 1.0 / (d + 1e-9)
            row = self._inter[nb]
            for col, val in enumerate(row):
                if val <= 0:
                    continue
                pid = self._product_ids[col]
                scores[pid] = scores.get(pid, 0.0) + w * float(val)
        top = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
        frag = "Popular with shoppers who have similar tastes"
        return {pid: (sc, frag) for pid, sc in top}


class KNNItemRecommender:
    def __init__(self, n_neighbors: int = ITEM_N_NEIGHBORS):
        self.n_neighbors = n_neighbors
        self._nn: Optional[NearestNeighbors] = None
        self._item_rows: Optional[np.ndarray] = None
        self._product_ids: List[int] = []

    def fit(self, interaction_matrix: np.ndarray, product_ids: List[int]) -> None:
        self._product_ids = list(product_ids)
        m = np.asarray(interaction_matrix, dtype=np.float64).T
        norms = np.linalg.norm(m, axis=1, keepdims=True) + 1e-9
        self._item_rows = m / norms
        n_items = len(product_ids)
        k = min(max(1, self.n_neighbors), n_items)
        self._nn = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")
        self._nn.fit(self._item_rows)

    def recommend(
        self,
        user_idx: int,
        interaction_matrix: np.ndarray,
        top_n: int = 30,
        min_seed_weight: float = ITEM_CF_MIN_USER_WEIGHT,
    ) -> Dict[int, Tuple[float, str]]:
        if self._nn is None or self._item_rows is None:
            return {}
        urow = np.asarray(interaction_matrix[user_idx], dtype=np.float64)
        if urow.max() < 1e-9:
            return {}
        seed_idx = np.argsort(-urow)[:ITEM_SEED_TOP]
        seeds = [(int(i), float(urow[i])) for i in seed_idx if urow[i] >= min_seed_weight]
        if not seeds:
            seeds = [(int(i), float(urow[i])) for i in seed_idx[:2] if urow[i] > 0]
        if not seeds:
            return {}
        scores: Dict[int, float] = {}
        for s, w_seed in seeds:
            if s >= len(self._product_ids):
                continue
            vec = self._item_rows[s : s + 1]
            dist, ind = self._nn.kneighbors(vec, return_distance=True)
            for j, nb in enumerate(ind[0]):
                d = float(dist[0][j])
                sim = max(0.0, 1.0 - d)
                if nb == s:
                    continue
                pid = self._product_ids[nb]
                scores[pid] = scores.get(pid, 0.0) + sim * w_seed
        top = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
        frag = "Similar to items you browsed or saved"
        return {pid: (sc, frag) for pid, sc in top}
