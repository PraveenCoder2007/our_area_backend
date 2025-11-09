from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PostCategory(str, Enum):
    EVENT = "event"
    BUSINESS = "business"
    ACTIVITY = "activity"
    NEWS = "news"
    QUESTION = "question"
    OTHER = "other"

class ReportReason(str, Enum):
    SPAM = "spam"
    INAPPROPRIATE = "inappropriate"
    HARASSMENT = "harassment"
    FAKE = "fake"
    OTHER = "other"

# Auth schemas
class UserSignup(BaseModel):
    display_name: str = Field(..., max_length=100)
    username: str = Field(..., max_length=50)
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# User schemas
class LocationCreate(BaseModel):
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    address_line: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LocationResponse(LocationCreate):
    id: str
    created_at: datetime

class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)

class UserResponse(BaseModel):
    id: str
    display_name: str
    username: str
    phone: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_verified: bool
    created_at: datetime
    location: Optional[LocationResponse] = None

# Area schemas
class AreaResponse(BaseModel):
    id: str
    name: str
    center_lat: float
    center_lng: float
    radius_m: int

# Post schemas
class PostCreate(BaseModel):
    text: str = Field(..., max_length=280)
    category: PostCategory
    images: Optional[List[str]] = []
    location_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    event_time: Optional[datetime] = None

class PostUpdate(BaseModel):
    text: Optional[str] = Field(None, max_length=280)
    category: Optional[PostCategory] = None
    event_time: Optional[datetime] = None

class PostImageResponse(BaseModel):
    id: str
    url: str
    order_idx: int

class PostResponse(BaseModel):
    id: str
    user_id: str
    area_id: str
    text: str
    category: str
    lat: Optional[float]
    lng: Optional[float]
    event_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    images: List[PostImageResponse] = []
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    is_wishlisted: bool = False
    user: Optional[dict] = None

# Comment schemas
class CommentCreate(BaseModel):
    text: str = Field(..., max_length=280)

class CommentUpdate(BaseModel):
    text: str = Field(..., max_length=280)

class CommentResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    text: str
    created_at: datetime
    user: Optional[dict] = None

# Report schemas
class ReportCreate(BaseModel):
    post_id: Optional[str] = None
    user_id: Optional[str] = None
    reason: ReportReason
    description: Optional[str] = Field(None, max_length=500)

# Response wrapper
class APIResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    message: Optional[str] = None