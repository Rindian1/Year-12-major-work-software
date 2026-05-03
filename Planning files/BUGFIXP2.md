# Bug Fixes & Improvements - Part 2

## 1) Registration Process Error Handling

### Current Issues:
- Registration crashes when `Flask()` class constructor is called instead of `flash()` function
- Line 701 in `app.py` uses incorrect function: `Flask('Registration successful! Please log in.')`
- No proper error handling for database operations during registration
- Missing import for `flash` function from Flask
- Email validation lacks proper exception handling for `EmailNotValidError`
- Duplicate email checking occurs after validation but without transaction safety

### Technical Details:
- **Error Location**: `app.py` line 701 in registration route
- **Root Cause**: Calling `Flask()` constructor instead of `flash()` function
- **Current Error**: `Flask('Registration successful! Please log in.')` attempts to instantiate Flask class
- **Expected Error**: `TypeError: Flask.__init__() missing 1 required positional argument: 'import_name'`
- **Missing Import**: `flash` function not imported from Flask
- **Email Validation Issues**:
  - Line 662: `validate_email(email)` called without try-catch for `EmailNotValidError`
  - Line 683: `validate_email(email)` called again without exception handling
  - Import exists: `from email_validator import validate_email, EmailNotValidError` (line 12)
  - Missing: No handling of `EmailNotValidError` exceptions
- **Database Race Condition**: Email uniqueness check (lines 683-687) not wrapped in transaction
- **Impact**: Registration process crashes with TypeError, email validation may crash with unhandled exceptions

### Implementation Methods:
1. **Fix typo and add import**: Simple, direct fix for Flask/flash issue
2. **Fix email validation exception handling**: Add try-catch for EmailNotValidError
3. **Add comprehensive error handling**: Wrap database operations in try-catch
4. **Add transaction safety**: Prevent race conditions in email uniqueness checks

### SIMPLEST SOLUTION:
Fix the typo and add missing import:

```python
# Add to imports at top of app.py (line 1-8)
from flask import flash

# Fix line 701 in registration route
flash('Registration successful! Please log in.')
```

**Enhanced Solution with Email Error Handling:**
```python
# Fix email validation with proper exception handling
try:
    # Validate email with exception handling
    if not email:
        errors.append('Email is required')
    else:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            errors.append(f'Invalid email address: {str(e)}')
except Exception as e:
    errors.append('Email validation failed')

# Enhanced database operations with transaction safety
try:
    db = get_db()
    password_hash = generate_password_hash(password)
    
    # Start transaction for atomic operations
    db.execute('BEGIN TRANSACTION')
    
    # Check username and email uniqueness in same transaction
    existing_user = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing_user:
        errors.append('Username already exists')
    
    existing_email = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if existing_email:
        errors.append('Email already registered')
    
    if errors:
        db.rollback()
        return render_template('register.html', errors=errors, username=username, email=email)
    
    # Insert user if no errors
    db.execute(
        'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
        (username, email, password_hash)
    )
    db.commit()
    flash('Registration successful! Please log in.')
    return redirect(url_for('login'))
    
except sqlite3.IntegrityError as e:
    db.rollback()
    if 'UNIQUE constraint failed: users.username' in str(e):
        errors.append('Username already exists')
    elif 'UNIQUE constraint failed: users.email' in str(e):
        errors.append('Email already registered')
    else:
        errors.append('Registration failed. Please try again.')
    return render_template('register.html', errors=errors, username=username, email=email)
except Exception as e:
    db.rollback()
    flash('Registration failed. Please try again.')
    return render_template('register.html', errors=['An unexpected error occurred'], username=username, email=email)
```

**Email Validation Fix Only:**
```python
# Fix email validation in registration route (lines 660-663)
if not email:
    errors.append('Email is required')
else:
    try:
        validate_email(email)
    except EmailNotValidError as e:
        errors.append('Please enter a valid email address')

# Fix duplicate email check (lines 682-687)
if email and not any('Email' in error for error in errors):  # Only check if email is valid
    try:
        db = get_db()
        existing_email = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing_email:
            errors.append('Email already registered')
    except Exception as e:
        errors.append('Unable to verify email availability')
```

**Current State Analysis:**
The issue has evolved from a simple typo to a more serious problem:
- **Original**: `flask()` → `NameError: name 'flask' is not defined`
- **Current**: `Flask()` → `TypeError: Flask.__init__() missing 1 required positional argument: 'import_name'`
- **Correct**: `flash()` → Properly displays success message to user

