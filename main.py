from sqlalchemy import text
from fastapi import FastAPI
from app.services.llm_clients.mistral_client import LLMClient
from contextlib import asynccontextmanager
from app.routers.chat_router import router as chat_router
from app.routers.user_router import router as user_router
from app.db.database import engine
from app.db.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    application context management
    """
    print('App startup: initializing Mistral client and database...')
    global llm_client
    llm_client = LLMClient()

    # Initialize database tables
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    yield  # Application runs after this point
    print('App shutdown complete')

app = FastAPI(title="NeuralFoundry", version="0.0.0", lifespan=lifespan)
app.include_router(chat_router)
app.include_router(user_router)