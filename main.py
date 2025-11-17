from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import json as json_lib
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import uuid
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Our Area API")
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserSignup(BaseModel):
    username: str
    password: str
    phone: str = None
    email: str = None
    avatar_url: str = None
    bio: str = None
    location_id: str = None

class UserLogin(BaseModel):
    username: str
    password: str

class LocationCreate(BaseModel):
    country: str = None
    state: str = None
    district: str = None
    city: str = None
    postal_code: str = None
    address_line: str = None
    latitude: float = None
    longitude: float = None

class PostCreate(BaseModel):
    area_id: str = "area1"
    location_id: str = None
    text: str
    category: str
    event_time: str = None
    image_urls: List[str] = []

class CommentCreate(BaseModel):
    text: str

class ReportCreate(BaseModel):
    post_id: str = None
    reported_user_id: str = None
    reason: str
    description: str = None

def execute_sql(query, params=None):
    turso_url = os.getenv("TURSO_DB_URL")
    turso_token = os.getenv("TURSO_DB_TOKEN")
    
    if not turso_url or not turso_token:
        raise Exception("Missing TURSO_DB_URL or TURSO_DB_TOKEN environment variables")
    
    # Convert libsql URL to HTTP API URL
    api_url = turso_url.replace("libsql://", "https://").replace(".turso.io", ".turso.io/v2/pipeline")
    
    headers = {
        "Authorization": f"Bearer {turso_token}",
        "Content-Type": "application/json"
    }
    
    # Format parameters for Turso API
    formatted_params = []
    if params:
        for p in params:
            if p is None:
                formatted_params.append({"type": "null"})
            elif isinstance(p, str):
                formatted_params.append({"type": "text", "value": p})
            elif isinstance(p, int):
                formatted_params.append({"type": "integer", "value": str(p)})
            elif isinstance(p, float):
                formatted_params.append({"type": "float", "value": str(p)})
            else:
                formatted_params.append({"type": "text", "value": str(p)})
    
    payload = {
        "requests": [{
            "type": "execute",
            "stmt": {
                "sql": query,
                "args": formatted_params
            }
        }]
    }
    
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Database request failed: {response.status_code} - {response.text}")
    return response.json()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, os.getenv("SECRET_KEY", "fallback-secret"), algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return {"id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Not authenticated")

@app.get("/")
def root():
    return {"message": "Our Area API", "status": "ok", "docs": "/docs"}

@app.get("/debug")
def debug():
    return {"status": "working", "message": "API is running"}