**Implementation Steps:**
1. Add `flash` to Flask imports in `app.py` (line 1-8 area)
2. Fix line 701: `Flask()` → `flash()`
3. Fix email validation exception handling (lines 662 and 683)
4. Optional: Add comprehensive error handling around database operations
5. Optional: Add transaction safety for email uniqueness checks
6. Test registration flow with valid and invalid emails
7. Verify success message appears after successful registration
8. Test edge cases: malformed emails, duplicate emails, database errors

---

## 2) Search Authentication Requirement

### Current Issues:
- Search functionality is accessible to non-authenticated users
- No `@login_required` decorator on search route
- Search bar visible in header for all users
- Security concern: exposing product data to unauthenticated users

### Technical Details:
- **Affected Route**: `/search` in `app.py` line 412
- **Current Implementation**: No authentication check
- **Template Impact**: Search form in `base.html` needs conditional display
- **User Experience**: Non-authenticated users can't add items to cart anyway

### Implementation Methods:
1. **Add @login_required decorator**: Simple authentication requirement
2. **Conditional search display**: Hide search for non-authenticated users
3. **Redirect with message**: Inform users they need to login

### SIMPLEST SOLUTION:
Add authentication requirement and conditional display:

```python
# In app.py, add decorator to search route
@app.route('/search')
@login_required  # Add this decorator
def search():
    # ... existing search code remains unchanged
```

```html
<!-- In base.html, make search form conditional -->
<div class="search-container">
    {% if current_user.is_authenticated %}
        {% block search_form %}
        <form method="get" action="{{ url_for('search') }}" class="search-form">
            <!-- existing search form content -->
        </form>
        {% endblock %}
    {% else %}
        <div class="search-prompt">
            <a href="{{ url_for('login') }}" class="search-login-prompt">Login to search</a>
        </div>
    {% endif %}
</div>
```

**Enhanced Solution with User Guidance:**
```python
# Modified search route with redirect message
@app.route('/search')
@login_required
def search():
    query = (request.args.get('q') or '').strip()
    category = (request.args.get('category') or '').strip().lower()
    # ... rest of existing search code
```

**CSS for Search Prompt:**
```css
.search-prompt {
    padding: 10px 15px;
    text-align: center;
}

.search-login-prompt {
    color: white;
    text-decoration: none;
    background: rgba(255, 255, 255, 0.2);
    padding: 8px 16px;
    border-radius: 20px;
    transition: all 0.3s ease;
}

.search-login-prompt:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-1px);
}
```

**Implementation Steps:**
1. Add `@login_required` decorator to search route in `app.py`
2. Wrap search form in authentication check in `base.html`
3. Add CSS styling for login prompt
4. Test search functionality with authenticated and non-authenticated users

---

## 3) Stock Management with Cart Items

### Current Issues:
- Product stock doesn't update when items are added to cart
- No stock validation during cart operations
- Cart can exceed available product stock
- No real-time stock tracking

### Technical Details:
- **Missing Feature**: Stock decrement in `add_to_cart` route
- **Database Schema**: Products table has `stock` column but not utilized
- **Cart Logic**: Current implementation ignores stock availability
- **Impact**: Overselling products, inventory management issues

### Implementation Methods:
1. **Stock decrement on add**: Reduce stock when items added to cart
2. **Stock restoration on remove**: Return stock when items removed
3. **Real-time validation**: Check stock before allowing cart operations

### SIMPLEST SOLUTION:
Update stock when adding/removing cart items:

