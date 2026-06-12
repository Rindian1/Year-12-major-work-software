# Guitar Store Flask App - Project Summary

## Overview
This is a Flask-based web application for a guitar store, featuring user authentication, product search, detailed product pages with YouTube video demos, shopping cart functionality, and a hybrid ML-based recommendation system. The app uses SQLite for data storage, integrates with the YouTube API for sound test videos, and implements personalized product recommendations using KNN collaborative filtering and content-based filtering.

## Architecture
- **Backend**: Flask web framework with SQLite database
- **Frontend**: Jinja2 templates with CSS styling
- **Database**: SQLite with tables for `users`, `cart_items`, `products`, `recently_viewed`, `user_surveys`, `product_interactions`, and `recommendation_cache`
- **External APIs**: YouTube Data API v3 for video search and retrieval
- **ML System**: Hybrid KNN recommender (user-CF + item-CF + content-based) using scikit-learn, pandas, and numpy
- **Authentication**: Flask-Login for user authentication and session management
- **Key Features**:
  - User registration, login, and profile management
  - Product search and filtering with category and sorting options
  - Product detail pages with video demos
  - Shopping cart functionality with stock management
  - YouTube video integration for sound tests
  - User preference survey for personalized recommendations
  - Hybrid ML recommendations (collaborative filtering + content-based)
  - Recently viewed products tracking
  - Product interaction tracking for ML model training

## File Structure
- `app.py`: Main application file with routes, database logic, authentication, and recommendation API
- `ml_recommender.py`: Hybrid KNN recommender system (user-CF + item-CF + content-based)
- `ml/`: Machine learning module
  - `config.py`: ML configuration and weights
  - `data_loader.py`: Database data loading for ML models
  - `feature_engineering.py`: Feature engineering for user and product data
  - `knn_models.py`: KNN-based recommendation models
- `youtube_search.py`: Script for generating YouTube video data
- `fetch_missing_images.py`: Script for downloading missing product images
- `templates/`: HTML templates (base.html, index.html, search.html, product_detail.html, shopping_cart.html, survey.html, recommendations.html, register.html, login.html)
- `static/`: Static assets (Images/, CSS files)
- `migrations/`: Database migration scripts
  - `001_add_youtube_links.py`: Add YouTube links column to products
  - `002_populate_youtube_links.py`: Populate YouTube links for products
  - `003_create_survey_tables.py`: Create user survey tables
  - `004_seed_ml_data.py`: Seed ML training data
  - `005_expand_ml_data.py`: Expand ML dataset
  - `006_seed_more_surveys.py`: Add more survey data
  - `007_remove_budget_from_surveys.py`: Remove budget feature from surveys
- `Planning files/`: Feature planning documents
- `instance/cart.db`: SQLite database file
- `requirements.txt`: Python dependencies (Flask, scikit-learn, pandas, numpy, Flask-Login, email-validator)

## Current Functionality
1. **Home Page**: Displays cart items, recently viewed products, and personalized recommendations for authenticated users
2. **Authentication System**: User registration with email validation, login/logout, session management with Flask-Login
3. **Search Page**: Product search with category filtering, sorting by name/price/date, and cart status indicators
4. **Product Detail Page**: Individual product view with YouTube video grid, stock information, and add-to-cart functionality
5. **Shopping Cart**: Cart management with quantity updates, stock checking, and total calculation
6. **Survey System**: User preference collection (skill level, instrument type, preferred genres) for ML recommendations
7. **ML Recommendations**: Hybrid KNN recommender combining user-based collaborative filtering, item-based collaborative filtering, and content-based filtering
8. **Product Interaction Tracking**: Logs user interactions (views, cart additions) for ML model training
9. **Recently Viewed**: Tracks and displays recently viewed products per user
10. **YouTube Integration**: Automated video search and display for products (when available)
11. **Stock Management**: Real-time stock checking and updates for products

## Database Schema

### Core Tables
- **users**: User authentication and profile information (id, username, email, password_hash, created_at, last_login)
- **products**: Product catalog (id, name, category, price, description, image_url, stock, created_at, youtube_links, genre_suitability, skill_level, instrument_type)
- **cart_items**: User shopping cart items (id, user_id, name, price, product_id, quantity, created_at)
- **recently_viewed**: Track user's recently viewed products (id, user_id, product_id, viewed_at)

### ML-Related Tables
- **user_surveys**: User preference data for recommendations (user_id, skill_level, instrument_type, preferred_genres, created_at, updated_at)
- **product_interactions**: User interaction logs for ML training (user_id, product_id, action, duration, frequency, created_at)
- **recommendation_cache**: Cached recommendations to improve performance (user_id, product_id, score, algorithm, reason, expires_at, created_at)

## Known Issues and Limitations

### Current Issues
1. **YouTube Integration**: YouTube links may not display for all products depending on data availability from migrations
2. **SQL Injection Risk**: Login route uses string interpolation for username/email query (should use parameterized queries)
3. **Password Security**: Passwords stored in plain text (should use hashing with bcrypt or similar)
4. **CSRF Protection**: No CSRF tokens on forms, vulnerable to CSRF attacks
5. **Database Concurrency**: Uses `check_same_thread=False` which can cause concurrency problems
6. **Error Handling**: Limited error handling in some routes; exceptions may cause 500 errors

### ML System Limitations
1. **Cold Start Problem**: New users with no interactions get less accurate recommendations
2. **Data Sparsity**: Limited user interaction data may affect recommendation quality
3. **Performance**: KNN models can be slow with large datasets
4. **Cache Expiration**: Recommendations cached for 24 hours may become stale

## Suggested Improvements

