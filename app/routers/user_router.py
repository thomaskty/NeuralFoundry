import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.db.models import User, ChatSession
from app.models.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user and store it in the database.
    """
    # Check if username already exists
    existing = await db.execute(select(User).where(User.username == payload.username))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        id=uuid.uuid4().hex,
        username=payload.username,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.get("/", response_model=list[UserRead])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    """
    Fetch all registered users.
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Fetch details for a specific user by ID.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/{user_id}/chats")
async def get_user_chats(user_id: str, db: AsyncSession = Depends(get_db)):
    """
    Fetch all chats created by a given user.
    """
    # Ensure the user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chats_result = await db.execute(select(ChatSession).where(ChatSession.user_id == user_id))
    chats = chats_result.scalars().all()

    return {
        "user_id": user_id,
        "username": user.username,
        "chats": [
            {"id": c.id, "title": c.title, "created_at": c.created_at}
            for c in chats
        ],
    }