```python
# Modified add_to_cart route with stock management
@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', 1)
    try:
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    if not product_id:
        return jsonify({'success': False, 'error': 'Product ID is required'}), 400

    db = get_db()
    try:
        # Start transaction
        db.execute('BEGIN TRANSACTION')
        
        # Fetch the product details with stock lock
        product = db.execute('SELECT name, price, stock FROM products WHERE id = ? FOR UPDATE', (product_id,)).fetchone()
        if not product:
            db.rollback()
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Check if item already exists in cart
        existing_item = db.execute('SELECT id, quantity FROM cart_items WHERE product_id = ? AND user_id = ?', 
                                  (product_id, current_user.id)).fetchone()
        
        if existing_item:
            # Update quantity of existing item
            new_quantity = existing_item['quantity'] + quantity
            if product['stock'] > 0 and new_quantity <= product['stock']:
                # Update cart item quantity
                db.execute('UPDATE cart_items SET quantity = ? WHERE id = ?', (new_quantity, existing_item['id']))
                # Decrement stock
                db.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (quantity, product_id))
                db.commit()
                return jsonify({'success': True, 'message': 'Quantity updated in cart', 'quantity': new_quantity})
            else:
                db.rollback()
                return jsonify({'success': False, 'error': 'Insufficient stock available'}), 400
        else:
            # Add new item to cart
            if product['stock'] > 0 and quantity <= product['stock']:
                # Add to cart
                db.execute('INSERT INTO cart_items (name, price, user_id, product_id, quantity) VALUES (?, ?, ?, ?, ?)', 
                          (product['name'], product['price'], current_user.id, product_id, quantity))
                # Decrement stock
                db.execute('UPDATE products SET stock = stock - ? WHERE id = ?', (quantity, product_id))
                db.commit()
                return jsonify({'success': True, 'message': 'Added to cart', 'quantity': quantity})
            else:
                db.rollback()
                return jsonify({'success': False, 'error': 'Insufficient stock available'}), 400
                
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Modified remove_item route with stock restoration
@app.route('/remove-item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id: int):
    db = get_db()
    try:
        # Get cart item details before deletion
        item = db.execute('SELECT product_id, quantity FROM cart_items WHERE id = ? AND user_id = ?', 
                         (item_id, current_user.id)).fetchone()
        
        if not item:
            return redirect(url_for('home'))
        
        # Remove from cart
        db.execute('DELETE FROM cart_items WHERE id = ? AND user_id = ?', (item_id, current_user.id))
        
        # Restore stock if product_id exists
        if item['product_id']:
            db.execute('UPDATE products SET stock = stock + ? WHERE id = ?', (item['quantity'], item['product_id']))
        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error removing item: {e}")
    
    return redirect(url_for('home'))
```

**Enhanced Stock Display:**
```python
# Modified product_detail route to show stock
@app.route('/product/<int:product_id>')
def product_detail(product_id: int):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        abort(404)

    # Calculate available stock (current stock + items in user's cart)
    available_stock = product['stock']
    if current_user.is_authenticated:
        cart_quantity = db.execute('SELECT SUM(quantity) as total FROM cart_items WHERE product_id = ? AND user_id = ?', 
                                  (product_id, current_user.id)).fetchone()['total'] or 0
        available_stock += cart_quantity

    # ... rest of existing code
    
    return render_template(
        'product_detail.html',
        product=product,
        detailed_description=detailed_description,
        youtube_links=youtube_links,
        in_cart=in_cart,
        cart_items=cart_items,
        available_stock=available_stock  # Add to template context
    )
```

**Template Updates:**
```html
<!-- In product_detail.html, add stock display -->
<div class="stock-info">
    {% if available_stock > 0 %}
        <span class="stock-available">{{ available_stock }} in stock</span>
    {% else %}
        <span class="stock-out">Out of stock</span>
    {% endif %}
</div>

<!-- Disable add to cart if out of stock -->
{% if available_stock > 0 %}
    <button type="submit" class="add-to-cart-btn" {% if in_cart %}disabled{% endif %}>
        {% if in_cart %}In Cart{% else %}Add to Cart{% endif %}
    </button>
{% else %}
    <button type="submit" class="add-to-cart-btn" disabled>Out of Stock</button>
{% endif %}
```

**Implementation Steps:**
1. Update `add_to_cart` route to decrement stock with transaction handling
2. Update `remove_item` route to restore stock
3. Modify `product_detail` to calculate and display available stock
4. Update templates to show stock information and disable out-of-stock items
5. Test stock management with various cart operations

---

## 4) Category Change Auto-Search

### Current Issues:
- Changing category dropdown doesn't trigger search
- User must manually click search button after selecting category
- Poor user experience for category-based browsing
- No immediate visual feedback for category selection

### Technical Details:
- **Current Implementation**: Category dropdown only works with form submission
- **Missing Feature**: Auto-submit on category change
- **User Experience**: Extra click required for category filtering
- **JavaScript Needed**: Handle dropdown change events

### Implementation Methods:
1. **Auto-submit on change**: Simple JavaScript solution
2. **AJAX category filtering**: More advanced, no page reload
3. **Enhanced UX with loading states**: Better user feedback

### SIMPLEST SOLUTION:
Add JavaScript to auto-submit form on category change:

```html
<!-- In base.html, modify category select -->
<select name="category" class="search-category-select" onchange="this.form.submit()">
    <option value="">All Categories</option>
    {% if categories %}
        {% for cat in categories %}
        <option value="{{ cat['category'] }}" {% if selected_category == cat['category'].lower() %}selected{% endif %}>{{ cat['category'] }}</option>
        {% endfor %}
    {% endif %}
</select>
```

