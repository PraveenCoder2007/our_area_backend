from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import libsql_client
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import uuid
from typing import Optional

# Environment variables
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

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

def get_db():
    return libsql_client.create_client(
        url=TURSO_DATABASE_URL,
        auth_token=TURSO_AUTH_TOKEN
    )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Health
@app.get("/")
def root():
    return {"message": "Our Area API is running on Vercel", "status": "ok"}

# Auth
@app.post("/auth/signup")
def signup(user_data: dict):
    db = get_db()
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash(user_data["password"])
    
    try:
        db.execute(
            "INSERT INTO users (id, display_name, username, password_hash) VALUES (?, ?, ?, ?)",
            [user_id, user_data["display_name"], user_data["username"], hashed_password]
        )
        return {"status": "success", "message": "User created"}
    except:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/auth/login")
def login(credentials: dict):
    db = get_db()
    
    result = db.execute(
        "SELECT * FROM users WHERE username = ?",
        [credentials["username"]]
    )
    
    if not result.rows or not pwd_context.verify(credentials["password"], result.rows[0][7]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {"sub": result.rows[0][0], "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer"}

# Users
@app.get("/users/me")
def get_me(current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = db.execute("SELECT * FROM users WHERE id = ?", [current_user["id"]])
    if not result.rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = result.rows[0]
    return {
        "id": user[0],
        "display_name": user[1],
        "username": user[2],
        "phone": user[3],
        "email": user[4]
    }

@app.put("/users/me")
def update_me(user_update: dict, current_user: dict = Depends(get_current_user)):
    db = get_db()
    
    fields = []
    values = []
    for key, value in user_update.items():
        if key in ["display_name", "phone", "email", "bio"]:
            fields.append(f"{key} = ?")
            values.append(value)
    
    if fields:
        values.append(current_user["id"])
        db.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", values)
    
    return {"status": "success", "message": "Profile updated"}

# Areas
@app.get("/areas/near")
def get_areas(lat: float = Query(...), lng: float = Query(...)):
    db = get_db()
    result = db.execute("SELECT * FROM areas")
    return [{
        "id": row[0],
        "name": row[1],
        "center_lat": row[2],
        "center_lng": row[3],
        "radius_m": row[4]
    } for row in result.rows]

# Posts
@app.get("/posts/feed")
def get_feed(
    area_id: str = Query(...),
    page: int = Query(1),
    limit: int = Query(20),
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    offset = (page - 1) * limit
    
    result = db.execute(
        "SELECT p.*, u.display_name, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.area_id = ? AND p.is_deleted = 0 ORDER BY p.created_at DESC LIMIT ? OFFSET ?",
        [area_id, limit, offset]
    )
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "area_id": row[2],
        "text": row[4],
        "category": row[5],
        "created_at": row[8],
        "user": {"display_name": row[11], "username": row[12]}
    } for row in result.rows]

@app.post("/posts")
def create_post(post_data: dict, current_user: dict = Depends(get_current_user)):
    db = get_db()
    post_id = str(uuid.uuid4())
    
    db.execute(
        "INSERT INTO posts (id, user_id, area_id, text, category) VALUES (?, ?, ?, ?, ?)",
        [post_id, current_user["id"], post_data["area_id"], post_data["text"], post_data["category"]]
    )
    
    return {"status": "success", "message": "Post created", "data": {"post_id": post_id}}

@app.get("/posts/{post_id}")
def get_post(post_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = db.execute(
        "SELECT p.*, u.display_name, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = ? AND p.is_deleted = 0",
        [post_id]
    )
    
    if not result.rows:
        raise HTTPException(status_code=404, detail="Post not found")
    
    row = result.rows[0]
    return {
        "id": row[0],
        "user_id": row[1],
        "area_id": row[2],
        "text": row[4],
        "category": row[5],
        "created_at": row[8],
        "user": {"display_name": row[11], "username": row[12]}
    }

@app.post("/posts/{post_id}/like")
def toggle_like(post_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    
    # Check if already liked
    result = db.execute(
        "SELECT id FROM likes WHERE post_id = ? AND user_id = ?",
        [post_id, current_user["id"]]
    )
    
    if result.rows:
        db.execute(
            "DELETE FROM likes WHERE post_id = ? AND user_id = ?",
            [post_id, current_user["id"]]
        )
        return {"status": "success", "message": "Like removed"}
    else:
        db.execute(
            "INSERT INTO likes (id, post_id, user_id) VALUES (?, ?, ?)",
            [str(uuid.uuid4()), post_id, current_user["id"]]
        )
        return {"status": "success", "message": "Post liked"}

@app.get("/posts/{post_id}/comments")
def get_comments(post_id: str):
    db = get_db()
    result = db.execute(
        "SELECT c.*, u.display_name, u.username FROM comments c JOIN users u ON c.user_id = u.id WHERE c.post_id = ? ORDER BY c.created_at ASC",
        [post_id]
    )
    
    return [{
        "id": row[0],
        "post_id": row[1],
        "user_id": row[2],
        "text": row[3],
        "created_at": row[4],
        "user": {"display_name": row[5], "username": row[6]}
    } for row in result.rows]

@app.post("/posts/{post_id}/comments")
def add_comment(post_id: str, comment_data: dict, current_user: dict = Depends(get_current_user)):
    db = get_db()
    comment_id = str(uuid.uuid4())
    
    db.execute(
        "INSERT INTO comments (id, post_id, user_id, text) VALUES (?, ?, ?, ?)",
        [comment_id, post_id, current_user["id"], comment_data["text"]]
    )
    
    return {"status": "success", "message": "Comment added", "data": {"comment_id": comment_id}}

# Reports
@app.post("/reports")
def create_report(report_data: dict, current_user: dict = Depends(get_current_user)):
    db = get_db()
    report_id = str(uuid.uuid4())
    
    db.execute(
        "INSERT INTO reports (id, reporter_id, post_id, user_id, reason, description) VALUES (?, ?, ?, ?, ?, ?)",
        [report_id, current_user["id"], report_data.get("post_id"), report_data.get("user_id"), report_data["reason"], report_data.get("description")]
    )
    
    return {"status": "success", "message": "Report submitted", "data": {"report_id": report_id}}