import asyncio
from app.db.database import engine

async def test_connection():
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: print("✅ Connected to PostgreSQL!"))

asyncio.run(test_connection())