**Enhanced Solution with Loading State:**
```html
<!-- Modified search form with loading indicator -->
<form method="get" action="{{ url_for('search') }}" class="search-form" id="searchForm">
    <div class="search-input-wrapper">
        <button type="submit" class="search-icon-btn">
            <img src="{{ url_for('static', filename='Images/Search_Icon.png') }}" alt="Search" class="search-icon">
        </button>
        <input type="text" name="q" class="search-input" placeholder="Search guitars..." id="searchInput">
        <select name="category" class="search-category-select" id="categorySelect">
            <option value="">All Categories</option>
            {% if categories %}
                {% for cat in categories %}
                <option value="{{ cat['category'] }}" {% if selected_category == cat['category'].lower() %}selected{% endif %}>{{ cat['category'] }}</option>
                {% endfor %}
            {% endif %}
        </select>
        <div class="search-loading" id="searchLoading" style="display: none;">
            <div class="loading-spinner"></div>
        </div>
    </div>
</form>
```

```javascript
// Add to base.html script section
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('categorySelect');
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const searchLoading = document.getElementById('searchLoading');
    
    if (categorySelect && searchForm) {
        categorySelect.addEventListener('change', function() {
            // Show loading state
            if (searchLoading) {
                searchLoading.style.display = 'block';
            }
            
            // Preserve current search query
            const currentQuery = searchInput ? searchInput.value : '';
            
            // Small delay for visual feedback
            setTimeout(function() {
                searchForm.submit();
            }, 300);
        });
    }
});
```

**CSS for Loading Indicator:**
```css
.search-loading {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    align-items: center;
    justify-content: center;
}

.loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Adjust search input wrapper for loading indicator */
.search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.search-category-select {
    transition: all 0.3s ease;
}

.search-category-select:focus {
    outline: none;
    border-color: rgba(255, 255, 255, 0.5);
    box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2);
}
```

**Alternative AJAX Solution (Advanced):**
```javascript
// AJAX category filtering without page reload
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('categorySelect');
    const searchInput = document.getElementById('searchInput');
    const resultsContainer = document.getElementById('searchResults');
    
    if (categorySelect && searchInput) {
        categorySelect.addEventListener('change', function() {
            performSearch();
        });
        
        searchInput.addEventListener('input', debounce(performSearch, 300));
    }
    
    function performSearch() {
        const query = searchInput ? searchInput.value : '';
        const category = categorySelect ? categorySelect.value : '';
        
        // Show loading state
        if (resultsContainer) {
            resultsContainer.style.opacity = '0.5';
        }
        
        fetch(`/search?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}`)
            .then(response => response.text())
            .then(html => {
                // Update results container (would need template restructuring)
                console.log('Search completed');
            })
            .catch(error => {
                console.error('Search error:', error);
            });
    }
    
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
});
```

**Implementation Steps:**
1. Add `onchange="this.form.submit()"` to category select in `base.html`
2. Optional: Add loading spinner for better UX
3. Optional: Add JavaScript for enhanced loading states
4. Test category selection with and without search query
5. Verify URL parameters are correctly maintained

---

## 5) Mobile Search Bar Text Size

### Current Issues:
- Search bar text is too large on mobile devices
- Poor readability and usability on small screens
- Inconsistent with mobile design principles
- Takes up too much horizontal space

### Technical Details:
- **Current CSS**: `.search-input` uses fixed font size for all devices
- **Missing Media Queries**: No mobile-specific styling
- **Impact**: Poor mobile user experience
- **Target**: Reduce font size on screens ≤768px

### Implementation Methods:
1. **Mobile-specific font size**: Simple media query approach
2. **Responsive typography**: Clamp-based fluid sizing
3. **Mobile-optimized layout**: Restructure search for mobile

### SIMPLEST SOLUTION:
Add mobile-specific font size with media query:

```css
/* Add to style.css - Mobile search optimizations */
@media (max-width: 768px) {
    .search-input {
        font-size: 14px !important;
        padding: 8px 12px !important;
    }
    
    .search-category-select {
        font-size: 14px !important;
        padding: 8px 12px !important;
    }
    
    .search-input-wrapper {
        gap: 8px;
    }
}

@media (max-width: 480px) {
    .search-input {
        font-size: 13px !important;
        padding: 6px 10px !important;
    }
    
    .search-category-select {
        font-size: 13px !important;
        padding: 6px 10px !important;
    }
}
```

