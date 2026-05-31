# KNN Machine Learning Recommendation System — Implementation Guide

This document provides step-by-step instructions for replacing the current simple survey-based recommendation system with a K-Nearest Neighbors (KNN) hybrid recommender in the Flask guitar e-commerce application. It does **not** include implementation code. For reference implementations and code samples, see `YEAR 12 MAJOR WORK planning files/machine-learning-implementation.md`.

**Project root:** `/Users/ryanbhandari/Year-12-major-work-software/`  
**Database:** `instance/cart.db` (SQLite)  
**Primary files to modify:** `app.py`, `templates/base.html`, `templates/index.html`, `requirements.txt`

---

## 1. Executive Summary

### What the ML system will do

The new system will generate personalized product recommendations by combining:

1. **User survey signals** — `skill_level`, `instrument_type`, `preferred_genres`, `budget_range` from `user_surveys`
2. **Behavioral signals** — weighted interactions from `product_interactions` (`view`, `like`, `add_to_cart`, `purchase`, `compare`)
3. **User–user collaborative filtering** — find similar users via KNN on user feature vectors, recommend products those neighbors engaged with
4. **Item–item collaborative filtering** — find similar products via KNN on product vectors, recommend items similar to ones the user already liked or purchased
5. **Content-based filtering** — match user preference vectors to product attribute vectors (genres, skill level, instrument type, price range)

Results will be ranked, explained in plain language, cached in `recommendation_cache`, and served through the existing `GET /api/recommendations/<user_id>` endpoint.

### Why KNN

- **Interpretable:** Neighbor distance and shared attributes support human-readable `reason` strings.
- **No separate training phase:** KNN is lazy learning; the “model” is the feature matrix refreshed from the database.
- **Fits current data scale:** Migrations `004_seed_ml_data.py`, `005_expand_ml_data.py`, and `006_seed_more_surveys.py` provide ~100 users, ~50 products, and 364+ interactions — enough for KNN without heavy infrastructure.
- **Composable:** User-based, item-based, and content-based scores can be blended with configurable weights.

### Expected benefits over the current system

The current `generate_simple_recommendations()` in `app.py` (lines 966–1020):

- Uses a SQL filter plus `ORDER BY RANDOM()` — not personalized beyond coarse filters
- Ignores `product_interactions` entirely
- Assigns a mostly static score (0.8 base + small genre/skill tweaks)
- Does not use collaborative filtering

The KNN system should improve relevance, diversity, explainability, and engagement while reusing existing tables, API shape, and dashboard UI.

---

## 2. Prerequisites and Dependencies

### Python packages to add

Add these to `requirements.txt` (currently only Flask and related packages — no ML libraries):

| Package | Purpose |
|---------|---------|
| `scikit-learn` | `NearestNeighbors`, distance metrics, optional `StandardScaler` |
| `pandas` | DataFrames for matrices and joins |
| `numpy` | Numerical arrays and vector math |
| `joblib` (optional) | Persist fitted scalers or neighbor indices to disk |

Pin versions compatible with Python 3.10+ (e.g. `scikit-learn>=1.3.0`, `pandas>=2.0.0`, `numpy>=1.24.0`).

### Installation steps

1. Activate the project virtual environment (`.venv/`).
2. Run `pip install -r requirements.txt` after updating the file.
3. Verify imports in a Python shell: `sklearn`, `pandas`, `numpy` load without error.

### System requirements

- Same environment as the Flask app (macOS/Linux; SQLite file access)
- Sufficient RAM for in-memory matrices (~100 users × 50 products is trivial; plan for 10× growth)
- No GPU required
- Optional: `joblib` model directory under `instance/` (e.g. `instance/ml_models/`) — add to `.gitignore` if models contain derived user data

### Database prerequisites

Ensure migrations have been run:

```bash
python migrations/003_create_survey_tables_fixed.py
python migrations/004_seed_ml_data.py
python migrations/005_expand_ml_data.py
python migrations/006_seed_more_surveys.py
```

Confirm tables exist: `user_surveys`, `recommendation_cache`, `product_interactions`, and guitar columns on `products` (`skill_level`, `genre_suitability`, `instrument_type`, `price_range`).

---

## 3. Architecture Overview

