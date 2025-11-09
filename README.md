# Our Area - Local Community Social App Backend

A FastAPI backend for a local community social app where people can share neighborhood events, business openings, activities, and more.

## Features

- **Authentication**: JWT-based signup/login
- **User Management**: Profile management with location support
- **Areas**: Geographic area management with proximity search
- **Posts**: Create, view, like, and comment on community posts
- **Feed**: Area-based post feed with pagination
- **Reports**: Report inappropriate posts or users
- **Real-time**: Async database operations with SQLite/Turso

## Tech Stack

- FastAPI (Python 3.11+)
- SQLite/Turso database
- JWT authentication
- Async database layer (databases + aiosqlite)
- Pydantic for data validation

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python run.py
   ```
   This will:
   - Create a `.env` file with default settings
   - Initialize the database with schema
   - Start the server on http://localhost:8000

3. **Seed sample data** (optional):
   ```bash
   python seed_data.py
   ```
   Creates sample areas and a test user (username: `johndoe`, password: `password123`)

4. **Access API docs**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Login and get JWT token

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `POST /users/me/location` - Create/update user location

### Areas
- `GET /areas/near?lat=&lng=` - Find nearby areas

### Posts
- `GET /posts/feed?area_id=&page=&limit=` - Get area feed
- `POST /posts` - Create new post
- `GET /posts/{id}` - Get post details
- `POST /posts/{id}/like` - Toggle like on post
- `POST /posts/{id}/wishlist` - Toggle wishlist on post
- `GET /posts/{id}/comments` - Get post comments
- `POST /posts/{id}/comments` - Add comment to post

### Reports
- `POST /reports` - Report post or user

## Configuration

Environment variables (`.env` file):

```env
DATABASE_URL=sqlite:///./our_area.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Database Schema

The app uses SQLite with the following main tables:
- `users` - User accounts and profiles
- `locations` - Geographic locations
- `areas` - Community areas with radius
- `posts` - User posts with categories
- `post_images` - Post image attachments
- `likes`, `wishlists`, `comments` - Social interactions
- `reports` - Content moderation

## Development

The API includes:
- Automatic OpenAPI documentation
- CORS support for frontend integration
- JWT authentication with password hashing
- Input validation with Pydantic
- Async database operations
- Consistent JSON response format

## Production Deployment

For production:
1. Change `SECRET_KEY` to a secure random string
2. Update `DATABASE_URL` to your Turso database
3. Configure proper CORS origins
4. Use a production ASGI server like Gunicorn