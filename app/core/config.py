from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # API Keys
    MISTRAL_API_KEY: str
    OLLAMA_BASE_URL: str
    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # RAG Configuration - Chat History (Hybrid Approach)
    RECENT_MESSAGE_WINDOW: int = 10  # Always include last N messages
    OLDER_MESSAGE_RETRIEVAL: int = 3  # Retrieve N older relevant messages
    CHAT_HISTORY_THRESHOLD: float = 0.75  # For older message retrieval

    # RAG Configuration - Knowledge Base
    KB_CHUNK_THRESHOLD: float = 0.70
    MAX_KB_CHUNKS_PER_KB: int = 3

    # Token Limits (approximate word counts)
    MAX_RECENT_MESSAGES_TOKENS: int = 800  # ~10 messages
    MAX_OLDER_MESSAGES_TOKENS: int = 300  # ~3 messages
    MAX_KB_CONTEXT_TOKENS: int = 1500  # ~5 chunks

    # LLM Settings
    DEFAULT_LLM_MODEL: str = "mistral-small-latest"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()