### High-level architecture (text diagram)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Application (app.py)                │
├─────────────────────────────────────────────────────────────────┤
│  Routes: /survey, POST /api/user/survey,                        │
│          GET /api/recommendations/<user_id>, /product/<id>       │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             ▼                               ▼
┌────────────────────────┐      ┌────────────────────────────────┐
│  SQLite (cart.db)      │      │  ml_recommender.py (new)        │
│  - user_surveys        │◄────►│  - DataLoader                   │
│  - products            │      │  - FeatureEngineer              │
│  - product_interactions│      │  - KNNUserRecommender           │
│  - recommendation_cache│      │  - KNNItemRecommender           │
│  - recently_viewed     │      │  - ContentBasedRecommender      │
│                        │      │  - HybridRecommender            │
└────────────────────────┘      └────────────────────────────────┘
             ▲                               │
             │                               ▼
┌────────────────────────┐      ┌────────────────────────────────┐
│  Frontend              │      │  Optional: instance/ml_models/  │
│  base.html (JS)        │      │  (cached matrices / scalers)    │
│  index.html (panel)    │      └────────────────────────────────┘
└────────────────────────┘
```

### Integration with the existing Flask app

- **Instantiation:** Create a single recommender instance at app startup (module-level or Flask `before_first_request` / app factory pattern) so KNN indices are not rebuilt on every HTTP request.
- **Database access:** Pass the same `sqlite3.Connection` from `get_db()` (lines 36–41 in `app.py`) or a dedicated read-only connection path (`DB_PATH` at line 33).
- **Replacement point:** `get_recommendations()` (lines 895–964) should call the hybrid recommender instead of `generate_simple_recommendations()`.
- **Deprecation:** Keep `generate_simple_recommendations()` as a fallback only if the ML module fails or data is insufficient.

### Data flow: interaction → recommendation

1. User completes survey → `POST /api/user/survey` (lines 829–893) writes `user_surveys`.
2. User views product → **new step:** log `view` in `product_interactions` from `product_detail` route (currently only `recently_viewed` is updated ~lines 477–489).
3. User likes/adds to cart/purchases → log corresponding `action` in `product_interactions`.
4. User opens dashboard → `loadRecommendations()` in `templates/base.html` (lines 518–563) calls `GET /api/recommendations/<user_id>`.
5. API checks `recommendation_cache` for non-expired rows; if miss, hybrid KNN runs, writes cache with `algorithm` e.g. `knn_hybrid`, returns JSON.
6. Frontend renders match % and reason from response fields `score` and `reason`.

---

## 4. Implementation Steps

### Step 1: Create ML Module Structure

#### File layout

Create at project root:

| File | Responsibility |
|------|----------------|
| `ml_recommender.py` | Public API: `HybridRecommender` class used by Flask |
| `ml/data_loader.py` (optional subpackage) | SQLite queries → pandas DataFrames |
| `ml/feature_engineering.py` | Encoding, matrices, scaling |
| `ml/knn_models.py` | User-KNN, item-KNN, content-based logic |
| `ml/config.py` | Weights, k, action weights, cache TTL constants |

A single `ml_recommender.py` is acceptable for a school project; split modules when any file exceeds ~300 lines.

#### Classes and functions to define

**`ml/config.py` (or constants block)**

- `N_NEIGHBORS` (default 5–10; must be less than user count for user-KNN)
- `USER_CF_WEIGHT`, `ITEM_CF_WEIGHT`, `CONTENT_WEIGHT` (e.g. 0.4, 0.35, 0.25 — sum to 1.0)
- `ACTION_WEIGHTS` dict: `view`=1, `like`=3, `add_to_cart`=5, `purchase`=10, `compare`=2
- `CACHE_TTL_HOURS` = 24 (match current `get_recommendations` behavior)
- `MAX_RECOMMENDATIONS` = 10 API / 5–3 dashboard display

**`DataLoader` class**

- `__init__(self, db_connection)` — store connection with `row_factory` already set
- `load_users_with_surveys()` → DataFrame of users joined to `user_surveys`
- `load_products()` → DataFrame with parsed `genre_suitability` JSON
- `load_interactions()` → DataFrame of `product_interactions`
- `load_user_interaction_matrix()` → pivot: rows=users, columns=product_ids, values=weighted action scores
- `get_user_survey(user_id)` → dict or None
- `get_user_interacted_product_ids(user_id)` → set of product IDs to exclude from recommendations

**`FeatureEngineer` class**

- `encode_user_survey(survey_row)` → 1D numpy vector
- `encode_product(product_row)` → 1D numpy vector
- `build_user_feature_matrix(users_df)` → 2D array + user_id index mapping
- `build_product_feature_matrix(products_df)` → 2D array + product_id index mapping
- `build_interaction_matrix(interactions_df)` → sparse or dense user×product matrix

**`KNNUserRecommender` class**

- `fit(user_feature_matrix, interaction_matrix, user_ids)`
- `recommend(user_id, n, exclude_product_ids)` → list of `(product_id, score, reason_fragment)`

**`KNNItemRecommender` class**

- `fit(product_feature_matrix, interaction_matrix, product_ids)`
- `recommend(user_id, n, exclude_product_ids)` → list of `(product_id, score, reason_fragment)`

**`ContentBasedRecommender` class**

- `recommend(user_survey, products_df, n, exclude_product_ids)` → list of `(product_id, score, reason_fragment)`

**`HybridRecommender` class**

- `__init__(self, db_connection)` — wires subcomponents
- `refresh()` — reload data from DB and refit KNN models
- `get_recommendations(user_id, n=10)` → list of dicts matching API shape: `id`, `name`, `category`, `price`, `image_url`, `score`, `reason`

**`generate_recommendation_reason()` helper**

- Inputs: contributing signals (neighbor username patterns avoided for privacy; use “similar shoppers”, genre overlap, interaction type)
- Output: string ≤ 120 characters for UI tooltip

#### Separation of concerns

- Flask routes: HTTP, auth, cache read/write, JSON serialization only
- `ml_recommender.py`: all numeric/ML logic
- Migrations: schema and seed data only — no ML imports in migration scripts

---

### Step 2: Data Loading and Preprocessing

#### Connect to SQLite

- Reuse `DB_PATH` from `app.py` (line 33): `os.path.join(app.instance_path, 'cart.db')`.
- When loading outside Flask request context, use the same path pattern as `migrations/004_seed_ml_data.py` `get_db_path()`.

#### Required queries

1. **All surveys**

   ```sql
   SELECT u.id AS user_id, us.skill_level, us.instrument_type,
          us.preferred_genres, us.budget_range
   FROM users u
   INNER JOIN user_surveys us ON u.id = us.user_id
   ```

2. **All products with ML attributes**

   ```sql
   SELECT id, name, category, price, stock, description, image_url,
          skill_level, genre_suitability, instrument_type, price_range
   FROM products
   ```

3. **All interactions**

   ```sql
   SELECT user_id, product_id, action, timestamp, duration, frequency
   FROM product_interactions
   ORDER BY timestamp DESC
   ```

4. **Per-user interactions** (for item-CF seed and exclusion lists)

   ```sql
   SELECT product_id, action, MAX(timestamp) AS last_ts
   FROM product_interactions
   WHERE user_id = ?
   GROUP BY product_id, action
   ```

#### Missing data handling

| Scenario | Handling |
|----------|----------|
| User has survey but zero interactions | Use content-based + user-KNN on survey features only; cold-start path (Step 5) |
| User has interactions but no survey | Block recommendations at API level (existing behavior lines 906–910) — survey required |
| Product missing `genre_suitability` | Treat as empty list `[]` |
| Product missing `skill_level` / `instrument_type` | Use neutral encoding (midpoint) or exclude from content-CF |
| `preferred_genres` invalid JSON | Log error, skip user or fall back to empty genre list |
| Duplicate interaction rows | Aggregate: sum `frequency`, take max `duration`, use highest `ACTION_WEIGHTS` action per user-product pair |

#### Categorical encoding (overview)

- **skill_level:** Ordinal map `beginner`→0, `intermediate`→1, `advanced`→2, `professional`→3, then scale to [0,1]
- **instrument_type:** One-hot: `acoustic`, `electric`, `both` (3 columns)
- **preferred_genres:** One-hot over fixed list: `rock`, `blues`, `jazz`, `classical`, `metal`, `pop`, `country`, `folk`, `indie` (9 columns)
- **budget_range:** Ordinal map `under_500`→0 through `over_5000`→4, scale to [0,1]
- **category (products):** One-hot: `guitars`, `amplifiers`, `effects`, `accessories`

#### Interaction matrix construction

- Rows: `user_id` (only users appearing in `user_surveys` or all users with interactions — document choice; recommend all surveyed users)
- Columns: `product_id`
- Cell value: sum over interactions of `ACTION_WEIGHTS[action] * frequency` (optionally decay older `timestamp` with exponential decay)
- Fill missing cells with 0

#### Scaling and normalization

- Apply `StandardScaler` (fit on training matrix, transform at query time) to user and product feature matrices before KNN **when mixing features of different scales** (genres 0/1 vs ordinal skill).
- For cosine similarity on interaction vectors, L2-normalize each user row optionally.
- Store fitted scaler objects in `instance/ml_models/` if using persistence.

---

### Step 3: Feature Engineering

#### User survey vector (content + user-KNN features)

Build a fixed-length vector per user (~15–20 dimensions):

1. Scaled skill level (1 dim)
2. Instrument type one-hot (3 dim)
3. Genre one-hot (9 dim)
4. Scaled budget (1 dim)

**Rationale:** Fixed dimensionality ensures `NearestNeighbors` works; one-hot genres preserve “plays rock and metal” without false ordinality.

#### Product attribute vector

Per product:

1. Scaled product `skill_level` (1 dim)
2. Product `instrument_type` one-hot (3 dim)
3. `genre_suitability` one-hot (9 dim) — parse JSON from `genre_suitability` column
4. Scaled `price_range` or normalized `price` (1 dim)
5. Optional: `category` one-hot (4 dim)

#### Genre overlap score (for content-based and explanations)

For user \(u\) and product \(p\):

- `overlap = |user_genres ∩ product_genres| / max(|user_genres|, 1)`
- Use as multiplier or additional feature in content-based scoring

#### Instrument and skill compatibility

- **Instrument:** Full match = 1.0; user `both` matches any product type; product `both` matches any user type; else 0.5 or 0 for mismatch
- **Skill:** Exact match = 1.0; product `beginner` can match lower user tiers with 0.7; user skill more than one level above product = 0.3 penalty

#### Budget compatibility

Map `budget_range` to min/max price bounds (mirror logic in `generate_simple_recommendations` lines 979–989). Score 1.0 inside range, decay outside (e.g. 0.5 if one band away).

#### Popularity signal (optional)

- Per product: count of interactions or purchases across all users
- Add small boost (e.g. +0.05 max) to break ties — avoids recommending obscure items with no support

---

### Step 4: KNN Model Implementation

#### User–user collaborative filtering

1. Build user feature matrix: concatenate **survey vector** and **flattened normalized interaction row** (or use interaction-only matrix for pure CF).
2. Fit `NearestNeighbors` with `metric='cosine'` (preferred for sparse preference data) or `metric='minkowski', p=2` (Euclidean).
3. For target `user_id`, find k neighbors (exclude self).
4. Collect products that neighbors interacted with (weight by neighbor distance inverse and interaction strength).
5. Aggregate scores per `product_id`.

**Choosing k:** Start with `k=5`. Rule: k should be odd for tie-breaking; k < number of users with similar survey cluster. With ~100 seeded users, test k ∈ {3, 5, 7, 10}.

**Distance metric rationale:** Cosine emphasizes pattern similarity (genre + behavior shape) rather than absolute scale.

#### Item–item collaborative filtering

1. Build product feature matrix from product attributes **or** use product columns from user×product interaction matrix (item vectors).
2. Fit `NearestNeighbors` on product vectors.
3. For target user, take their top-N interacted products (by weight).
4. For each seed product, find k similar items; score by similarity × user’s engagement with seed.
5. Sum scores across seeds.

**Use when:** User has at least 1–2 meaningful interactions (`like`, `add_to_cart`, or `purchase`).

#### Content-based filtering

1. Compare user survey vector to each product vector (cosine similarity or weighted dot product with instrument/skill/budget gates).
2. Hard-filter: exclude products outside budget band unless fewer than 5 candidates remain.
3. Soft-boost: genre overlap, skill match.

**Use when:** Cold start or sparse interaction history.

#### Combining three sources

For each candidate `product_id`:

```
final_score = (w_user * user_cf_score) + (w_item * item_cf_score) + (w_content * content_score)
```

- Normalize each component to [0, 1] before weighting (min-max or divide by max observed).
- If a component returns no candidates, redistribute its weight to the others proportionally.
- Exclude products in `get_user_interacted_product_ids()` except optionally `view` if you want re-surfacing — recommend excluding all previously purchased items always.

#### Explainability

Build `reason` from dominant component:

| Dominant signal | Example reason template |
|-----------------|-------------------------|
| Content | "Matches your electric preference and rock, blues genres" |
| User-CF | "Popular with shoppers who have similar skill and genre tastes" |
| Item-CF | "Similar to items you recently liked" |
| Mixed | "Strong match for your budget and similar to your browsing history" |

Store component breakdown internally (optional JSON in `recommendation_cache.reason` prefixed with metadata) for debugging — do not expose raw neighbor user IDs (privacy).

---

### Step 5: Training the Model

#### When to train / refresh

| Strategy | When to use |
|----------|-------------|
| **On app startup** | Load matrices and fit KNN once; acceptable for current dataset size |
| **On demand** | Expose `recommender.refresh()` after survey submit or significant interaction |
| **Scheduled** | Optional cron/background thread every N hours for production |

**Recommendation for this project:** Refresh on startup + call `refresh()` after `POST /api/user/survey` success and after logging `purchase` or `add_to_cart`.

#### Model persistence

- Save with `joblib`: `StandardScaler`, user/product id index maps, and optionally precomputed distance structures if you switch to custom caching.
- File naming: `instance/ml_models/knn_state_{timestamp}.joblib` or single `knn_state_latest.joblib`.
- On startup: if file exists and DB modification time is older than model time, load; else rebuild.

#### Incremental updates

Full refresh is simplest at this scale. For incremental:

- Append new interaction to matrix row/column and **refit** neighbors (sklearn refit is fast at N<1000).
- Do not partially update cosine indices without validation tests.

#### Cold-start handling

| User state | Strategy |
|------------|----------|
| New user, survey only | 100% content-based; optional: recommend globally popular items in same `instrument_type` |
| Survey + few views | Content 60%, user-CF 40% (adjust weights dynamically) |
| Survey + rich history | Full hybrid |
| No similar neighbors found | Fall back to content-based; if still empty, relax budget filter one band |
| Global new product | Rely on content vector until interactions accrue |

---

### Step 6: Generating Recommendations

#### End-to-end process

1. Validate `user_id` has row in `user_surveys`.
2. Load or refresh recommender state if stale.
3. Compute three score lists (user-CF, item-CF, content).
4. Merge to unified candidate set (union of product IDs).
5. Apply exclusion list (already purchased, optionally cart items).
6. Compute weighted `final_score` per candidate.
7. Join product metadata (`name`, `category`, `price`, `image_url`) from `products`.
8. Sort descending by `final_score`; take top `MAX_RECOMMENDATIONS`.
9. Clamp `score` to [0, 1] for frontend `% Match` display (line 591 in `base.html`).
10. Attach `reason` string per item.

#### Filtering rules

- Never recommend `stock = 0` unless business rules allow backorder display.
- Prefer `instrument_type` match or `both` (same rule as current SQL lines 972–974).
- Deduplicate by `product_id`.

#### Ranking ties

- Secondary sort: genre overlap count
- Tertiary: lower price variance within budget band (optional variety)

---

### Step 7: Integration with Flask App

#### Modify `get_recommendations()` (`app.py` lines 895–964)

1. Import `HybridRecommender` from `ml_recommender`.
2. Create module-level `recommender = HybridRecommender(get_db())` **or** lazy singleton initialized on first request.
3. Replace line 946 call:
   - **From:** `recommendations = generate_simple_recommendations(db, survey_data)`
   - **To:** `recommendations = recommender.get_recommendations(user_id, n=10)`
4. Update cache insert (lines 951–956):
   - Set `algorithm` to `'knn_hybrid'` instead of `'simple_survey_based'`.
   - Store enriched `reason` from ML output.
5. On ML exception: log traceback, fall back to `generate_simple_recommendations()` once, set `algorithm` to `'simple_fallback'`.

#### Cache invalidation

Invalidate `recommendation_cache` for `user_id` when:

- Survey updated (`POST /api/user/survey` after successful commit, lines 887–887)
- New `purchase` or `add_to_cart` logged
- User clicks refresh (new query param or DELETE cache endpoint)

Implementation: `DELETE FROM recommendation_cache WHERE user_id = ?` before regenerating.

#### Add interaction logging (prerequisite — not yet in `app.py`)

The seeded `product_interactions` data exists, but live routes must write interactions:

| Route / event | `action` value |
|---------------|----------------|
| `product_detail` view | `view` |
| Wishlist/favorite (if added) | `like` |
| Add to cart | `add_to_cart` |
| Checkout complete | `purchase` |
| Compare feature (if exists) | `compare` |

Create helper `log_product_interaction(user_id, product_id, action, duration=0)` using parameterized SQL `INSERT INTO product_interactions (...) VALUES (?, ?, ?, ...)`.

Reference `product_detail` route where `recently_viewed` is updated (~lines 477–489) — add `log_product_interaction` call in the same block.

#### Survey submission hook

After `db.commit()` in `submit_survey()` (line 887), call cache invalidation and optionally `recommender.refresh()` if matrices are global.

#### Error handling

- Return `500` with `{'error': 'Failed to load recommendations'}` only on unrecoverable errors (match line 964).
- Return `200` with empty list + message if survey incomplete (keep lines 909–910).
- Time out ML work: if generation exceeds 2s, return cached stale results or fallback simple recommender.

#### App entry point

- Note: `app.py` line 1023 runs on port `5001`; project notes mention port `5006` — align port in README and run command when testing.

---

### Step 8: Frontend Integration

#### Files

- `templates/index.html` — recommendations panel markup (lines 60–81)
- `templates/base.html` — JavaScript loader and card renderer (lines 517–644)
- `static/style.css` — `.recommendations-card`, `.match-score`, `.recommendation-reason` (from line 12 onward)

#### Display match scores

Already implemented: `Math.round(product.score * 100)}% Match` in `createRecommendationCard()` (`base.html` line 591). Ensure ML returns `score` as float 0–1.

#### Display recommendation reasons

Current UI shows "Why recommended?" as static text (line 597–598). Update to:

- Show `product.reason` in the tooltip (`title` attribute) — already partially wired.
- Optionally show truncated reason text (first 50 chars) visible under product name.
- Add `algorithm` badge in dev mode only (e.g. "Hybrid ML") — hide in production UI.

#### Loading states

- Keep `#recommendationsLoading` visible until fetch completes (lines 524–526, 559–561).
- On refresh, show spinner again before fetch.

