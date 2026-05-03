# User Authentication and Personalized Shopping Lists Implementation Plan

## Overview
This plan outlines the implementation of user authentication and personalized shopping lists for the guitar store application. Each user will have their own account and shopping cart, allowing for a personalized experience.

## Current State Analysis
- **Current Database**: Single `cart_items` table shared across all users
- **Authentication**: None currently implemented
- **Session Management**: Basic Flask session handling
- **UI**: Shows placeholder `<username>` in welcome message

## Implementation Phases

### Phase 1: Database Schema Updates
**Files to modify**: `app.py` (database initialization)

#### New Tables Required:
1. **Users Table**
   ```sql
   CREATE TABLE users (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT UNIQUE NOT NULL,
       email TEXT UNIQUE NOT NULL,
       password_hash TEXT NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       last_login TIMESTAMP
   )
   ```

2. **Updated Cart Items Table**
   ```sql
   -- Add user_id foreign key to existing cart_items table
   ALTER TABLE cart_items ADD COLUMN user_id INTEGER REFERENCES users(id)
   
   -- For new installations, create with user_id from start
   CREATE TABLE cart_items (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       name TEXT NOT NULL,
       price REAL NOT NULL DEFAULT 0,
       product_id INTEGER,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(id)
   )
   ```

3. **User Sessions Table** (optional, for enhanced session management)
   ```sql
   CREATE TABLE user_sessions (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       session_token TEXT UNIQUE NOT NULL,
       expires_at TIMESTAMP NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES users(id)
   )
   ```

### Phase 2: Authentication System
**Files to create**: `auth.py`, `models.py`
**Files to modify**: `app.py`, `requirements.txt`

#### Dependencies to Add:
- `Flask-Login==0.6.3` - Session management
- `Werkzeug==2.3.7` - Password hashing (already included)
- `Flask-SQLAlchemy==3.0.5` - Optional ORM alternative

#### Core Authentication Features:
1. **User Registration**
   - Username validation (unique, alphanumeric)
   - Email validation
   - Password strength requirements
   - Duplicate account prevention

2. **User Login**
   - Username/email login options
   - Password verification
   - Session creation
   - Remember me functionality

3. **Password Security**
   - Hashing with Werkzeug's generate_password_hash
   - Salted hashes
   - Secure password reset flow

4. **Session Management**
   - Flask-Login integration
   - User session persistence
   - Automatic logout on timeout

### Phase 3: Route Updates
**Files to modify**: `app.py`

#### New Routes Required:
1. **Authentication Routes**
   - `/register` - User registration (GET/POST)
   - `/login` - User login (GET/POST)
   - `/logout` - User logout (POST)
   - `/profile` - User profile management
   - `/reset-password` - Password reset flow

2. **Protected Routes** (require login)
   - `/shopping-cart` - Personalized cart
   - `/add-to-cart` - Add items to user's cart
   - `/remove-item/<item_id>` - Remove from user's cart

#### Route Modifications Required:
1. **Home Route (`/`)**
   - Check authentication status
   - Show personalized welcome message
   - Redirect to login if not authenticated (optional)

2. **Cart-Related Routes**
   - Filter cart items by `user_id`
   - Update all cart queries to include user context

3. **Product Routes**
   - Maintain cart state across sessions
   - Show personalized recommendations

### Phase 4: Template Updates
**Files to create**: `register.html`, `login.html`, `profile.html`
**Files to modify**: `index.html`, `shopping_cart.html`, `base.html` (new)

#### Authentication Templates:
1. **Login Page** (`login.html`)
   - Username/email field
   - Password field
   - Remember me checkbox
   - Register link
   - Forgot password link

2. **Registration Page** (`register.html`)
   - Username field
   - Email field
   - Password field
   - Password confirmation
   - Validation messages
   - Login link

3. **Profile Page** (`profile.html`)
   - User information display
   - Password change
   - Account deletion option

#### Existing Template Updates:
1. **Navigation Updates**
   - Add Login/Register links when not authenticated
   - Add Profile/Logout links when authenticated
   - Show username in welcome message

2. **Cart Integration**
   - Show user-specific cart items
   - Maintain cart state across sessions

### Phase 5: Security Enhancements
**Files to modify**: `app.py`, new middleware files

#### Security Measures:
1. **Input Validation**
   - CSRF protection (Flask-WTF)
   - SQL injection prevention (parameterized queries)
   - XSS protection (template escaping)

2. **Session Security**
   - Secure cookie settings
   - Session timeout configuration
   - HTTPS enforcement (production)

3. **Rate Limiting**
   - Login attempt limiting
   - Registration rate limiting
   - API endpoint protection

### Phase 6: User Experience Enhancements
**Files to modify**: All templates, `static/style.css`

#### UX Improvements:
1. **Responsive Auth Forms**
   - Mobile-friendly login/register
   - Inline validation messages
   - Loading states

2. **Cart Persistence**
   - Save cart across sessions
   - Merge guest cart with user cart on login
   - Cart synchronization

3. **Personalization**
   - Welcome message with username
   - Personalized recommendations
   - Order history (future feature)

## Implementation Order

### Priority 1 (Core Functionality)
1. Database schema updates
2. Basic authentication (login/register)
3. Cart user association
4. Template updates for auth

### Priority 2 (Security & UX)
1. Password security implementation
2. Session management
3. Form validation
4. UI/UX improvements

### Priority 3 (Advanced Features)
1. Password reset functionality
2. Profile management
3. Enhanced security measures
4. Personalization features

## Migration Strategy

### Existing Data Handling:
1. **Current Cart Items**: Create a "guest" user or migrate to admin account
2. **Database Migration**: Use Flask-Migrate or custom migration scripts
3. **Backward Compatibility**: Ensure graceful degradation during transition

### Deployment Considerations:
1. **Staging Environment**: Test authentication flow thoroughly
2. **Data Backup**: Backup existing database before schema changes
3. **Rollback Plan**: Prepare migration rollback procedures

## Testing Strategy

### Unit Tests:
- User registration/validation
- Login/logout functionality
- Password hashing/verification
- Database operations

### Integration Tests:
- Full authentication flow
- Cart operations with user context
- Session management
- Security measures

### User Acceptance Tests:
- Registration process
- Login/logout experience
- Cart personalization
- Error handling

## Future Enhancements

### Phase 2 Features:
1. **Social Login** - Google, Facebook OAuth
2. **Two-Factor Authentication** - Enhanced security
3. **Order History** - Purchase tracking
4. **Wishlist** - Save items for later
5. **User Reviews** - Product ratings and reviews

### Analytics & Personalization:
1. **User Behavior Tracking** - Shopping patterns
2. **Recommendation Engine** - AI-powered suggestions
3. **Email Notifications** - Cart abandonment, promotions

## Technical Considerations

### Performance:
1. **Database Indexing** - Add indexes on user_id, username, email
2. **Session Storage** - Consider Redis for scalable sessions
3. **Caching** - Cache user data, cart information

### Scalability:
1. **Database Design** - Prepare for high user volume
2. **Load Balancing** - Session affinity considerations
3. **CDN Integration** - Static asset delivery

## Security Checklist

- [ ] Password hashing implementation
- [ ] CSRF protection enabled
- [ ] SQL injection prevention
- [ ] XSS protection in templates
- [ ] Secure session configuration
- [ ] Rate limiting implementation
- [ ] Input validation on all forms
- [ ] HTTPS enforcement (production)
- [ ] Secure cookie settings
- [ ] Password complexity requirements



This comprehensive plan ensures a secure, user-friendly authentication system that integrates seamlessly with the existing guitar store application while providing a foundation for future enhancements.
