# Render + Turso Deployment Guide

## Prerequisites
1. Turso database created and configured
2. Render account set up

## Steps

### 1. Get Turso Credentials
```bash
# Install Turso CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Login to Turso
turso auth login

# Get your database URL
turso db show your-database-name

# Create auth token
turso db tokens create your-database-name
```

### 2. Deploy to Render
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Use the render.yaml configuration
4. Set environment variables in Render dashboard:
   - `TURSO_DB_URL`: libsql://your-database-name.turso.io
   - `TURSO_DB_TOKEN`: your-auth-token-from-step-1
   - `SECRET_KEY`: generate-a-secure-32-character-string

### 3. Test Deployment
- Visit your Render URL + `/debug` to test API
- Visit your Render URL + `/test-db` to test database connection
- Visit your Render URL + `/docs` for API documentation

## API Endpoints Available
- `GET /` - Health check
- `GET /debug` - API status
- `GET /test-db` - Database connection test
- `POST /signup` - User registration
- `POST /login` - User authentication
- `GET /users` - List all users
- `GET /users/me` - Current user profile
- `GET /areas` - List areas
- `GET /posts` - Get posts feed
- `POST /posts` - Create new post

## Environment Variables Required
```
TURSO_DB_URL=libsql://your-database-name.turso.io
TURSO_DB_TOKEN=your-turso-auth-token
SECRET_KEY=your-production-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```