### Security Enhancements (Priority: High)
1. **Password Hashing**: Implement bcrypt or similar for password storage (currently plain text)
2. **SQL Injection Fix**: Replace string interpolation in login route with parameterized queries
3. **CSRF Protection**: Implement Flask-WTF for form security
4. **Input Sanitization**: Use WTForms for comprehensive input validation
5. **HTTPS Enforcement**: Ensure all traffic is encrypted in production
6. **Session Security**: Use secure session cookies with proper configuration

### Performance Optimizations (Priority: Medium)
1. **Database Indexing**: Add indexes on frequently queried columns (user_id, product_id, category)
2. **ML Model Optimization**: Consider using approximate nearest neighbors for large datasets
3. **Pagination**: Add pagination to search results and recommendations
4. **Lazy Loading**: Load YouTube thumbnails on demand
5. **Database Connection Pooling**: Use SQLAlchemy instead of raw SQLite for better connection management

### Code Quality Improvements (Priority: Medium)
1. **Testing**: Add unit tests and integration tests (pytest) for ML models and routes
2. **Code Organization**: Separate concerns (models, views, services) - consider Flask blueprints
3. **Configuration Management**: Use environment variables for all config (SECRET_KEY, DB_PATH)
4. **Logging**: Implement proper logging throughout the app (currently using print statements)
5. **Documentation**: Add docstrings and API documentation

### ML System Enhancements (Priority: Medium)
1. **Algorithm Diversity**: Add matrix factorization or deep learning models alongside KNN
2. **Real-time Updates**: Implement incremental model updates instead of full refresh
3. **A/B Testing**: Framework for testing different recommendation algorithms
4. **Explainability**: Improve recommendation explanations with more detailed reasoning
5. **Cold Start Solutions**: Implement better strategies for new users (popular items, demographic-based)

### Feature Enhancements (Priority: Low)
1. **Product Reviews**: User reviews and ratings system
2. **Wishlist**: Add wishlist functionality for saved products
3. **Order History**: Track past purchases for repeat customers
4. **Payment Integration**: Stripe or PayPal integration for checkout
5. **Email Notifications**: Order confirmations and promotional emails
6. **Admin Dashboard**: Interface for managing products, users, and viewing analytics
7. **Mobile Responsiveness**: Further improve mobile UI and PWA features
8. **SEO Optimization**: Meta tags, sitemaps, and structured data

## Dependencies Analysis
**Current Dependencies** (from requirements.txt):
- Flask 2.3.3: Web framework
- Werkzeug 2.3.7: WSGI utility library for Flask
- Jinja2 3.1.2: Template engine for Flask
- itsdangerous 2.1.2: Security utilities for Flask
- click 8.1.7: Command-line interface for Flask
- python-dotenv 1.0.0: Environment variable management
- google-api-python-client>=2.0.0: Google API client for YouTube integration
- Flask-Login 0.6.3: User authentication and session management
- email-validator 2.0.0: Email validation for registration
- scikit-learn>=1.3.0: Machine learning library for KNN models
- pandas>=2.0.0: Data manipulation for ML models
- numpy>=1.24.0: Numerical computing for ML models

**Status**: Dependencies are well-maintained and appropriate for the current feature set. The ML dependencies (scikit-learn, pandas, numpy) are essential for the recommendation system.

**Recommendations**:
- Consider pinning specific versions for production stability
- Add requirements-dev.txt for development dependencies (pytest, black, flake8)
- Use virtual environment for dependency isolation (already implemented)

## Deployment Considerations
1. **Production Database**: Migrate from SQLite to PostgreSQL for better concurrency and performance
2. **Environment Variables**: Proper .env management (SECRET_KEY, DATABASE_URL, YouTube API keys)
3. **Static File Serving**: Use CDN for static assets (product images, CSS, JS)
4. **ML Model Deployment**: Consider separate service for ML recommendations if scaling
5. **Monitoring**: Add error tracking (Sentry) and analytics (Google Analytics)
6. **Backup Strategy**: Database backups and recovery procedures
7. **Scaling**: Prepare for horizontal scaling if needed (load balancer, multiple app instances)
8. **HTTPS**: Enable SSL/TLS for all traffic in production

## Priority Action Items

### Critical Security Issues (Immediate)
1. **Implement Password Hashing** - Replace plain text password storage with bcrypt
2. **Fix SQL Injection Vulnerability** - Replace string interpolation in login route with parameterized queries
3. **Add CSRF Protection** - Implement Flask-WTF for form security

### High Priority
4. **Improve Error Handling** - Add comprehensive error handling and logging
5. **Add Input Validation** - Strengthen validation on all user inputs
6. **Database Indexing** - Add indexes on frequently queried columns for performance

### Medium Priority
7. **Implement Testing Suite** - Add unit tests and integration tests (pytest)
8. **Refactor Database Layer** - Consider using SQLAlchemy for better connection management
9. **ML Model Monitoring** - Add metrics and monitoring for recommendation quality
10. **Configuration Management** - Move all configuration to environment variables

### Low Priority
11. **UI/UX Improvements** - Enhance mobile responsiveness and add loading states
12. **Feature Enhancements** - Add product reviews, wishlist, and order history
13. **Documentation** - Add comprehensive API documentation and developer guide

## Conclusion

This project has evolved from a basic guitar store e-commerce application to a sophisticated platform with user authentication, personalized ML recommendations, and comprehensive product management. The hybrid KNN recommendation system combines collaborative filtering and content-based approaches to provide personalized product suggestions based on user preferences and interaction history.

While the core functionality is solid, there are critical security issues that need immediate attention, particularly around password storage and SQL injection prevention. The ML system provides good recommendations but could benefit from additional algorithms and better cold-start handling.

The application is well-structured with clear separation of concerns between the web layer, ML layer, and data layer, making it maintainable and extensible for future enhancements.
