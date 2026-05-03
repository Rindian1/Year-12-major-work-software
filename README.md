# Guitar Store E-Commerce Application

A full-featured e-commerce web application for guitar enthusiasts built with Flask. This application includes user authentication, product browsing, shopping cart functionality, and personalized shopping lists.

## Features

- **User Authentication**: Registration, login, logout with secure password hashing
- **Product Catalog**: Browse guitars, amplifiers, effects, and accessories
- **Search & Filter**: Advanced search with category filtering and sorting
- **Shopping Cart**: Add/remove items, quantity management with stock checking
- **Personalized Dashboard**: Shopping list and recently viewed items
- **Product Details**: Detailed product pages with descriptions and images
- **Responsive Design**: Mobile-friendly interface with modern UI

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "guitar store v1"
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5001`

## Database Setup

### Database Initialization

The application automatically initializes the SQLite database on first run. The database is stored in the `instance/cart.db` file.

### Manual Database Operations

If you need to manually initialize or reset the database:

```bash
# Start Python shell
python

# Then run these commands:
>>> from app import init_db, seed_products, update_product_images
>>> init_db()  # Create database tables
>>> seed_products()  # Add sample products
>>> update_product_images()  # Set product images
>>> exit()
```

### Database Schema

The application uses the following tables:

- **users**: User authentication and profile information
- **products**: Product catalog with details and stock
- **cart_items**: User shopping cart items with quantities
- **recently_viewed**: Track user's recently viewed products

## Run Commands

### Development Server

```bash
# Run in development mode with debug enabled
python app.py

# Alternative with Flask
flask run --host=0.0.0.0 --port=5001 --debug
```

### Production Mode

```bash
# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False

# Run with production server
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## Deployment

### Heroku Deployment

1. **Create Procfile**
   ```text
   web: gunicorn app:app
   ```

2. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   heroku config:set FLASK_ENV=production
   git push heroku main
   ```

### Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5001
   CMD ["python", "app.py"]
   ```

2. **Build and run**
   ```bash
   docker build -t guitar-store .
   docker run -p 5001:5001 guitar-store
   ```

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `SECRET_KEY`: Change the default secret key in production
- `DATABASE_URL`: Optional database URL for PostgreSQL/MySQL

## Route Table

| Method | Path | Description | Authentication |
|--------|------|-------------|----------------|
| **GET** | `/` | Home page with dashboard | Optional |
| **GET** | `/index.html` | Redirect to home page | Optional |
| **GET** | `/page-2.html` | Static page 2 | Optional |
| **GET** | `/search` | Product search and catalog | Required |
| **POST** | `/add-item` | Add custom item to cart | Required |
| **POST** | `/remove-item/<int:item_id>` | Remove item from cart | Required |
| **GET** | `/product/<int:product_id>` | Product detail page | Optional |
| **GET** | `/shopping-cart` | Shopping cart page | Required |
| **POST** | `/add-to-cart` | Add product to cart | Required |
| **POST** | `/update-cart-quantity` | Update cart item quantity | Required |
| **GET** | `/register` | User registration page | Optional |
| **POST** | `/register` | Process user registration | Optional |
| **GET** | `/login` | User login page | Optional |
| **POST** | `/login` | Process user login | Optional |
| **POST** | `/logout` | Process user logout | Required |
| **PUT** | `/api/product/<int:product_id>/stock` | Update product stock quantity | Required |

### HTTP Methods Used

- **GET**: Retrieve data (pages, product listings, search results)
- **POST**: Submit data (add items, update quantities, authentication)
- **PUT**: Update resources (product stock management)
- **DELETE**: Not currently implemented (could be used for API endpoints)

## API Endpoints

### Cart Management

- **Add to Cart**: `POST /add-to-cart`
  - Parameters: `product_id`, `quantity` (optional)
  - Returns: JSON response with success status and message

- **Update Quantity**: `POST /update-cart-quantity`
  - Parameters: `item_id`, `quantity`
  - Returns: JSON response with updated totals

### Product Management

- **Update Stock**: `PUT /api/product/<int:product_id>/stock`
  - Parameters: JSON body with `stock` field
  - Returns: JSON response with success status and stock changes
  - Example: `{"stock": 25}`

## Database Seed Data

The application includes sample products across these categories:

- **Electric Guitars**: Fender Stratocaster, Gibson Les Paul, PRS Custom 24
- **Acoustic Guitars**: Martin D-28, Taylor 814ce, Yamaha FG800
- **Bass Guitars**: Fender Precision Bass
- **Amplifiers**: Fender Deluxe Reverb, Marshall DSL40CR, Boss Katana-50
- **Effects Pedals**: Boss DS-1, Ibanez TS9, Strymon BigSky

## Configuration

### Security Considerations

1. **Secret Key**: Change `app.secret_key` in production
2. **Database**: Use PostgreSQL/MySQL for production
3. **HTTPS**: Enable SSL in production
4. **CSRF**: Consider adding CSRF protection

### Customization

- **Products**: Modify `seed_products()` function for custom inventory
- **Categories**: Update product categories in the database
- **Styling**: Modify CSS in `static/style.css`
- **Templates**: Customize HTML templates in `templates/` directory

## Troubleshooting

### Common Issues

1. **Database Permission Error**
   ```bash
   chmod 755 instance/
   ```

2. **Port Already in Use**
   ```bash
   # Kill process on port 5001
   lsof -ti:5001 | xargs kill -9
   ```

3. **Import Errors**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

### Development Tips

- Use `FLASK_DEBUG=1` for development debugging
- Database is automatically created in `instance/` directory
- Images should be placed in `static/Images/` folder
- Logs are printed to console for debugging

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the route table for correct endpoints
3. Verify database initialization
4. Ensure all dependencies are installed

## License

This project is for educational purposes. Feel free to modify and distribute.