#### Refresh recommendations

`refreshRecommendations()` (line 641) calls `loadRecommendations()` only — cache may still serve stale data for 24h.

**Required backend change:** Support cache bust:

- Option A: `GET /api/recommendations/<user_id>?refresh=true` deletes cache then regenerates.
- Option B: `POST /api/recommendations/<user_id>/refresh` with CSRF/session auth.

Update `refreshRecommendations()` to call API with refresh flag.

#### Survey update flow

`updateSurvey()` navigates to `/survey` (line 653). After survey save from `register.html` / `survey.html`, ensure redirect triggers `loadRecommendations()` on dashboard (check script ~line 808 in `base.html`).

#### `viewAllRecommendations()`

Currently navigates to `/recommendations` (line 648) — **route does not exist**. Either implement a full recommendations page template or change to expand grid to show all 10 items on dashboard.

---

### Step 9: Testing and Validation

#### Unit tests (create `tests/test_ml_recommender.py`)

| Test case | Assertion |
|-----------|-----------|
| `encode_user_survey` known input | Fixed vector length and known values for `beginner` + `rock` |
| Empty interactions user | Returns content-only recommendations, length > 0 |
| User with purchases | Item-CF contributes; purchased IDs not in results |
| Invalid `user_id` | Raises or returns empty with clear handling |
| Genre JSON malformed | Graceful degradation |

