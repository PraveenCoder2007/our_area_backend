from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import libsql_client
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import uuid

# Environment variables
TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")

app = FastAPI(title="Our Area API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database connection
def get_db():
    return libsql_client.create_client(
        url=TURSO_DATABASE_URL,
        auth_token=TURSO_AUTH_TOKEN
    )

@app.get("/")
async def root():
    return {"message": "Our Area API is running on Vercel", "status": "ok"}

@app.post("/auth/login")
async def login(credentials: dict):
    db = get_db()
    
    result = db.execute(
        "SELECT * FROM users WHERE username = ?",
        [credentials["username"]]
    )
    
    if not result.rows or not pwd_context.verify(credentials["password"], result.rows[0]["password_hash"]):
        return {"error": "Invalid credentials"}
    
    token = jwt.encode(
        {"sub": result.rows[0]["id"], "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm="HS256"
    )
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/areas/near")
async def get_areas(lat: float, lng: float):
    db = get_db()
    result = db.execute("SELECT * FROM areas")
    return [{"id": row["id"], "name": row["name"]} for row in result.rows]