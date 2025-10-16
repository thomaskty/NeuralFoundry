from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # API Keys
    MISTRAL_API_KEY: str

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # RAG Configuration - Chat History
    CHAT_HISTORY_THRESHOLD: float = 0.75
    MAX_CHAT_HISTORY_RESULTS: int = 5

    # RAG Configuration - Knowledge Base
    KB_CHUNK_THRESHOLD: float = 0.70
    MAX_KB_CHUNKS_PER_KB: int = 3

    # Token Limits (approximate word counts)
    MAX_CHAT_HISTORY_TOKENS: int = 1000
    MAX_KB_CONTEXT_TOKENS: int = 2000

    # LLM Settings
    DEFAULT_LLM_MODEL: str = "mistral-small-latest"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()