Use seeded DB copy in `tests/fixtures/cart_test.db` — copy `instance/cart.db` after migrations.

#### Integration tests

- Flask test client: `GET /api/recommendations/<id>` with logged-in user session
- Verify response JSON schema: `recommendations` array with keys `id`, `name`, `score`, `reason`
- Verify `403` when requesting another user's ID (line 901–902)
- Survey incomplete → empty list + message

#### Recommendation quality checks (manual)

With seeded data:

1. Pick user `rock_mike` from migration `004_seed_ml_data.py` — expect electric/rock-oriented products ranked high.
2. Pick `acoustic_sarah` — expect acoustic/folk/indie alignment.
3. Compare top-5 before/after ML vs `generate_simple_recommendations` — document differences in a short test log for your major work report.

#### Performance metrics

| Metric | Target |
|--------|--------|
| API latency (cached) | < 100 ms |
| API latency (cold ML) | < 500 ms at current data size |
| Matrix build time | < 2 s on startup |

Measure with `time.perf_counter()` in Flask before/after `get_recommendations`.

#### Edge cases checklist

- [ ] New registered user with survey, no interactions
- [ ] User with interactions but outdated survey (after update, cache clears)
- [ ] All recommended products out of stock
- [ ] Single user in database (KNN k must reduce to 1)
- [ ] User with only `view` interactions (weak signals)

