from fastapi import APIRouter, Query
from typing import List
from ..models.schemas import AreaResponse
from ..core.database import get_database
import math

router = APIRouter(prefix="/areas", tags=["areas"])

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in meters using Haversine formula"""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

@router.get("/near", response_model=List[AreaResponse])
async def get_nearby_areas(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: int = Query(10000, description="Search radius in meters")
):
    db = await get_database()
    
    # Get all areas (in a real app, you'd use spatial indexing)
    areas = await db.fetch_all("SELECT * FROM areas")
    
    nearby_areas = []
    for area in areas:
        distance = calculate_distance(lat, lng, area["center_lat"], area["center_lng"])
        if distance <= radius:
            nearby_areas.append(AreaResponse(
                id=area["id"],
                name=area["name"],
                center_lat=area["center_lat"],
                center_lng=area["center_lng"],
                radius_m=area["radius_m"]
            ))
    
    return nearby_areas