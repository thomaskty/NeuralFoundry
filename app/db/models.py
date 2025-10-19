from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    Boolean, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

# -------------------------------------------------------------------------
# USERS
# -------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    chats = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    knowledge_bases = relationship("KnowledgeBase", back_populates="owner", cascade="all, delete-orphan")


# -------------------------------------------------------------------------
# CHAT SYSTEM
# -------------------------------------------------------------------------
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=True)
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    attached_kbs = relationship("ChatSessionKB", back_populates="chat", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True)  # matches e5-small-v2
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


# -------------------------------------------------------------------------
# KNOWLEDGE BASE SYSTEM
# -------------------------------------------------------------------------
class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationships
    owner = relationship("User", back_populates="knowledge_bases")
    documents = relationship("KBDocument", back_populates="kb", cascade="all, delete-orphan")
    chat_links = relationship("ChatSessionKB", back_populates="kb", cascade="all, delete-orphan")


class KBDocument(Base):
    __tablename__ = "kb_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    text_sha256 = Column(String, index=True, nullable=False)
    text_size = Column(Integer, nullable=True)
    doc_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    kb = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("KBChunk", back_populates="document", cascade="all, delete-orphan")


class KBChunk(Base):
    __tablename__ = "kb_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("kb_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    embedding = Column(Vector(384), nullable=True)
    indexed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("KBDocument", back_populates="chunks")


# -------------------------------------------------------------------------
# RELATIONSHIP TABLE: CHATS ↔ KNOWLEDGE BASES
# -------------------------------------------------------------------------
class ChatSessionKB(Base):
    __tablename__ = "chat_session_kbs"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    attached_at = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("ChatSession", back_populates="attached_kbs")
    kb = relationship("KnowledgeBase", back_populates="chat_links")