---

### Step 10: Performance Optimization

#### Caching strategy

1. **Database cache** — existing `recommendation_cache` with `expires_at` (24h) — keep.
2. **In-memory cache** — dict `user_id → (recommendations, expiry)` inside `HybridRecommender` for repeat requests within same process.
3. **Do not** add Redis unless scaling beyond SQLite single-host — out of scope unless already deployed.

#### Query optimization

- Bulk-load tables once per `refresh()`; avoid per-product queries in loops.
- Use pandas merge for metadata join instead of N+1 SQL.
- Index suggestion (optional migration): `CREATE INDEX idx_pi_user ON product_interactions(user_id);` and `idx_pi_product ON product_interactions(product_id);`

#### Large dataset path

When users > 1000 or products > 500:

- Switch to sparse matrices (`scipy.sparse`)
- Reduce `n_neighbors` dynamically
- Batch precompute recommendations nightly; API serves cache only

#### Batch processing

- Admin script `scripts/refresh_all_recommendations.py`: loop all `user_id` from `user_surveys`, write `recommendation_cache` — run after bulk seed import.

#### Monitoring

- Log ML generation duration and fallback events to stdout or file `instance/ml.log`
- Count cache hit vs miss in `get_recommendations`

---

## 5. Configuration and Tuning

### KNN parameters

