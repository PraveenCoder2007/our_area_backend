from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import os
import libsql_client
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import uuid
from pydantic import BaseModel

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

def get_db():
    return libsql_client.create_client(
        url=os.getenv("TURSO_DB_URL"),
        auth_token=os.getenv("TURSO_DB_TOKEN")
    )

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

@app.post("/signup")
def signup(user_data: UserSignup):
    db = get_db()
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash(user_data.password)
    
    try:
        db.execute(
            "INSERT INTO users (id, display_name, username, password_hash) VALUES (?, ?, ?, ?)",
            [user_id, user_data.display_name, user_data.username, hashed_password]
        )
        return {"status": "success", "message": "User created"}
    except:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/login")
def login(credentials: UserLogin):
    db = get_db()
    
    result = db.execute(
        "SELECT * FROM users WHERE username = ?",
        [credentials.username]
    )
    
    if not result.rows or not pwd_context.verify(credentials.password, result.rows[0][7]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {"sub": result.rows[0][0], "exp": datetime.utcnow() + timedelta(minutes=30)},
        os.getenv("SECRET_KEY", "fallback-secret"),
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/areas")
def get_areas():
    db = get_db()
    result = db.execute("SELECT * FROM areas")
    
    return [{
        "id": row[0],
        "name": row[1],
        "center_lat": row[2],
        "center_lng": row[3],
        "radius_m": row[4]
    } for row in result.rows]

@app.get("/users")
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

@app.get("/posts")
def get_posts(
    area_id: str = Query("area1"),
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
def create_post(post_data: PostCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    post_id = str(uuid.uuid4())
    
    db.execute(
        "INSERT INTO posts (id, user_id, area_id, text, category) VALUES (?, ?, ?, ?, ?)",
        [post_id, current_user["id"], post_data.area_id, post_data.text, post_data.category]
    )
    
    return {"status": "success", "message": "Post created", "data": {"post_id": post_id}}

# Vercel handler
handler = app