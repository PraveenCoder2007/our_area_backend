# Our Area API - Complete Documentation

## 🚀 Live API
- **Base URL**: https://our-area-backend.onrender.com
- **Interactive Docs**: https://our-area-backend.onrender.com/docs
- **GitHub**: https://github.com/PraveenCoder2007/our_area_backend

## 📊 Database Schema

### Tables Overview
| Table | Purpose | Key Features |
|-------|---------|--------------|
| `users` | User accounts and profiles | Authentication, location tracking |
| `areas` | Geographic community areas | Radius-based location zones |
| `locations` | Detailed address information | GPS coordinates, postal data |
| `posts` | Community posts and events | Categories, location-based |
| `post_images` | Image attachments for posts | Multiple images per post |
| `likes` | Post likes/reactions | User engagement tracking |
| `wishlists` | Saved posts | User bookmarking |
| `comments` | Post comments | Community discussions |
| `reports` | Content moderation | Report posts/users |
| `joins` | Event participation | User event attendance |

### Database Relationships
```
users ←→ areas (many-to-one)
users ←→ locations (many-to-one)
posts ←→ users (many-to-one)
posts ←→ areas (many-to-one)
posts ←→ post_images (one-to-many)
posts ←→ likes (one-to-many)
posts ←→ comments (one-to-many)
```

## 🔧 Environment Setup

### Required Environment Variables
```env
TURSO_DB_URL=libsql://your-database-name.turso.io
TURSO_DB_TOKEN=your-turso-auth-token
SECRET_KEY=your-production-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Local Development
```bash
# 1. Clone repository
git clone https://github.com/PraveenCoder2007/our_area_backend.git
cd our_area_backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Edit .env with your Turso credentials

# 4. Run application
python main.py
```

## 📋 API Endpoints Reference

### 🔐 Authentication Endpoints

#### POST /signup
Create a new user account.

**Request Body:**
```json
{
  "display_name": "John Doe",
  "username": "johndoe",
  "password": "password123"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "User created"
}
```

#### POST /login
Authenticate user and get JWT token.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 👥 User Endpoints

#### GET /users
Get all users (public endpoint).

**Response:**
```json
[
  {
    "id": "user1",
    "display_name": "John Doe",
    "username": "johndoe",
    "phone": null,
    "email": null,
    "avatar_url": null,
    "bio": null,
    "location_id": "loc1",
    "area_id": "area1",
    "is_verified": 0,
    "created_at": "2025-11-09 06:14:13"
  }
]
```

#### GET /users/me
Get current authenticated user profile.

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Response:**
```json
{
  "id": "user1",
  "display_name": "John Doe",
  "username": "johndoe",
  "phone": null,
  "email": null
}
```

### 🌍 Area Endpoints

#### GET /areas
Get all community areas.

**Response:**
```json
[
  {
    "id": "area1",
    "name": "Downtown",
    "center_lat": 12.9716,
    "center_lng": 77.5946,
    "radius_m": 5000
  }
]
```

### 📝 Post Endpoints

#### GET /posts
Get posts feed for an area (requires authentication).

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Query Parameters:**
- `area_id` (string): Area ID to get posts from (default: "area1")
- `page` (integer): Page number (default: 1)
- `limit` (integer): Posts per page (default: 20)

**Example Request:**
```
GET /posts?area_id=area1&page=1&limit=10
```

**Response:**
```json
[
  {
    "id": "post1",
    "user_id": "user1",
    "area_id": "area1",
    "text": "New coffee shop opening tomorrow!",
    "category": "business",
    "created_at": "2025-11-09 10:30:00",
    "user": {
      "display_name": "John Doe",
      "username": "johndoe"
    }
  }
]
```

#### POST /posts
Create a new post (requires authentication).

**Headers:**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

**Request Body:**
```json
{
  "area_id": "area1",
  "text": "Community cleanup event this Saturday at 9 AM!",
  "category": "event"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Post created",
  "data": {
    "post_id": "generated-uuid"
  }
}
```

### 🔧 Utility Endpoints

#### GET /
API health check.

**Response:**
```json
{
  "message": "Our Area API",
  "status": "ok",
  "docs": "/docs"
}
```

#### GET /debug
API status check.

**Response:**
```json
{
  "status": "working",
  "message": "API is running"
}
```

#### GET /test-db
Test database connection.

**Response:**
```json
{
  "status": "success",
  "message": "Database connection working",
  "test_result": { ... }
}
```

## 📖 Step-by-Step Usage Guide

### 1. User Registration & Authentication

**Step 1: Create Account**
```bash
curl -X POST "https://our-area-backend.onrender.com/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Jane Smith",
    "username": "janesmith",
    "password": "securepassword123"
  }'
