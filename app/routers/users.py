from fastapi import APIRouter, Depends, HTTPException, status
from ..models.schemas import UserResponse, UserUpdate, LocationCreate, LocationResponse, APIResponse
from ..core.auth import get_current_user
from ..core.database import get_database
import uuid

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    db = await get_database()
    
    # Get user with location
    user_query = """
        SELECT u.*, l.id as loc_id, l.country, l.state, l.district, l.city, 
               l.postal_code, l.address_line, l.latitude, l.longitude, l.created_at as loc_created_at
        FROM users u
        LEFT JOIN locations l ON u.location_id = l.id
        WHERE u.id = :user_id
    """
    
    user_data = await db.fetch_one(user_query, {"user_id": current_user["id"]})
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build response
    location = None
    if user_data["loc_id"]:
        location = LocationResponse(
            id=user_data["loc_id"],
            country=user_data["country"],
            state=user_data["state"],
            district=user_data["district"],
            city=user_data["city"],
            postal_code=user_data["postal_code"],
            address_line=user_data["address_line"],
            latitude=user_data["latitude"],
            longitude=user_data["longitude"],
            created_at=user_data["loc_created_at"]
        )
    
    return UserResponse(
        id=user_data["id"],
        display_name=user_data["display_name"],
        username=user_data["username"],
        phone=user_data["phone"],
        email=user_data["email"],
        avatar_url=user_data["avatar_url"],
        bio=user_data["bio"],
        is_verified=bool(user_data["is_verified"]),
        created_at=user_data["created_at"],
        location=location
    )

@router.put("/me", response_model=APIResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    # Build update query dynamically
    update_fields = []
    values = {"user_id": current_user["id"]}
    
    for field, value in user_update.dict(exclude_unset=True).items():
        update_fields.append(f"{field} = :{field}")
        values[field] = value
    
    if not update_fields:
        return APIResponse(status="success", message="No changes to update")
    
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = :user_id"
    await db.execute(query, values)
    
    return APIResponse(status="success", message="Profile updated successfully")

@router.post("/me/location", response_model=APIResponse)
async def create_update_location(
    location_data: LocationCreate,
    current_user: dict = Depends(get_current_user)
):
    db = await get_database()
    
    # Check if user already has a location
    existing_location_id = current_user.get("location_id")
    
    if existing_location_id:
        # Update existing location
        update_fields = []
        values = {"location_id": existing_location_id}
        
        for field, value in location_data.dict(exclude_unset=True).items():
            update_fields.append(f"{field} = :{field}")
            values[field] = value
        
        if update_fields:
            query = f"UPDATE locations SET {', '.join(update_fields)} WHERE id = :location_id"
            await db.execute(query, values)
    else:
        # Create new location
        location_id = str(uuid.uuid4())
        await db.execute(
            """INSERT INTO locations (id, country, state, district, city, postal_code, 
                                    address_line, latitude, longitude)
               VALUES (:id, :country, :state, :district, :city, :postal_code, 
                      :address_line, :latitude, :longitude)""",
            {
                "id": location_id,
                **location_data.dict()
            }
        )
        
        # Update user's location_id
        await db.execute(
            "UPDATE users SET location_id = :location_id WHERE id = :user_id",
            {"location_id": location_id, "user_id": current_user["id"]}
        )
    
    return APIResponse(status="success", message="Location updated successfully")