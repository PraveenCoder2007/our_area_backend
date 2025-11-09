import databases
import aiosqlite
from .config import DATABASE_URL, TURSO_DATABASE_URL, TURSO_AUTH_TOKEN

# Configure database with Turso auth token if available
if TURSO_DATABASE_URL and TURSO_AUTH_TOKEN:
    database = databases.Database(
        TURSO_DATABASE_URL,
        connect_args={"auth_token": TURSO_AUTH_TOKEN}
    )
else:
    database = databases.Database(DATABASE_URL)

async def init_db():
    """Initialize database with schema"""
    # Skip schema creation for Turso (should be done via Turso CLI)
    if "turso" in DATABASE_URL.lower():
        return
    
    async with aiosqlite.connect(DATABASE_URL.replace("sqlite:///", "")) as db:
        with open("schema.sql", "r") as f:
            schema = f.read()
        await db.executescript(schema)
        await db.commit()

async def get_database():
    return database