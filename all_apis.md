# Complete API Endpoints for Our Area Backend

Base URL: `https://our-area-backend.onrender.com`

## Authentication Required
For protected endpoints, add this header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 1. Health Check & Utility

### GET /
API health check
```bash
curl https://our-area-backend.onrender.com/
```

### GET /debug
API status check
```bash
curl https://our-area-backend.onrender.com/debug
```

### GET /test-db
Test database connection
```bash
curl https://our-area-backend.onrender.com/test-db
```

### GET /env-check
Check environment variables
```bash
curl https://our-area-backend.onrender.com/env-check
```

## 2. Authentication

### POST /signup
Create new user account
```bash
curl -X POST "https://our-area-backend.onrender.com/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "password123",
    "phone": "+1234567890",
    "email": "john@example.com",
    "avatar_url": "https://example.com/avatar.jpg",
    "bio": "Community member",
    "location_id": "loc1"
  }'
```

### POST /login
Login and get JWT token
```bash
curl -X POST "https://our-area-backend.onrender.com/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "password123"
  }'
```

## 3. Users

### GET /users
Get all users (public)
```bash
curl https://our-area-backend.onrender.com/users
```

### GET /users/me
Get current user profile (requires auth)
```bash
curl "https://our-area-backend.onrender.com/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### PUT /users/me
Update current user profile (requires auth)
```bash
curl -X PUT "https://our-area-backend.onrender.com/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1987654321",
    "email": "newemail@example.com",
    "avatar_url": "https://example.com/newavatar.jpg",
    "bio": "Updated bio",
    "location_id": "new_location_id"
  }'
```

## 4. Locations

### GET /locations
Get all locations
```bash
curl https://our-area-backend.onrender.com/locations
```

### POST /locations
Create new location (requires auth)
```bash
curl -X POST "https://our-area-backend.onrender.com/locations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "India",
    "state": "Karnataka",
    "district": "Bangalore Urban",
    "city": "Bangalore",
    "postal_code": "560001",
    "address_line": "MG Road",
    "latitude": 12.9716,
    "longitude": 77.5946
  }'
```

## 5. Posts

### GET /posts
Get posts feed (requires auth)
```bash
curl "https://our-area-backend.onrender.com/posts?location_id=loc1&page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /posts
Create new post (requires auth)
```bash
curl -X POST "https://our-area-backend.onrender.com/posts" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location_id": "loc1",
    "text": "Great event happening downtown!",
    "category": "event",
    "event_time": "2025-01-15 18:00:00",
    "image_urls": ["https://example.com/image.jpg"]
  }'
```

### GET /posts/{post_id}
Get specific post details
```bash
curl "https://our-area-backend.onrender.com/posts/POST_ID"
```

### POST /posts/{post_id}/like
Toggle like on post (requires auth)
```bash
curl -X POST "https://our-area-backend.onrender.com/posts/POST_ID/like" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### POST /posts/{post_id}/wishlist
Toggle wishlist on post (requires auth)
```bash
curl -X POST "https://our-area-backend.onrender.com/posts/POST_ID/wishlist" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### GET /posts/{post_id}/comments
Get post comments
```bash
curl "https://our-area-backend.onrender.com/posts/POST_ID/comments"
```

### POST /posts/{post_id}/comments
Add comment to post (requires auth)
```bash
curl -X POST "https://our-area-backend.onrender.com/posts/POST_ID/comments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Great post!"
  }'
```

## 6. Reports

### POST /reports
Report post or user (requires auth)
```bash
curl -X POST "https://our-area-backend.onrender.com/reports" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "post_id": "post_id_here",
    "reported_user_id": null,
    "reason": "spam",
    "description": "This is spam content"
  }'
```

## Test Flow

1. **Health check**: `GET /`
2. **Login**: `POST /login` with `johndoe` / `password123`
3. **Get profile**: `GET /users/me` with token
4. **Update profile**: `PUT /users/me` with new data
5. **Create location**: `POST /locations` with address data
6. **Create post**: `POST /posts` with content
7. **Get feed**: `GET /posts` to see posts
8. **Like post**: `POST /posts/{id}/like`
9. **Add comment**: `POST /posts/{id}/comments`

## Post Categories

- `event` - Community events
- `business` - Business announcements
- `sports` - Sports activities
- `social` - Social gatherings
- `help` - Help requests
- `announcement` - General announcements
- `lost_found` - Lost and found
- `marketplace` - Buy/sell items

## Response Format

**Success:**
```json
{
  "status": "success",
  "message": "Operation completed",
  "data": { ... }
}
```

**Error:**
```json
{
  "error": "Error description",
  "type": "ErrorType"
}
```