| Parameter | Starting value | Tuning direction |
|-----------|----------------|------------------|
| `n_neighbors` | 5 | Increase if recommendations too narrow; decrease if noisy |
| `metric` | `cosine` | Try Euclidean if features all same scale |
| `weights` (sklearn) | `distance` | Closer neighbors influence more — good for CF |
| Hybrid weights | 0.4 / 0.35 / 0.25 | Shift toward content if CF too sparse |

### Hyperparameter tuning process

1. Hold out 10% of interactions (mask as test set).
2. For each masked `(user, product)` pair, generate top-10 recommendations.
3. Compute hit rate@10 and MRR (mean reciprocal rank).
4. Grid search k and hybrid weights; record best on spreadsheet for major work evidence.

### A/B testing (optional)

- Serve `algorithm='knn_hybrid'` vs `'simple_survey_based'` by `user_id % 2` for two weeks.
- Compare click-through from recommendation cards (`viewProduct` clicks) and add-to-cart rate.

### Monitoring accuracy over time

- Weekly script: average hit rate on newly logged purchases.
- Dashboard metric in admin (future): % recommendations clicked.

---

## 6. Security Considerations

### Input validation

- Reuse survey validation in `submit_survey()` (lines 840–863): whitelist `skill_level`, `instrument_type`, `budget_range`, `preferred_genres`.
- Never pass raw client strings into dynamic SQL in ML loader — always parameterized queries.

