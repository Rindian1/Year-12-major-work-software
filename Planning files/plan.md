# Product Detail View Plan

## Goal
When a user clicks a product in `templates/search.html`, navigate to an in-depth product page that shows a larger image, name, category, price, short and detailed descriptions, an Add to cart button, and a grid of placeholder sound test links (YouTube).

## Steps Implemented
- **Add route**: Created `product_detail()` in `app.py` at `/product/<int:product_id>`.
- **Data retrieval**: Fetch product by `id` from `products` table. 404 if not found.
- **Placeholders**:
  - Detailed description constructed from `product['description']` plus extra copy.
  - `sound_tests`: six items with `title` and `url` set to `https://youtube.com`.
- **Template**: Added `templates/product_detail.html` rendering:
  - Large product image with fallback `static/images/placeholder.jpg`.
  - Name, category, price, short description.
  - Add to cart form posting to `/add-to-cart` with hidden `product_id`.
  - Detailed description block.
  - "Sound tests of product" section with 3-column grid of links (all placeholder to YouTube).
- **Search linking**: Updated `templates/search.html` product cards to link to the internal detail page using `url_for('product_detail', product_id=product['id'])`.

## How To Extend Later
- **Real long descriptions**: Add `long_description` column to `products` and populate; render it instead of the placeholder.
- **Real sound tests**: Create a `product_sound_tests` table: `(id, product_id, title, url, sort_order)`. Query and pass to the template; fall back to placeholders if none.
- **Images**: Add multiple images/gallery and thumbnails.
- **SEO-friendly URLs**: Add a slug column and route `/product/<int:product_id>-<slug>`.
- **Breadcrumbs and category links**: Link category to `search?category=<category>` from the detail page.
- **Add to cart UX**: Convert add-to-cart on detail page to AJAX for instant feedback like in search results.

## Files Touched
- `app.py`: new route `product_detail()` and `abort` import.
- `templates/search.html`: product card link updated to use internal detail URL.
- `templates/product_detail.html`: new template for the detail view.

## Testing Checklist
- **Search page**: Click a product → navigates to `/product/<id>`.
- **Detail page**: Displays image, name, category, price, short description, detailed description, and Add to cart button reflecting stock.
- **Sound test links**: All six tiles open `https://youtube.com` in a new tab.
- **Add to cart**: Submitting the form adds the product to cart and responds successfully.
