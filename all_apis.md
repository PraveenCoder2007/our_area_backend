# Complete API Endpoints for Postman

Replace `your-project-name` with your actual Vercel project name.
Base URL: `https://your-project-name.vercel.app/api`

## Authentication Required
For protected endpoints, add this header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 1. Health Check
**GET** `/`

## 2. Authentication

### Signup
**POST** `/auth/signup`
```json
{
  "display_name": "John Doe",
  "username": "johndoe2",
  "password": "password123"
}
```

### Login
**POST** `/auth/login`
```json
{
  "username": "johndoe",
  "password": "password123"
}
```

## 3. Users

### Get Current User
**GET** `/users/me`
*Requires: Authorization header*

### Update Profile
**PUT** `/users/me`
*Requires: Authorization header*
```json
{
  "display_name": "John Updated",
  "phone": "+1234567890",
  "email": "john@example.com"
}
```

## 4. Areas

### Get Nearby Areas
**GET** `/areas/near?lat=40.7128&lng=-74.0060`

## 5. Posts

### Get Feed
**GET** `/posts/feed?area_id=area1&page=1&limit=20`
*Requires: Authorization header*

### Create Post
**POST** `/posts`
*Requires: Authorization header*
```json
{
  "area_id": "area1",
  "text": "Great event happening downtown!",
  "category": "event"
}
```

### Get Post Details
**GET** `/posts/{post_id}`
*Requires: Authorization header*

### Like/Unlike Post
**POST** `/posts/{post_id}/like`
*Requires: Authorization header*

### Get Comments
**GET** `/posts/{post_id}/comments`

### Add Comment
**POST** `/posts/{post_id}/comments`
*Requires: Authorization header*
```json
{
  "text": "Great post!"
}
```

## 6. Reports

### Report Post/User
**POST** `/reports`
*Requires: Authorization header*
```json
{
  "post_id": "post_id_here",
  "reason": "spam",
  "description": "This is spam content"
}
```

## Test Flow:
1. Health check
2. Login to get token
3. Get areas
4. Create a post
5. Like the post
6. Add a comment
7. Get feed to see your post