### SQL injection

- `DataLoader` must only use `?` placeholders and tuple parameters, same as `get_db()` patterns throughout `app.py`.

### Privacy

- Do not return other users' usernames or emails in API responses or `reason` text.
- `product_interactions` contains behavioral data — restrict API access to own `user_id` (already enforced line 901–902).
- Add `instance/ml_models/` to `.gitignore` if persisted models embed interaction data.

### Model data security

- File permissions on `instance/` — not world-readable on shared servers.
- No export of full interaction matrix to client-side JavaScript.

---

## 7. Deployment Considerations

### Deploying the ML system

1. Install updated `requirements.txt` on target host.
2. Run migrations if DB is fresh.
3. Pre-warm: start Flask, trigger one `refresh()` on startup.
4. Verify `/api/recommendations/<test_user_id>` returns non-empty for seeded user id=1 or first survey user.

### Model versioning

- Tag saved model files with date: `knn_state_20260520.joblib`.
- Keep previous version until new one validated.

### Rollback

1. Revert `app.py` to call `generate_simple_recommendations()`.
2. `DELETE FROM recommendation_cache WHERE algorithm = 'knn_hybrid';`
3. Remove scikit-learn from requirements if desired.

### Production health

- Health check endpoint (optional): `GET /api/ml/health` returns `{ "status": "ok", "users_loaded": N, "last_refresh": ISO8601 }`.
- Alert if fallback rate > 10% of requests.

---

## 8. Troubleshooting Guide

| Issue | Likely cause | Resolution |
|-------|--------------|------------|
| Empty recommendations for valid user | No products pass budget filter | Relax budget one band in content module |
| All scores identical | Normalization skipped | Min-max normalize each component before weighting |
| `403 Unauthorized` | Wrong `user_id` in fetch URL | Ensure `getCurrentUserId()` matches session user |
| Recommendations never change | 24h cache | Implement `?refresh=true` or invalidate on interaction |
| `ModuleNotFoundError: sklearn` | Dependencies not installed | `pip install -r requirements.txt` |
| KNN fails with few users | k too large | Set `n_neighbors = min(k, n_users - 1)` |
| JSON parse error on genres | Invalid `preferred_genres` in DB | Fix row or default to `[]` |
| Slow API | Full refresh per request | Move refresh to startup / background only |
| Memory growth | Repeated refit without releasing | Single recommender singleton; del old matrices on refresh |
| SQLite locked | Concurrent writes | Use one connection per request via `g`; batch writes |

