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
from dotenv import load_dotenv

load_dotenv()

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
    display_name: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PostCreate(BaseModel):
    area_id: str
    text: str
    category: str

def execute_sql(query, params=None):
    turso_url = os.getenv("TURSO_DB_URL")
    turso_token = os.getenv("TURSO_DB_TOKEN")
    
    # Convert libsql URL to HTTP API URL
    api_url = turso_url.replace("libsql://", "https://").replace(".turso.io", ".turso.io/v2/pipeline")
    
    headers = {
        "Authorization": f"Bearer {turso_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "requests": [{
            "type": "execute",
            "stmt": {
                "sql": query,
                "args": params or []
            }
        }]
    }
    
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, os.getenv("SECRET_KEY", "fallback-secret"), algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

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

@app.post("/signup")
def signup(user_data: UserSignup):
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash(user_data.password)
    
    try:
        execute_sql(
            "INSERT INTO users (id, display_name, username, password_hash) VALUES (?, ?, ?, ?)",
            [user_id, user_data.display_name, user_data.username, hashed_password]
        )
        return {"status": "success", "message": "User created"}
    except:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/login")
def login(credentials: UserLogin):
    result = execute_sql(
        "SELECT * FROM users WHERE username = ?",
        [credentials.username]
    )
    
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_row = rows[0]
    user_id = user_row[0].get("value") if isinstance(user_row[0], dict) else user_row[0]
    password_hash = user_row[9].get("value") if isinstance(user_row[9], dict) else user_row[9]
    
    if not pwd_context.verify(credentials.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {"sub": user_id, "exp": datetime.utcnow() + timedelta(minutes=30)},
        os.getenv("SECRET_KEY", "fallback-secret"),
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/areas")
def get_areas():
    result = execute_sql("SELECT * FROM areas")
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    
    return [{
        "id": row[0],
        "name": row[1],
        "center_lat": row[2],
        "center_lng": row[3],
        "radius_m": row[4]
    } for row in rows]

@app.get("/users")
def get_users():
    result = execute_sql("SELECT * FROM users")
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    
    def get_value(item):
        return item.get("value") if isinstance(item, dict) and item.get("type") != "null" else None
    
    return [{
        "id": get_value(row[0]),
        "display_name": get_value(row[1]), 
        "username": get_value(row[2]),
        "phone": get_value(row[3]),
        "email": get_value(row[4]),
        "avatar_url": get_value(row[5]),
        "bio": get_value(row[6]),
        "location_id": get_value(row[7]),
        "area_id": get_value(row[8]),
        "is_verified": int(get_value(row[10])) if get_value(row[10]) else 0,
        "created_at": get_value(row[11])
    } for row in rows]

@app.get("/users/me")
def get_me(current_user: dict = Depends(get_current_user)):
    result = execute_sql("SELECT * FROM users WHERE id = ?", [current_user["id"]])
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    
    if not rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    def get_value(item):
        return item.get("value") if isinstance(item, dict) and item.get("type") != "null" else None
    
    user = rows[0]
    return {
        "id": get_value(user[0]),
        "display_name": get_value(user[1]),
        "username": get_value(user[2]),
        "phone": get_value(user[3]),
        "email": get_value(user[4])
    }

@app.get("/posts")
def get_posts(
    area_id: str = Query("area1"),
    page: int = Query(1),
    limit: int = Query(20),
    current_user: dict = Depends(get_current_user)
):
    offset = (page - 1) * limit
    
    result = execute_sql(
        "SELECT p.*, u.display_name, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.area_id = ? AND p.is_deleted = 0 ORDER BY p.created_at DESC LIMIT ? OFFSET ?",
        [area_id, limit, offset]
    )
    
    rows = result.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
    
    return [{
        "id": row[0],
        "user_id": row[1],
        "area_id": row[2],
        "text": row[4],
        "category": row[5],
        "created_at": row[8],
        "user": {"display_name": row[11], "username": row[12]}
    } for row in rows]

@app.post("/posts")
def create_post(post_data: PostCreate, current_user: dict = Depends(get_current_user)):
    post_id = str(uuid.uuid4())
    
    execute_sql(
        "INSERT INTO posts (id, user_id, area_id, text, category) VALUES (?, ?, ?, ?, ?)",
        [post_id, current_user["id"], post_data.area_id, post_data.text, post_data.category]
    )
    
    return {"status": "success", "message": "Post created", "data": {"post_id": post_id}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))