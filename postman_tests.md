# Postman API Tests

Replace `your-project-name` with your actual Vercel project name.

## 1. Health Check
**GET** `https://your-project-name.vercel.app/api/`

## 2. Login
**POST** `https://your-project-name.vercel.app/api/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "username": "johndoe",
  "password": "password123"
}
```

## 3. Get Areas
**GET** `https://your-project-name.vercel.app/api/areas/near?lat=40.7128&lng=-74.0060`

## Test Flow:
1. Test health check first
2. Login to get access token
3. Copy the access_token from login response
4. Test areas endpoint

## Expected Responses:

**Health Check:**
```json
{
  "message": "Our Area API is running on Vercel",
  "status": "ok"
}
```

**Login Success:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Areas:**
```json
[
  {
    "id": "area1",
    "name": "Downtown"
  },
  {
    "id": "area2", 
    "name": "Brooklyn Heights"
  }
]
```