### Debugging recommendation quality

1. Log top 3 neighbors' distances for a test user (server log only).
2. Print decomposed scores (user_cf, item_cf, content) for top 5 products.
3. Compare against products manually expected for that user's survey row in `user_surveys`.

### Database connection errors

- Confirm `instance/cart.db` exists and path printed at startup (line 34).
- Run `PRAGMA foreign_keys = ON` (line 74) on each connection.

---

## 9. Success Metrics

| Metric | How to measure | Target (indicative) |
|--------|----------------|---------------------|
| Recommendation accuracy (offline) | Hit rate@10 on held-out interactions | > 0.15 with seeded data |
| User engagement | Click-through on recommendation cards / impressions | > 10% of dashboard loads |
| Click-through rate (CTR) | `view` interactions on recommended products / API loads | Improve 20% vs simple baseline |
| Conversion rate | `purchase` or `add_to_cart` within 7 days of recommendation display | > 5% of clicked items |
| API performance | p95 latency | < 500 ms |
| Fallback rate | % requests using `simple_fallback` | < 5% |

Document baseline metrics with the simple algorithm before switching, then re-measure after KNN deployment for your Software Major Work evidence.

---

## 10. Implementation Checklist (Ordered)

Use this as a sprint-ordered task list:

- [ ] Add ML dependencies to `requirements.txt` and install
- [ ] Create `ml_recommender.py` (and optional `ml/` submodules) with classes described in Step 1
- [ ] Implement `DataLoader` queries against `user_surveys`, `products`, `product_interactions`
- [ ] Implement `FeatureEngineer` encodings (Step 3)
- [ ] Implement user-KNN, item-KNN, and content-based recommenders (Step 4)
- [ ] Implement `HybridRecommender.get_recommendations(user_id, n)`
- [ ] Add `log_product_interaction()` to `app.py` and call from product/cart routes
- [ ] Wire `get_recommendations()` to hybrid recommender; keep simple fallback
- [ ] Invalidate cache on survey submit and refresh API param
- [ ] Update `refreshRecommendations()` to bust cache
- [ ] Fix or implement `/recommendations` page for "View All"
- [ ] Display `product.reason` visibly in recommendation cards
- [ ] Write unit and integration tests (Step 9)
- [ ] Run offline evaluation and record metrics for major work report
- [ ] Optional: persistence in `instance/ml_models/`
- [ ] Update README with ML setup and port note

---

## 11. Key File Reference Summary

| Location | Purpose |
|----------|---------|
| `app.py` 895–964 | `get_recommendations()` — primary integration point |
| `app.py` 966–1020 | `generate_simple_recommendations()` — fallback to deprecate |
| `app.py` 829–893 | `submit_survey()` — cache invalidation hook |
| `app.py` 33–41 | `DB_PATH`, `get_db()` |
| `templates/index.html` 60–81 | Recommendations panel HTML |
| `templates/base.html` 517–644 | Load/render/refresh JavaScript |
| `migrations/003_create_survey_tables_fixed.py` | Schema for ML tables |
| `migrations/004_seed_ml_data.py` | Initial ML seed data |
| `migrations/005_expand_ml_data.py` | Expansion to ~100 users, ~50 products |
| `migrations/006_seed_more_surveys.py` | Additional survey diversity |
| `YEAR 12 MAJOR WORK planning files/machine-learning-implementation.md` | Reference code (do not copy blindly — align with this guide) |

---

## 12. Valid Domain Values (Quick Reference)

Copy validation whitelists from `submit_survey()` in `app.py` (~lines 840–863):

- **skill_level:** `beginner`, `intermediate`, `advanced`, `professional`
- **instrument_type:** `acoustic`, `electric`, `both`
- **preferred_genres:** `rock`, `blues`, `jazz`, `classical`, `metal`, `pop`, `country`, `folk`, `indie`
- **budget_range:** `under_500`, `500_1000`, `1000_2000`, `2000_5000`, `over_5000`
- **category:** `guitars`, `amplifiers`, `effects`, `accessories`
- **action:** `view`, `like`, `add_to_cart`, `purchase`, `compare`

---

*This guide is the instruction-only companion to `ML_IMPLEMENTATION_PROMPT.md`. Implement in order, validate against seeded data in `instance/cart.db`, and retain the simple recommender as fallback until offline metrics and integration tests pass.*
