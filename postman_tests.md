# Postman Testing Guide for Our Area API

## Setup

1. **Import Collection**: Import the `postman_collection.json` file
2. **Set Base URL**: `https://our-area-backend.onrender.com`
3. **Environment Variables**:
   - `base_url`: `https://our-area-backend.onrender.com`
   - `access_token`: (will be set automatically after login)

## Test Sequence

### 1. Health Checks
- **GET** `/` - API health check
- **GET** `/debug` - API status
- **GET** `/test-db` - Database connection test
- **GET** `/env-check` - Environment variables check

### 2. Authentication Flow
- **POST** `/login` - Login with existing user
  ```json
  {
    "username": "johndoe",
    "password": "password123"
  }
  ```
- **POST** `/signup` - Create new user (optional)
  ```json
  {
    "username": "testuser",
    "password": "testpass123",
    "phone": "+1234567890",
    "email": "test@example.com"
  }
  ```

### 3. User Management
- **GET** `/users` - Get all users (public)
- **GET** `/users/me` - Get current user profile
- **PUT** `/users/me` - Update profile
  ```json
  {
    "phone": "+1987654321",
    "email": "updated@example.com",
    "bio": "Updated bio text"
  }
  ```

### 4. Location Management
- **GET** `/locations` - Get all locations
- **POST** `/locations` - Create new location
  ```json
  {
    "country": "India",
    "state": "Karnataka",
    "city": "Bangalore",
    "address_line": "Test Location",
    "latitude": 12.9716,
    "longitude": 77.5946
  }
  ```

### 5. Post Management
- **GET** `/posts` - Get posts feed
  - Query params: `location_id`, `page`, `limit`
- **POST** `/posts` - Create new post
  ```json
  {
    "location_id": "loc1",
    "text": "Test post from Postman",
    "category": "announcement",
    "image_urls": ["https://example.com/image.jpg"]
  }
  ```
- **GET** `/posts/{post_id}` - Get specific post

### 6. Social Features
- **POST** `/posts/{post_id}/like` - Toggle like
- **POST** `/posts/{post_id}/wishlist` - Toggle wishlist
- **GET** `/posts/{post_id}/comments` - Get comments
- **POST** `/posts/{post_id}/comments` - Add comment
  ```json
  {
    "text": "Great post!"
  }
  ```

### 7. Moderation
- **POST** `/reports` - Report content
  ```json
  {
    "post_id": "post_id_here",
    "reason": "spam",
    "description": "This is spam content"
  }
  ```

## Pre-request Scripts

### Auto-set Token
Add this to requests that need authentication:
```javascript
pm.request.headers.add({
    key: 'Authorization',
    value: 'Bearer ' + pm.environment.get('access_token')
});
```

### Login Script
Add this to the login request's Tests tab:
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set('access_token', response.access_token);
    pm.test('Token saved', function () {
        pm.expect(pm.environment.get('access_token')).to.not.be.undefined;
    });
}
```

## Test Scripts

### Basic Response Test
```javascript
pm.test('Status code is 200', function () {
    pm.response.to.have.status(200);
});

pm.test('Response time is less than 2000ms', function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});
```

### JSON Response Test
```javascript
pm.test('Response is JSON', function () {
    pm.response.to.be.json;
});

pm.test('Has required fields', function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('status');
});
```

### Authentication Test
```javascript
pm.test('Authentication successful', function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('access_token');
    pm.expect(response.token_type).to.equal('bearer');
});
```

## Environment Setup

Create a Postman environment with these variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `https://our-area-backend.onrender.com` | |
| `access_token` | | (auto-set by login) |
| `user_id` | | (auto-set by login) |
| `test_post_id` | | (auto-set by create post) |

## Collection Structure

```
Our Area API
├── Health Checks
│   ├── GET Health Check
│   ├── GET Debug
│   ├── GET Test DB
│   └── GET Env Check
├── Authentication
│   ├── POST Login
│   └── POST Signup
├── Users
│   ├── GET All Users
│   ├── GET My Profile
│   └── PUT Update Profile
├── Locations
│   ├── GET All Locations
│   └── POST Create Location
├── Posts
│   ├── GET Posts Feed
│   ├── POST Create Post
│   ├── GET Post Details
│   ├── POST Like Post
│   ├── POST Wishlist Post
│   ├── GET Post Comments
│   └── POST Add Comment
└── Reports
    └── POST Report Content
```

## Expected Responses

### Successful Login
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1
}
```

### User Profile
```json
{
  "id": 1,
  "username": "johndoe",
  "phone": "+1234567890",
  "email": "john@example.com",
  "avatar_url": "https://example.com/avatar.jpg",
  "bio": "Community member",
  "location_id": "loc1"
}
```

### Posts Feed
```json
[
  {
    "id": "post1",
    "user_id": "user1",
    "location_id": "loc1",
    "text": "Community event this weekend!",
    "category": "event",
    "created_at": "2025-01-09T10:30:00",
    "images": ["https://example.com/image.jpg"],
    "user": {"username": "johndoe"}
  }
]
```

## Troubleshooting

### Common Issues
1. **401 Unauthorized**: Check if token is set and valid
2. **404 Not Found**: Verify endpoint URL and method
3. **422 Validation Error**: Check request body format
4. **500 Server Error**: Check server logs or try again

### Debug Steps
1. Check environment variables are set
2. Verify token in Authorization header
3. Validate JSON request body
4. Check API documentation for required fields
5. Test with curl commands first

## Performance Testing

Add these tests for performance monitoring:
```javascript
pm.test('Response time under 1000ms', function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});

pm.test('No server errors', function () {
    pm.response.to.not.have.status(500);
});
```