import asyncio
import aiosqlite
import uuid
from app.core.auth import get_password_hash

async def seed_database():
    """Seed the database with sample data"""
    async with aiosqlite.connect("our_area.db") as db:
        # First create the schema
        with open("schema.sql", "r") as f:
            schema = f.read()
        await db.executescript(schema)
        # Create sample areas
        areas = [
            {
                "id": str(uuid.uuid4()),
                "name": "Downtown",
                "center_lat": 40.7128,
                "center_lng": -74.0060,
                "radius_m": 2000
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Brooklyn Heights",
                "center_lat": 40.6962,
                "center_lng": -73.9961,
                "radius_m": 1500
            }
        ]
        
        for area in areas:
            await db.execute(
                "INSERT OR IGNORE INTO areas (id, name, center_lat, center_lng, radius_m) VALUES (?, ?, ?, ?, ?)",
                (area["id"], area["name"], area["center_lat"], area["center_lng"], area["radius_m"])
            )
        
        # Create sample location
        location_id = str(uuid.uuid4())
        await db.execute(
            """INSERT OR IGNORE INTO locations (id, country, state, city, latitude, longitude)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (location_id, "USA", "NY", "New York", 40.7128, -74.0060)
        )
        
        # Create sample user
        user_id = str(uuid.uuid4())
        password_hash = get_password_hash("password123")
        await db.execute(
            """INSERT OR IGNORE INTO users (id, display_name, username, password_hash, location_id, area_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, "John Doe", "johndoe", password_hash, location_id, areas[0]["id"])
        )
        
        await db.commit()
        print("Database seeded successfully!")
        print("Sample user: username='johndoe', password='password123'")

if __name__ == "__main__":
    asyncio.run(seed_database())