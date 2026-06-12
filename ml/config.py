# ML Configuration Parameters

# KNN Parameters
N_NEIGHBORS = 15  # Number of similar users for user-based CF
ITEM_N_NEIGHBORS = 12  # Number of similar items for item-based CF (recently viewed items)
ITEM_SEED_TOP = 5  # Number of top user interactions to use as seeds for item recommendation
ITEM_CF_MIN_USER_WEIGHT = 1.0

# Hybrid Weights
# USER_CF_WEIGHT: User-based collaborative filtering (finds similar users)
# ITEM_CF_WEIGHT: Item-based collaborative filtering (recommends products similar to recently viewed items) - INCREASED for better personalization
# CONTENT_WEIGHT: Content-based filtering (matches user survey preferences with product attributes)
USER_CF_WEIGHT = 0.3
ITEM_CF_WEIGHT = 0.5
CONTENT_WEIGHT = 0.2

# Action Weights for Interaction Matrix
ACTION_WEIGHTS = {
    'view': 1.0,
    'like': 2.0,
    'add_to_cart': 3.0,
    'purchase': 5.0,
    'compare': 1.5,
}

# Other Parameters
MAX_RECOMMENDATIONS = 10
