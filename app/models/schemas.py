from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import UUID



# defines a Pydantic model called ChatCreate for FastAPI request validation.
class ChatCreate(BaseModel):
    # optional Field title which describes the chat's title.
    title: Optional[str] = Field(default=None, description="Chat title")

    # openapi schema example payload for api docs.
    # this helps clients understand the expected forma when creating a new chat.
    model_config = {
        "json_schema_extra": {
            "examples": [{"title": "Research helper"}]
        }
    }

class MessageCreate(BaseModel):
    role: str = Field(..., description="Message role, e.g., user or assistant")
    content: str = Field(..., min_length=1, description="User message text")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"role": "user", "content": "Explain Fastapi in three sentence"}
            ]
        }
    }
class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatSummaryRead(BaseModel):
    chat_id: str
    messages: list[MessageRead]

class UserCreate(BaseModel):
    username: str

class UserRead(BaseModel):
    id: UUID
    username: str
    created_at: datetime

    class Config:
        orm_mode = True
