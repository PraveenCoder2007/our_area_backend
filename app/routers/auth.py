from fastapi import APIRouter, HTTPException, status, Depends
from ..models.schemas import UserSignup, UserLogin, Token, APIResponse
from ..core.auth import get_password_hash, verify_password, create_access_token
from ..core.database import get_database
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=APIResponse)
async def signup(user_data: UserSignup):
    db = await get_database()
    
    # Check if username exists
    existing_user = await db.fetch_one(
        "SELECT id FROM users WHERE username = :username",
        {"username": user_data.username}
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    await db.execute(
        """INSERT INTO users (id, display_name, username, phone, email, password_hash)
           VALUES (:id, :display_name, :username, :phone, :email, :password_hash)""",
        {
            "id": user_id,
            "display_name": user_data.display_name,
            "username": user_data.username,
            "phone": user_data.phone,
            "email": user_data.email,
            "password_hash": hashed_password
        }
    )
    
    return APIResponse(status="success", message="User created successfully")

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    db = await get_database()
    
    user = await db.fetch_one(
        "SELECT * FROM users WHERE username = :username",
        {"username": user_credentials.username}
    )
    
    if not user or not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}