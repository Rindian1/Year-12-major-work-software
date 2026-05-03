from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import abort
from flask import flash
import sqlite3
import os
from flask import g 
from flask import jsonify
import json
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__, instance_relative_config=True)
app.secret_key = 'your-secret-key-change-in-production'

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# --- Database helpers ---
# Use instance folder for database (works regardless of parent folder name)
import os

# Ensure instance directory exists
os.makedirs(app.instance_path, exist_ok=True)

# Database will be stored in instance/cart.db
DB_PATH = os.path.join(app.instance_path, 'cart.db')
print(f"Using database at: {DB_PATH}")  # Helpful for debugging

def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.row_factory = sqlite3.Row
    return db

def get_cart_items():
    """Helper function to get cart items for the current user"""
    if not current_user.is_authenticated:
        return []
    db = get_db()
    return db.execute('SELECT id, name, price FROM cart_items WHERE user_id = ? ORDER BY id DESC', (current_user.id,)).fetchall()

def get_categories():
    """Helper function to get all product categories"""
    db = get_db()
    return db.execute('SELECT DISTINCT category FROM products ORDER BY category').fetchall()

@app.context_processor
def inject_globals():
    """Make global variables available to all templates"""
    return {
        'categories': get_categories()
    }

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()

def init_db():
    try:
        print(f"Initializing database at: {DB_PATH}")
        db = get_db()
        
        # Enable foreign key support
        db.execute('PRAGMA foreign_keys = ON')
        
        # Create tables with error handling
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS cart_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                price REAL NOT NULL DEFAULT 0,
                product_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

        # Add user_id column if it doesn't exist (for existing databases)
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(cart_items)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE cart_items ADD COLUMN user_id INTEGER')
        if 'product_id' not in columns:
            cursor.execute('ALTER TABLE cart_items ADD COLUMN product_id INTEGER')
        if 'quantity' not in columns:
            cursor.execute('ALTER TABLE cart_items ADD COLUMN quantity INTEGER DEFAULT 1')
        
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                description TEXT,
                image_url TEXT,
                stock INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS recently_viewed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_id INTEGER NOT NULL,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            """
        )
        db.commit()
        print("Database initialized successfully")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        raise

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(user['id'], user['username'], user['email'], user['password_hash'])
    return None

def seed_products():
    """Seed sample products if products table is empty."""
    db = get_db()
    count = db.execute('SELECT COUNT(*) AS c FROM products').fetchone()['c']
    if count == 0:
        db.executemany(
            'INSERT INTO products (name, category, price, description, image_url, stock) VALUES (?, ?, ?, ?, ?, ?)',
            [
                (
                    'Fender Stratocaster',
                    'Electric',
                    799.99,
                    'Classic electric guitar with versatile tone',
                    '/static/Images/Fender Stratocaster.jpeg',
                    10,
                ),
                (
                    'Gibson Les Paul',
                    'Electric',
                    1299.99,
                    'Iconic solid-body electric guitar',
                    '/static/Images/Gibson les paul.webp',
                    5,
                ),
                (
                    'Martin D-28',
                    'Acoustic',
                    2499.99,
                    'Premium acoustic guitar with rich tone',
                    '/static/Images/Martin D-28.jpeg',
                    8,
                ),
                (
                    'Fender Precision Bass',
                    'Bass',
                    899.99,
                    'Legendary bass guitar',
                    '/static/Images/fender precision bass.jpeg',
                    7,
                ),
                (
                    'Fender Telecaster',
                    'Electric',
                    849.99,
                    'Classic country and rock guitar',
                    '/static/Images/Fender telecaster.png',
                    6,
                ),
                (
                    'Gibson SG Standard',
                    'Electric',
                    1199.99,
                    'Rock and blues powerhouse',
                    '/static/Images/Gibson SG Standard.png',
                    4,
                ),
                (
                    'PRS Custom 24',
                    'Electric',
                    3499.99,
                    'Premium American-made electric guitar',
                    '/static/Images/PRS Custom 24.png',
                    3,
                ),
                (
                    'Taylor 814ce',
                    'Acoustic',
                    2899.99,
                    'Premium acoustic-electric guitar',
                    '/static/Images/Taylor 814ce.jpeg',
                    5,
                ),
                (
                    'Yamaha FG800',
                    'Acoustic',
                    299.99,
                    'Affordable beginner acoustic guitar',
                    '/static/Images/Yamaha FG800.jpeg',
                    15,
                ),
                (
                    'Fender Deluxe Reverb',
                    'Amplifier',
                    999.99,
                    'Classic tube amplifier',
                    '/static/Images/Fender Deluxe Reverb.jpg',
                    4,
                ),
                (
                    'Marshall DSL40CR',
                    'Amplifier',
                    699.99,
                    'British rock amplifier',
                    '/static/Images/Marshall DSL40CR.jpeg',
                    6,
                ),
                (
                    'Boss Katana-50',
                    'Amplifier',
                    229.99,
                    'Versatile modeling amplifier',
                    '/static/Images/Boss Katana-50.jpeg',
                    8,
                ),
                (
                    'Boss DS-1 Distortion',
                    'Effects',
                    49.99,
                    'Classic distortion pedal',
                    '/static/Images/Boss DS-1 Distortion.jpg',
                    20,
                ),
                (
                    'Ibanez TS9 Tube Screamer',
                    'Effects',
                    89.99,
                    'Legendary overdrive pedal',
                    '/static/Images/Ibanez TS9 Tube Screamer.jpg',
                    12,
                ),
                (
                    'Electro-Harmonix Small Clone',
                    'Effects',
                    79.99,
                    'Classic analog chorus pedal',
                    '/static/Images/Electro-Harmonix Small Clone.jpg',
                    10,
                ),
                (
                    'Strymon BigSky Reverb',
                    'Effects',
                    479.99,
                    'Premium reverb pedal',
                    '/static/Images/Strymon BigSky Reverb.avif',
                    3,
                ),
                (
                    'TC Electronic Ditto Looper',
                    'Effects',
                    129.99,
                    'Simple loop pedal',
                    '/static/Images/TC Electronic Ditto Looper.jpeg',
                    7,
                ),
            ],
        )
        db.commit()

def update_product_images():
    """Update existing products with appropriate images."""
    db = get_db()
    
    # Update all 24 products with specific images
    product_image_mapping = {
        1: '/static/Images/Fender Stratocaster.jpeg',      # Fender Stratocaster
        2: '/static/Images/Gibson les paul.webp',         # Gibson Les Paul
        3: '/static/Images/Martin D-28.jpeg',             # Martin D-28
        4: '/static/Images/fender precision bass.jpeg',   # Fender Precision Bass
        5: '/static/Images/Fender telecaster.png',        # Fender Telecaster
        6: '/static/Images/Taylor 814ce.jpeg',            # Taylor 814ce
        7: '/static/Images/PRS Custom 24.png',            # PRS Custom 24
        8: '/static/Images/Gibson SG Standard.png',       # Gibson SG Standard
        9: '/static/Images/Yamaha FG800.jpeg',            # Yamaha FG800
        10: '/static/Images/Boss DS-1 Distortion.jpg',    # Boss DS-1 Distortion
        11: '/static/Images/Strymon BigSky Reverb.avif',  # Strymon BigSky Reverb
        12: '/static/Images/Ibanez TS9 Tube Screamer.jpg', # Ibanez TS9 Tube Screamer
        13: '/static/Images/TC Electronic Ditto Looper.jpeg', # TC Electronic Ditto Looper
        14: '/static/Images/Electro-Harmonix Small Clone.jpg', # Electro-Harmonix Small Clone
        15: '/static/Images/Fender Deluxe Reverb.jpg',    # Fender Deluxe Reverb
        16: '/static/Images/Marshall DSL40CR.jpeg',       # Marshall DSL40CR
        17: '/static/Images/Boss Katana-50.jpeg',         # Boss Katana-50
        18: '/static/Images/Dunlop Tortex Picks (1.0mm).jpg', # Dunlop Tortex Picks
        19: '/static/Images/DAddario EXL110 Strings.webp',   # DAddario EXL110 Strings
        20: '/static/Images/Planet Waves Cable 10ft.webp',   # Planet Waves Cable 10ft
        21: '/static/Images/Snark SN-5X Tuner.png',          # Snark SN-5X Tuner
        22: '/static/Images/Fender Deluxe Molded Case.webp',  # Fender Deluxe Molded Case
        23: '/static/Images/Gator GC-LTD Gig Bag.jpg',        # Gator GC-LTD Gig Bag
        24: '/static/Images/Mono M80 Electric Case.webp',     # Mono M80 Electric Case
    }
    
    # Update all products with their specific images
    for product_id, image_url in product_image_mapping.items():
        db.execute('UPDATE products SET image_url = ? WHERE id = ?', (image_url, product_id))
    
    # Set filler image for any new products that might be added in the future
    db.execute(
        'UPDATE products SET image_url = ? WHERE image_url IS NULL OR image_url = ""',
        ('/static/Images/FILLER.png',)
    )
    
    db.commit()

@app.before_request
def setup():
    init_db()
    seed_products()
    update_product_images()

# --- Routes ---
@app.route('/')
def home():
    db = get_db()
    if current_user.is_authenticated:
        items = db.execute('SELECT id, name, price FROM cart_items WHERE user_id = ? ORDER BY id DESC', (current_user.id,)).fetchall()
        # Get recently viewed products for this user
        recently_viewed = db.execute('''
            SELECT p.id, p.name, p.price 
            FROM recently_viewed rv
            JOIN products p ON rv.product_id = p.id
            WHERE rv.user_id = ?
            ORDER BY rv.viewed_at DESC
            LIMIT 5
        ''', (current_user.id,)).fetchall()
    else:
        items = []  # No cart items for non-authenticated users
        recently_viewed = []  # No recently viewed for non-authenticated users
    total = sum((row['price'] or 0) for row in items)
    return render_template('index.html', cart_items=items, cart_total=total, recently_viewed=recently_viewed)

@app.route('/page-2.html')
def page2():
    return render_template('page-2.html')

@app.route('/index.html')
def index():
    return home()

@app.route('/add-item', methods=['POST'])
@login_required
def add_item():
    name = request.form.get('name', '').strip()
    price_raw = request.form.get('price', '0').strip()
    try:
        price = float(price_raw)
    except ValueError:
        price = 0.0
    if name:
        db = get_db()
        db.execute('INSERT INTO cart_items (name, price, user_id) VALUES (?, ?, ?)', (name, price, current_user.id))
        db.commit()
    return redirect(url_for('home'))

@app.route('/remove-item/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id: int):
    db = get_db()
    db.execute('DELETE FROM cart_items WHERE id = ? AND user_id = ?', (item_id, current_user.id))
    db.commit()
    return redirect(url_for('home'))

@app.route('/search')
@login_required
def search():
    query = (request.args.get('q') or '').strip()
    category = (request.args.get('category') or '').strip().lower()

    db = get_db()
    sql = 'SELECT * FROM products WHERE 1=1'
    params = []

    if query:
        sql += ' AND (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)'
        term = f"%{query.lower()}%"
        params.extend([term, term])

    if category:
        sql += ' AND LOWER(category) = ?'
        params.append(category)

    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    valid_sort_columns = ['name', 'price', 'created_at']
    if sort_by not in valid_sort_columns:
        sort_by = 'name'
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'asc'
    sql += f' ORDER BY {sort_by} {sort_order.upper()}'

    products = db.execute(sql, params).fetchall()
    categories = db.execute('SELECT DISTINCT category FROM products').fetchall()
    cart_items = get_cart_items()

    # Check cart status for each product
    products_with_cart_status = []
    for product in products:
        product_dict = dict(product)
        product_dict['in_cart'] = False
        if current_user.is_authenticated:
            product_dict['in_cart'] = db.execute('SELECT COUNT(*) AS count FROM cart_items WHERE name = ? AND user_id = ?', 
                                                (product['name'], current_user.id)).fetchone()['count'] > 0
        products_with_cart_status.append(product_dict)

    return render_template(
        'search.html',
        products=products_with_cart_status,
        search_query=query,
        selected_category=category,
        categories=categories,
        sort_by=sort_by,
        sort_order=sort_order,
        cart_items=cart_items,
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id: int):
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        abort(404)

    # Track recently viewed product if user is authenticated
    if current_user.is_authenticated:
        # Check if product is already in recently viewed for this user
        existing = db.execute('SELECT id FROM recently_viewed WHERE user_id = ? AND product_id = ?', 
                            (current_user.id, product_id)).fetchone()
        if existing:
            # Update the timestamp
            db.execute('UPDATE recently_viewed SET viewed_at = CURRENT_TIMESTAMP WHERE id = ?', 
                      (existing['id'],))
        else:
            # Add to recently viewed
            db.execute('INSERT INTO recently_viewed (user_id, product_id) VALUES (?, ?)', 
                      (current_user.id, product_id))
        
        # Keep only the 5 most recent items for this user
        db.execute('DELETE FROM recently_viewed WHERE user_id = ? AND id NOT IN (SELECT id FROM recently_viewed WHERE user_id = ? ORDER BY viewed_at DESC LIMIT 5)', 
                  (current_user.id, current_user.id))
        db.commit()

    detailed_description = (
        (product['description'] or 'No description available.') +
        ' This is a detailed overview of the instrument, its tone, build, and typical use cases.'
    )

    # Check if product is already in cart
    in_cart = False
    if current_user.is_authenticated:
        in_cart = db.execute('SELECT COUNT(*) AS count FROM cart_items WHERE name = ? AND user_id = ?', 
                           (product['name'], current_user.id)).fetchone()['count'] > 0

    # Get YouTube links if they exist
    youtube_links = []
    if 'youtube_links' in product.keys() and product['youtube_links']:
        try:
            youtube_links = json.loads(product['youtube_links'])
        except (json.JSONDecodeError, TypeError):
            youtube_links = []

    cart_items = get_cart_items()

    return render_template(
        'product_detail.html',
        product=product,
        detailed_description=detailed_description,
        youtube_links=youtube_links,
        in_cart=in_cart,
        cart_items=cart_items,
    )

@app.route('/shopping-cart')
@login_required
def shopping_cart():
    db = get_db()
    items = db.execute('''
        SELECT ci.id, ci.name, ci.price, ci.quantity, p.image_url 
        FROM cart_items ci
        LEFT JOIN products p ON ci.product_id = p.id
        WHERE ci.user_id = ? 
        ORDER BY ci.id DESC
    ''', (current_user.id,)).fetchall()
    total = sum((row['price'] or 0) * (row['quantity'] or 1) for row in items)
    return render_template('shopping_cart.html', cart_items=items, cart_total=total)

@app.route('/update-cart-quantity', methods=['POST'])
@login_required
def update_cart_quantity():
    item_id = request.form.get('item_id')
    quantity = request.form.get('quantity')
    
    if not item_id or not quantity:
        return jsonify({'success': False, 'error': 'Item ID and quantity are required'}), 400
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return jsonify({'success': False, 'error': 'Quantity must be at least 1'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid quantity'}), 400
    
    db = get_db()
    try:
        # Get the cart item and product to check stock
        item = db.execute('''
            SELECT ci.quantity, p.stock, p.price 
            FROM cart_items ci
            LEFT JOIN products p ON ci.product_id = p.id
            WHERE ci.id = ? AND ci.user_id = ?
        ''', (item_id, current_user.id)).fetchone()
        
        if not item:
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        
        # Check stock availability
        if item['stock'] > 0 and quantity <= item['stock']:
            db.execute('UPDATE cart_items SET quantity = ? WHERE id = ? AND user_id = ?', 
                      (quantity, item_id, current_user.id))
            db.commit()
            
            # Calculate new item total and cart total
            new_item_total = (item['price'] or 0) * quantity
            all_items = db.execute('SELECT price, quantity FROM cart_items WHERE user_id = ?', 
                                  (current_user.id,)).fetchall()
            new_cart_total = sum((row['price'] or 0) * (row['quantity'] or 1) for row in all_items)
            
            return jsonify({
                'success': True, 
                'message': 'Quantity updated',
                'new_item_total': new_item_total,
                'new_cart_total': new_cart_total
            })
        else:
            return jsonify({'success': False, 'error': 'Insufficient stock available'}), 400
            
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

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
        # Fetch the product details
        product = db.execute('SELECT name, price, stock FROM products WHERE id = ?', (product_id,)).fetchone()
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Check if item already exists in cart
        existing_item = db.execute('SELECT id, quantity FROM cart_items WHERE product_id = ? AND user_id = ?', 
                                  (product_id, current_user.id)).fetchone()
        
        if existing_item:
            # Update quantity of existing item
            new_quantity = existing_item['quantity'] + quantity
            # Check stock availability
            if product['stock'] > 0 and new_quantity <= product['stock']:
                db.execute('UPDATE cart_items SET quantity = ? WHERE id = ?', (new_quantity, existing_item['id']))
                db.commit()
                return jsonify({'success': True, 'message': 'Product added to cart', 'quantity': new_quantity})
            else:
                return jsonify({'success': False, 'error': 'Insufficient stock available'}), 400
        else:
            # Add new item to cart
            if product['stock'] > 0 and quantity <= product['stock']:
                db.execute('INSERT INTO cart_items (name, price, user_id, product_id, quantity) VALUES (?, ?, ?, ?, ?)', 
                          (product['name'], product['price'], current_user.id, product_id, quantity))
                db.commit()
                return jsonify({'success': True, 'message': 'Added to cart', 'quantity': quantity})
            else:
                return jsonify({'success': False, 'error': 'Insufficient stock available'}), 400
                
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/product/<int:product_id>/stock', methods=['PUT'])
@login_required
def update_product_stock(product_id: int):
    """Update product stock quantity (admin function)"""
    data = request.get_json()
    if not data or 'stock' not in data:
        return jsonify({'success': False, 'error': 'Stock quantity is required'}), 400
    
    try:
        new_stock = int(data['stock'])
        if new_stock < 0:
            return jsonify({'success': False, 'error': 'Stock cannot be negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Invalid stock quantity'}), 400
    
    db = get_db()
    try:
        # Check if product exists
        product = db.execute('SELECT id, name, stock FROM products WHERE id = ?', (product_id,)).fetchone()
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Update stock
        db.execute('UPDATE products SET stock = ? WHERE id = ?', (new_stock, product_id))
        db.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Stock updated for {product["name"]}',
            'old_stock': product['stock'],
            'new_stock': new_stock
        })
        
    except Exception as e:
        db.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# --- Authentication Routes ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        errors = []
        
        # Validate username
        if not username:
            errors.append('Username is required')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        elif len(username) > 15:
            errors.append('Username must be no more than 15 characters long')
        elif not username.replace('_', '').replace('-', '').isalnum():
            errors.append('Username can only contain letters, numbers, underscores, and hyphens')
        
        # Validate email
        if not email:
            errors.append('Email is required')
        else:
            try:
                validate_email(email)
            except EmailNotValidError as e:
                errors.append('Please enter a valid email address')
        
        # Validate password
        if not password:
            errors.append('Password is required')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long')
        
        # Validate password confirmation
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if username already exists
        if username and len(username) >= 3 and len(username) <= 15:
            db = get_db()
            existing_user = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
            if existing_user:
                errors.append('Username already exists')
        
        # Check if email already exists
        if email and not any('Email' in error for error in errors):  # Only check if email is valid
            try:
                db = get_db()
                existing_email = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
                if existing_email:
                    errors.append('Email already registered')
            except Exception as e:
                errors.append('Unable to verify email availability')
        
        if errors:
            return render_template('register.html', errors=errors, username=username, email=email)
        
        # Create new user
        try:
            db = get_db()
            password_hash = generate_password_hash(password)
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
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    username_or_email = request.form.get('username_or_email', '').strip()
    password = request.form.get('password', '')
    remember = request.form.get('remember') == 'on'
    
    if not username_or_email or not password:
        return render_template('login.html', error='Please enter username/email and password')
    
    db = get_db()
    
    # Find user by username or email
    user = db.execute('SELECT * FROM users WHERE username = ? OR email = ?', 
                     (username_or_email, username_or_email)).fetchone()
    
    if not user or not check_password_hash(user['password_hash'], password):
        return render_template('login.html', error='Invalid username/email or password')
    
    # Update last login
    db.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user['id'],))
    db.commit()
    
    # Log the user in
    login_user(User(user['id'], user['username'], user['email'], user['password_hash']), remember=remember)
    
    return redirect(url_for('home'))

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)