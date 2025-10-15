import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.database import engine, get_db, AsyncSessionLocal

@pytest.mark.asyncio
async def test_engine_creation():
    # Ensure the engine object exists and is usable
    assert engine is not None
    assert str(engine.url).startswith("postgresql+asyncpg://")

@pytest.mark.asyncio
async def test_session_creation():
    # Verify we can create and use an AsyncSession manually
    async with AsyncSessionLocal() as session:
        assert isinstance(session, AsyncSession)
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1

@pytest.mark.asyncio
async def test_get_db_yield_session():
    # get_db is a generator that yields a session
    gen = get_db()
    session = await anext(gen)  # Python 3.10+ syntax for async generators
    try:
        assert isinstance(session, AsyncSession)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        await gen.aclose()
