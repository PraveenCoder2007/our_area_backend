# Our Area API - Quick Start Guide

## 🚀 Test the API in 2 Minutes

### Live API Base URL
```
https://our-area-backend.onrender.com
```

### 1. Test Basic Endpoints (No Auth Required)

```bash
# Health check
curl https://our-area-backend.onrender.com/

# Get all users
curl https://our-area-backend.onrender.com/users

# Get areas
curl https://our-area-backend.onrender.com/areas

# Test database connection
curl https://our-area-backend.onrender.com/test-db
```

### 2. Test Authentication Flow

**Login with existing user:**
```bash
curl -X POST "https://our-area-backend.onrender.com/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "password123"
  }'
```

**Copy the access_token from response, then:**
```bash
# Get your profile
curl "https://our-area-backend.onrender.com/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get posts feed
curl "https://our-area-backend.onrender.com/posts?area_id=area1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Create New Content

**Create a new user:**
```bash
curl -X POST "https://our-area-backend.onrender.com/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Test User",
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Create a new post (after login):**
```bash
curl -X POST "https://our-area-backend.onrender.com/posts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "area_id": "area1",
    "text": "Testing the API!",
    "category": "announcement"
  }'
```

## 🌐 Interactive Testing

**Easiest way to test:**
1. Visit: https://our-area-backend.onrender.com/docs
2. Click on `/login` → Try it out
3. Use: `johndoe` / `password123`
4. Copy the token from response
5. Click "Authorize" button at top
6. Enter: `Bearer YOUR_TOKEN`
7. Test any endpoint!

## 📊 Sample Data Available

**Test User:**
- Username: `johndoe`
- Password: `password123`
- Display Name: `John Doe`

**Test Area:**
- ID: `area1`
- Name: `Downtown`

## 🔧 Common Use Cases

### Frontend Integration
```javascript
// Login
const loginResponse = await fetch('https://our-area-backend.onrender.com/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'johndoe', password: 'password123' })
});
const { access_token } = await loginResponse.json();

// Get posts
const postsResponse = await fetch('https://our-area-backend.onrender.com/posts?area_id=area1', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const posts = await postsResponse.json();
```

### Mobile App Integration
```dart
// Flutter/Dart example
final response = await http.post(
  Uri.parse('https://our-area-backend.onrender.com/login'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'username': 'johndoe', 'password': 'password123'}),
);
final token = jsonDecode(response.body)['access_token'];
```

## 🚨 Quick Troubleshooting

**401 Unauthorized?**
- Check if token is included: `Authorization: Bearer TOKEN`
- Verify token is not expired (30 min default)
- Re-login to get fresh token

**Empty responses?**
- Check if database has data
- Verify area_id exists (use `area1` for testing)
- Check API endpoint spelling

**CORS issues?**
- API has CORS enabled for all origins
- Ensure proper Content-Type headers

## 📱 Next Steps

1. **Read full docs**: `API_DOCUMENTATION.md`
2. **Deploy your own**: `RENDER_DEPLOY.md`
3. **Customize**: Fork the GitHub repo
4. **Integrate**: Use in your frontend/mobile app