**Enhanced Solution with Fluid Typography:**
```css
/* Modern fluid typography approach */
.search-input {
    font-size: clamp(13px, 2vw, 16px);
    padding: clamp(6px, 1.5vw, 10px) clamp(10px, 2vw, 15px);
}

.search-category-select {
    font-size: clamp(13px, 2vw, 16px);
    padding: clamp(6px, 1.5vw, 10px) clamp(10px, 2vw, 15px);
}

/* Mobile-specific adjustments */
@media (max-width: 768px) {
    .search-container {
        flex: 1;
        max-width: none;
        margin: 0 8px;
    }
    
    .search-input-wrapper {
        flex-direction: column;
        gap: 8px;
        padding: 8px;
    }
    
    .search-input,
    .search-category-select {
        width: 100%;
        border-radius: 20px;
    }
    
    .search-icon-btn {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        padding: 4px;
    }
    
    /* Adjust search form layout for mobile */
    .search-form {
        position: relative;
    }
    
    .search-form .search-input-wrapper {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        padding: 4px;
    }
    
    .search-form .search-input {
        background: transparent;
        border: none;
        flex: 1;
        padding: 8px 12px;
        color: white;
    }
    
    .search-form .search-input::placeholder {
        color: rgba(255, 255, 255, 0.7);
    }
    
    .search-form .search-category-select {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        margin: 0 4px;
    }
    
    .search-form .search-category-select option {
        background: #e67e50;
        color: white;
    }
}

@media (max-width: 480px) {
    .search-input::placeholder {
        font-size: 12px;
    }
    
    .search-category-select {
        font-size: 12px;
    }
    
    /* Hide category text on very small screens, show icon only */
    .search-category-select {
        max-width: 120px;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
}
```

**Mobile-First Search Layout:**
```css
/* Complete mobile search redesign */
@media (max-width: 768px) {
    header {
        flex-wrap: wrap;
        padding: 8px 12px;
    }
    
    .header-left {
        order: 1;
        flex: 0 0 auto;
    }
    
    .search-container {
        order: 2;
        flex: 1 1 100%;
        margin: 8px 0;
        min-width: 0;
    }
    
    .user-menu,
    .auth-menu {
        order: 3;
        flex: 0 0 auto;
    }
    
    /* Compact search bar */
    .search-form {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 4px;
    }
    
    .search-input-wrapper {
        display: flex;
        align-items: center;
        flex: 1;
        min-width: 0;
    }
    
    .search-input {
        flex: 1;
        min-width: 0;
        background: transparent;
        border: none;
        color: white;
        font-size: 14px;
        padding: 8px 12px;
    }
    
    .search-input::placeholder {
        color: rgba(255, 255, 255, 0.7);
        font-size: 14px;
    }
    
    .search-category-select {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        border-radius: 15px;
        padding: 6px 10px;
        font-size: 12px;
        margin: 0 4px;
        min-width: 80px;
    }
    
    .search-category-select option {
        background: #e67e50;
    }
    
    .search-icon-btn {
        background: none;
        border: none;
        padding: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .search-icon {
        width: 16px;
        height: 16px;
        filter: brightness(0) invert(1);
    }
}

/* Extra small screens */
@media (max-width: 380px) {
    .search-input {
        font-size: 13px;
    }
    
    .search-input::placeholder {
        font-size: 13px;
    }
    
    .search-category-select {
        font-size: 11px;
        padding: 4px 8px;
    }
}
```

**Implementation Steps:**
1. Add mobile-specific font sizes using media queries in `style.css`
2. Optional: Implement fluid typography with `clamp()`
3. Optional: Redesign search layout for mobile-first experience
4. Test search bar on various mobile screen sizes
5. Verify placeholder text and category dropdown are readable

---

## Summary of Implementation Priority

### High Priority (Critical Issues)
1. **Registration Error Handling** - Fixes crash that prevents user registration
2. **Search Authentication** - Security requirement to protect product data

### Medium Priority (User Experience)
3. **Stock Management** - Prevents overselling and improves inventory control
4. **Category Auto-Search** - Improves user experience for category browsing

### Low Priority (UI Enhancement)
5. **Mobile Search Text Size** - Improves mobile usability

### Recommended Implementation Order
1. Fix registration typo and add flash import
2. Add @login_required to search route
3. Implement stock management with transactions
4. Add category auto-submit functionality
5. Optimize mobile search text sizing

Each fix can be implemented independently without affecting others, allowing for incremental improvements to the application.