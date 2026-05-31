"""Encode surveys and products into fixed-length numeric vectors."""

from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

GENRES: List[str] = [
    "rock",
    "blues",
    "jazz",
    "classical",
    "metal",
    "pop",
    "country",
    "folk",
    "indie",
]

SKILL_ORDER = {"beginner": 0, "intermediate": 1, "advanced": 2, "professional": 3}
INSTRUMENT_ORDER = ["acoustic", "electric", "both"]
BUDGET_ORDER = {
    "under_500": 0,
    "500_1000": 1,
    "1000_2000": 2,
    "2000_5000": 3,
    "over_5000": 4,
}
CATEGORIES = ["guitars", "amplifiers", "effects", "accessories"]

# Vector layout: skill(1) + instrument(3) + genres(9) + budget(1) + category(4) = 18
SURVEY_DIM = 1 + 3 + 9 + 1  # 14 — user survey has no category
PRODUCT_DIM = 1 + 3 + 9 + 1 + 4  # 18


def _skill_value(skill: str | None) -> float:
    if not skill:
        return 0.5
    v = SKILL_ORDER.get(str(skill).lower(), 1)
    return v / 3.0


def _budget_value(budget: str | None) -> float:
    if not budget:
        return 0.5
    v = BUDGET_ORDER.get(str(budget).lower(), 2)
    return v / 4.0


def _instrument_onehot(inst: str | None) -> np.ndarray:
    vec = np.zeros(3, dtype=np.float64)
    if not inst:
        vec[:] = 1.0 / 3.0
        return vec
    key = str(inst).lower()
    if key in INSTRUMENT_ORDER:
        vec[INSTRUMENT_ORDER.index(key)] = 1.0
    else:
        vec[:] = 1.0 / 3.0
    return vec


def _genre_onehot(genres: Iterable[str]) -> np.ndarray:
    vec = np.zeros(len(GENRES), dtype=np.float64)
    gset = {str(g).lower() for g in genres or []}
    for i, g in enumerate(GENRES):
        if g in gset:
            vec[i] = 1.0
    return vec


def _category_onehot(cat: str | None) -> np.ndarray:
    vec = np.zeros(len(CATEGORIES), dtype=np.float64)
    if not cat:
        vec[:] = 1.0 / len(CATEGORIES)
        return vec
    key = str(cat).lower()
    if key in CATEGORIES:
        vec[CATEGORIES.index(key)] = 1.0
    else:
        vec[:] = 1.0 / len(CATEGORIES)
    return vec


def encode_user_survey_row(row: pd.Series) -> np.ndarray:
    """14-dim vector: skill, instrument one-hot, genre one-hot, budget."""
    genres = row.get("preferred_genres")
    if isinstance(genres, str):
        import json

        try:
            genres = json.loads(genres)
        except (json.JSONDecodeError, TypeError):
            genres = []
    parts = [
        np.array([_skill_value(row.get("skill_level"))]),
        _instrument_onehot(row.get("instrument_type")),
        _genre_onehot(genres),
        np.array([_budget_value(row.get("budget_range"))]),
    ]
    return np.concatenate(parts)


def encode_product_row(row: pd.Series) -> np.ndarray:
    """18-dim vector including category."""
    genres = row.get("genres_list")
    if genres is None:
        genres = []
    parts = [
        np.array([_skill_value(row.get("skill_level"))]),
        _instrument_onehot(row.get("instrument_type")),
        _genre_onehot(genres),
        np.array([_budget_value(row.get("price_range"))]),
        _category_onehot(row.get("category")),
    ]
    return np.concatenate(parts)


class FeatureEngineer:
    def build_user_feature_matrix(
        self, users_df: pd.DataFrame
    ) -> Tuple[np.ndarray, List[int], StandardScaler]:
        user_ids = users_df["user_id"].astype(int).tolist()
        raw = np.stack([encode_user_survey_row(users_df.loc[i]) for i in users_df.index])
        scaler = StandardScaler()
        scaled = scaler.fit_transform(raw)
        return scaled, user_ids, scaler

    def build_product_feature_matrix(
        self, products_df: pd.DataFrame
    ) -> Tuple[np.ndarray, List[int], StandardScaler]:
        product_ids = products_df["id"].astype(int).tolist()
        raw = np.stack([encode_product_row(products_df.loc[i]) for i in products_df.index])
        scaler = StandardScaler()
        scaled = scaler.fit_transform(raw)
        return scaled, product_ids, scaler

    def build_user_knn_matrix(
        self,
        user_survey_scaled: np.ndarray,
        interaction_matrix: np.ndarray,
        eps: float = 1e-9,
    ) -> np.ndarray:
        """Concatenate scaled survey features with L2-normalized interaction rows."""
        norms = np.linalg.norm(interaction_matrix, axis=1, keepdims=True) + eps
        inter_norm = interaction_matrix / norms
        return np.hstack([user_survey_scaled, inter_norm])