```

**Step 2: Login**
```bash
curl -X POST "https://our-area-backend.onrender.com/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "janesmith",
    "password": "securepassword123"
  }'
```

**Step 3: Save Token**
Copy the `access_token` from login response for authenticated requests.

### 2. Exploring Data

**Get All Users:**
```bash
curl "https://our-area-backend.onrender.com/users"
```

**Get Areas:**
```bash
curl "https://our-area-backend.onrender.com/areas"
```

**Get Your Profile:**
```bash
curl "https://our-area-backend.onrender.com/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Working with Posts

**Create a Post:**
```bash
curl -X POST "https://our-area-backend.onrender.com/posts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "area_id": "area1",
    "text": "Looking for tennis partners this weekend!",
    "category": "sports"
  }'
```

**Get Posts Feed:**
```bash
curl "https://our-area-backend.onrender.com/posts?area_id=area1&page=1&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Using Interactive Documentation

1. **Visit**: https://our-area-backend.onrender.com/docs
2. **Login**: Use `/login` endpoint with test credentials
3. **Authorize**: Click "Authorize" button, enter `Bearer YOUR_TOKEN`
4. **Test**: Try any endpoint with the interactive interface

## 🗃️ Database Table Details

### users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,              -- Unique user identifier
    display_name TEXT NOT NULL,       -- User's display name
    username TEXT UNIQUE NOT NULL,    -- Unique username
    phone TEXT,                       -- Phone number (optional)
    email TEXT,                       -- Email address (optional)
    avatar_url TEXT,                  -- Profile picture URL
    bio TEXT,                         -- User biography
    location_id TEXT,                 -- Reference to locations table
    area_id TEXT,                     -- Reference to areas table
    password_hash TEXT NOT NULL,      -- Hashed password
    is_verified INTEGER DEFAULT 0,    -- Verification status
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### posts Table
```sql
CREATE TABLE posts (
    id TEXT PRIMARY KEY,              -- Unique post identifier
    user_id TEXT NOT NULL,            -- Post author
    area_id TEXT NOT NULL,            -- Area where post is visible
    location_id TEXT,                 -- Specific location reference
    text TEXT NOT NULL,               -- Post content
    category TEXT NOT NULL,           -- Post category (event, business, etc.)
    lat REAL,                         -- GPS latitude
    lng REAL,                         -- GPS longitude
    event_time DATETIME,              -- Event date/time (for events)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_deleted INTEGER DEFAULT 0      -- Soft delete flag
);
```

### areas Table
```sql
CREATE TABLE areas (
    id TEXT PRIMARY KEY,              -- Unique area identifier
    name TEXT NOT NULL,               -- Area name (e.g., "Downtown")
    center_lat REAL NOT NULL,         -- Center latitude
    center_lng REAL NOT NULL,         -- Center longitude
    radius_m INTEGER NOT NULL,        -- Radius in meters
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔒 Authentication Flow

1. **Register**: `POST /signup` with user details
2. **Login**: `POST /login` with username/password
3. **Get Token**: Save `access_token` from login response
4. **Use Token**: Include `Authorization: Bearer TOKEN` header
5. **Access Protected**: Use token for `/users/me`, `/posts` endpoints

## 📱 Post Categories

Supported post categories:
- `event` - Community events, meetups
- `business` - Business openings, promotions
- `sports` - Sports activities, games
- `social` - Social gatherings, parties
- `help` - Help requests, assistance
- `announcement` - General announcements
- `lost_found` - Lost and found items

## 🚨 Error Handling

### Common HTTP Status Codes
- `200` - Success
- `400` - Bad Request (invalid data)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found
- `422` - Validation Error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

## 🔧 Development & Deployment

### Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: Turso (SQLite-compatible)
- **Authentication**: JWT tokens
- **Hosting**: Render
- **API**: RESTful with OpenAPI docs

### Performance Features
- Async database operations
- Connection pooling via Turso HTTP API
- Indexed queries for fast lookups
- Pagination for large datasets
- CORS enabled for frontend integration

## 📞 Support & Resources

- **API Docs**: https://our-area-backend.onrender.com/docs
- **GitHub**: https://github.com/PraveenCoder2007/our_area_backend
- **Turso Docs**: https://docs.turso.tech/
- **FastAPI Docs**: https://fastapi.tiangolo.com/