@app.get("/test-db")
def test_database():
    try:
        turso_url = os.getenv("TURSO_DB_URL")
        turso_token = os.getenv("TURSO_DB_TOKEN")
        
        if not turso_url:
            return {"error": "TURSO_DB_URL not found"}
        if not turso_token:
            return {"error": "TURSO_DB_TOKEN not found"}
            
        # Test simple query
        result = execute_sql("SELECT 1 as test")
        
        return {
            "status": "success",
            "message": "Database connection working",
            "test_result": result
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.get("/env-check")
def check_env():
    return {
        "turso_url_exists": bool(os.getenv("TURSO_DB_URL")),
        "turso_token_exists": bool(os.getenv("TURSO_DB_TOKEN")),
        "secret_key_exists": bool(os.getenv("SECRET_KEY")),
        "turso_url_preview": os.getenv("TURSO_DB_URL", "NOT_SET")[:50] + "..." if os.getenv("TURSO_DB_URL") else "NOT_SET"
    }

@app.post("/simple-signup")
def simple_signup(user_data: UserSignup):
    try:
        user_id = str(uuid.uuid4())
        hashed_password = pwd_context.hash(user_data.password)
        
        return {
            "status": "success", 
            "message": "User data processed",
            "user_id": user_id,
            "username": user_data.username,
            "env_check": {
                "turso_url": bool(os.getenv("TURSO_DB_URL")),
                "turso_token": bool(os.getenv("TURSO_DB_TOKEN"))
            }
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}

@app.post("/signup")
def signup(user_data: UserSignup):
    try:
        # Check environment variables first
        if not os.getenv("TURSO_DB_URL") or not os.getenv("TURSO_DB_TOKEN"):
            raise HTTPException(status_code=500, detail="Database configuration missing")
            
        # Simple password truncation for bcrypt
        password = user_data.password[:50]  # Keep it simple
        hashed_password = pwd_context.hash(password)
        
        # Create users table only if it doesn't exist
        execute_sql("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                phone TEXT,
                email TEXT,
                avatar_url TEXT,
                bio TEXT,
                location_id TEXT,
                password_hash TEXT NOT NULL,
                is_verified INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        result = execute_sql(
            "INSERT INTO users (username, phone, email, avatar_url, bio, location_id, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [user_data.username, user_data.phone, user_data.email, user_data.avatar_url, user_data.bio, user_data.location_id, hashed_password]
        )
        
        # Get the auto-generated user ID from Turso response
        response_data = result.get("results", [{}])[0].get("response", {}).get("result", {})
        user_id = response_data.get("last_insert_rowid")
        
        # If last_insert_rowid is not available, query for the user
        if user_id is None:
            user_result = execute_sql("SELECT id FROM users WHERE username = ?", [user_data.username])
            user_rows = user_result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
            if user_rows:
                user_id_data = user_rows[0][0]
                user_id = user_id_data.get("value") if isinstance(user_id_data, dict) else user_id_data
        return {"status": "success", "message": "User created", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating user: {str(e)}")

@app.post("/login")
def login(credentials: UserLogin):
    result = execute_sql(
        "SELECT * FROM users WHERE username = ?",
        [credentials.username]
    )
    
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    if not rows or not pwd_context.verify(credentials.password, rows[0][7]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {"sub": rows[0][0], "exp": datetime.utcnow() + timedelta(minutes=30)},
        os.getenv("SECRET_KEY", "fallback-secret"),
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer", "user_id": rows[0][0]}

@app.get("/users")
def get_users():
    try:
        result = execute_sql("SELECT * FROM users ORDER BY created_at DESC")
        rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
        
        def extract_value(field):
            if isinstance(field, dict) and 'value' in field:
                return field['value']
            elif isinstance(field, dict) and field.get('type') == 'null':
                return None
            return field
        
        return [{
            "id": extract_value(row[0]),
            "username": extract_value(row[1]),
            "phone": extract_value(row[2]),
            "email": extract_value(row[3]),
            "avatar_url": extract_value(row[4]),
            "bio": extract_value(row[5]),
            "location_id": extract_value(row[6]),
            "is_verified": extract_value(row[8]),
            "created_at": extract_value(row[9])
        } for row in rows]
    except Exception as e:
        return {"error": f"Database error: {str(e)}", "users": []}

@app.get("/users/me")
def get_me():
    result = execute_sql("SELECT * FROM users WHERE id = ?", [1])
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    
    if not rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = rows[0]
    return {
        "id": user[0],
        "username": user[1],
        "phone": user[2],
        "email": user[3],
        "avatar_url": user[4],
        "bio": user[5],
        "location_id": user[6]
    }

@app.get("/locations")
def get_locations():
    try:
        result = execute_sql("SELECT * FROM locations ORDER BY created_at DESC")
        rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
        
        return [{
            "id": row[0],
            "country": row[1],
            "state": row[2],
            "district": row[3],
            "city": row[4],
            "postal_code": row[5],
            "address_line": row[6],
            "latitude": row[8],
            "longitude": row[9],
            "created_at": row[10]
        } for row in rows]
    except Exception as e:
        return {"error": f"Database error: {str(e)}", "locations": []}

@app.post("/locations")
def create_location(location_data: LocationCreate):
    location_id = str(uuid.uuid4())
    
    try:
        # Create locations table if not exists
        execute_sql("""
            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY,
                country TEXT,
                state TEXT,
                district TEXT,
                city TEXT,
                postal_code TEXT,
                address_line TEXT,
                city_id TEXT,
                latitude REAL,
                longitude REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        execute_sql(
            "INSERT INTO locations (id, country, state, district, city, postal_code, address_line, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [location_id, location_data.country, location_data.state, location_data.district, 
             location_data.city, location_data.postal_code, location_data.address_line, 
             location_data.latitude, location_data.longitude]
        )
        
        return {"status": "success", "message": "Location created", "location_id": location_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating location: {str(e)}")

@app.get("/areas")
def get_areas():
    try:
        # Create areas table if not exists
        execute_sql("""
            CREATE TABLE IF NOT EXISTS areas (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                center_lat REAL NOT NULL,
                center_lng REAL NOT NULL,
                radius_m INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert sample area if none exist
        execute_sql("INSERT OR IGNORE INTO areas (id, name, center_lat, center_lng, radius_m) VALUES ('area1', 'Downtown', 12.9716, 77.5946, 5000)")
        
        result = execute_sql("SELECT * FROM areas ORDER BY created_at DESC")
        rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
        
        return [{
            "id": row[0],
            "name": row[1],
            "center_lat": row[2],
            "center_lng": row[3],
            "radius_m": row[4],
            "created_at": row[5] if len(row) > 5 else None
        } for row in rows]
    except Exception as e:
        return {"error": f"Database error: {str(e)}", "areas": []}

@app.get("/posts")
def get_posts(
    area_id: str = Query("area1"),
    page: int = Query(1),
    limit: int = Query(20),
    current_user: dict = Depends(get_current_user)
):
    try:
        offset = (page - 1) * limit
        
        query = "SELECT p.*, u.username FROM posts p LEFT JOIN users u ON p.user_id = u.id WHERE p.area_id = ? AND p.is_deleted = 0 ORDER BY p.created_at DESC LIMIT ? OFFSET ?"
        params = [area_id, limit, offset]
        
        result = execute_sql(query, params)
        rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
        
        posts = []
        for row in rows:
            post_id = row[0]
            
            # Get images for this post
            images_result = execute_sql(
                "SELECT url FROM post_images WHERE post_id = ? ORDER BY order_idx",
                [post_id]
            )
            images_rows = images_result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
            image_urls = [img[0] for img in images_rows]
            
            posts.append({
                "id": row[0],
                "user_id": row[1],
                "area_id": row[2],
                "location_id": row[3],
                "text": row[4],
                "category": row[5],
                "event_time": row[6],
                "created_at": row[7],
                "updated_at": row[8],
                "images": image_urls,
                "user": {"username": row[10] if len(row) > 10 else "unknown"}
            })
        
        return posts
    except Exception as e:
        return {"error": f"Database error: {str(e)}", "posts": []}

@app.post("/posts")
def create_post(post_data: PostCreate):
    post_id = str(uuid.uuid4())
    
    try:
        # Create posts table if not exists
        execute_sql("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                area_id TEXT NOT NULL,
                location_id TEXT,
                text TEXT NOT NULL,
                category TEXT NOT NULL,
                event_time DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_deleted INTEGER DEFAULT 0
            )
        """)
        
        # Create post_images table if not exists
        execute_sql("""
            CREATE TABLE IF NOT EXISTS post_images (
                id TEXT PRIMARY KEY,
                post_id TEXT NOT NULL,
                url TEXT NOT NULL,
                order_idx INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Ensure area exists
        execute_sql("INSERT OR IGNORE INTO areas (id, name, center_lat, center_lng, radius_m) VALUES (?, 'Default Area', 12.9716, 77.5946, 5000)", [post_data.area_id])
        
        # Insert post
        execute_sql(
            "INSERT INTO posts (id, user_id, area_id, location_id, text, category, event_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
            [post_id, current_user["id"], post_data.area_id, post_data.location_id, post_data.text, post_data.category, post_data.event_time]
        )
        
        # Handle image URLs
        if post_data.image_urls:
            # Store images in post_images table
            for idx, image_url in enumerate(post_data.image_urls):
                image_id = str(uuid.uuid4())
                execute_sql(
                    "INSERT INTO post_images (id, post_id, url, order_idx) VALUES (?, ?, ?, ?)",
                    [image_id, post_id, image_url, idx]
                )
            
            # Automatically update user's avatar_url with first image (if user has no avatar)
            user_result = execute_sql("SELECT avatar_url FROM users WHERE id = ?", [current_user["id"]])
            user_rows = user_result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
            
            if user_rows and not user_rows[0][0]:  # User has no avatar
                execute_sql(
                    "UPDATE users SET avatar_url = ? WHERE id = ?",
                    [post_data.image_urls[0], current_user["id"]]
                )
        
        return {"status": "success", "message": "Post created", "post_id": post_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating post: {str(e)}")

@app.get("/posts/{post_id}")
def get_post(post_id: str):
    result = execute_sql(
        "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = ? AND p.is_deleted = 0",
        [post_id]
    )
    
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    if not rows:
        raise HTTPException(status_code=404, detail="Post not found")
    
    row = rows[0]
    
    # Get images for this post
    images_result = execute_sql(
        "SELECT url FROM post_images WHERE post_id = ? ORDER BY order_idx",
        [post_id]
    )
    images_rows = images_result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    image_urls = [img[0] for img in images_rows]
    
    return {
        "id": row[0],
        "user_id": row[1],
        "area_id": row[2],
        "location_id": row[3],
        "text": row[4],
        "category": row[5],
        "event_time": row[6],
        "created_at": row[7],
        "updated_at": row[8],
        "images": image_urls,
        "user": {"username": row[10]}
    }

@app.post("/posts/{post_id}/like")
def toggle_like(post_id: str):
    # Create likes table if not exists
    execute_sql("""
        CREATE TABLE IF NOT EXISTS likes (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if like exists
    result = execute_sql(
        "SELECT id FROM likes WHERE post_id = ? AND user_id = ?",
        [post_id, 1]
    )
    
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    
    if rows:
        # Unlike
        execute_sql("DELETE FROM likes WHERE post_id = ? AND user_id = ?", [post_id, 1])
        return {"status": "success", "action": "unliked"}
    else:
        # Like
        like_id = str(uuid.uuid4())
        execute_sql(
            "INSERT INTO likes (id, post_id, user_id) VALUES (?, ?, ?)",
            [like_id, post_id, 1]
        )
        return {"status": "success", "action": "liked"}

@app.post("/posts/{post_id}/wishlist")
def toggle_wishlist(post_id: str):
    # Create wishlists table if not exists
    execute_sql("""
        CREATE TABLE IF NOT EXISTS wishlists (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if wishlist exists
    result = execute_sql(
        "SELECT id FROM wishlists WHERE post_id = ? AND user_id = ?",
        [post_id, 1]
    )
    
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    
    if rows:
        # Remove from wishlist
        execute_sql("DELETE FROM wishlists WHERE post_id = ? AND user_id = ?", [post_id, 1])
        return {"status": "success", "action": "removed"}
    else:
        # Add to wishlist
        wishlist_id = str(uuid.uuid4())
        execute_sql(
            "INSERT INTO wishlists (id, post_id, user_id) VALUES (?, ?, ?)",
            [wishlist_id, post_id, 1]
        )
        return {"status": "success", "action": "added"}

@app.get("/posts/{post_id}/comments")
def get_comments(post_id: str):
    result = execute_sql(
        "SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id WHERE c.post_id = ? ORDER BY c.created_at ASC",
        [post_id]
    )
    
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    
    return [{
        "id": row[0],
        "post_id": row[1],
        "user_id": row[2],
        "text": row[3],
        "created_at": row[4],
        "user": {"username": row[5]}
    } for row in rows]

@app.post("/posts/{post_id}/comments")
def create_comment(post_id: str, comment_data: CommentCreate):
    # Create comments table if not exists
    execute_sql("""
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    comment_id = str(uuid.uuid4())
    
    execute_sql(
        "INSERT INTO comments (id, post_id, user_id, text) VALUES (?, ?, ?, ?)",
        [comment_id, post_id, 1, comment_data.text]
    )
    
    return {"status": "success", "message": "Comment created", "comment_id": comment_id}

@app.post("/reports")
def create_report(report_data: ReportCreate):
    # Create reports table if not exists
    execute_sql("""
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            reporter_id TEXT NOT NULL,
            post_id TEXT,
            reported_user_id TEXT,
            reason TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    report_id = str(uuid.uuid4())
    
    execute_sql(
        "INSERT INTO reports (id, reporter_id, post_id, reported_user_id, reason, description) VALUES (?, ?, ?, ?, ?, ?)",
        [report_id, 1, report_data.post_id, report_data.reported_user_id, report_data.reason, report_data.description]
    )
    
    return {"status": "success", "message": "Report submitted", "report_id": report_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))