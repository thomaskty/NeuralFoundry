# app/services/pipelines/chat_pipelines.py
import asyncio
from typing import Optional, List, Dict
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama

from app.core.config import settings
from app.services.vector_stores.pgvector_vs import PgVectorStore
from app.services.wrappers.async_embedding import get_embedding_async

# Initialize components (module-level singletons)
_pgv = PgVectorStore()

_llm = ChatMistralAI(
    api_key=settings.MISTRAL_API_KEY,
    model_name=settings.DEFAULT_LLM_MODEL,
    temperature=settings.LLM_TEMPERATURE,
    max_tokens=settings.LLM_MAX_TOKENS
)

# _llm = ChatOllama(
#     model=settings.DEFAULT_LLM_MODEL,
#     temperature=settings.LLM_TEMPERATURE,
#     num_predict=settings.LLM_MAX_TOKENS,
#     base_url=settings.OLLAMA_BASE_URL or "http://localhost:11434"
# )


_agent = create_react_agent(model=_llm, tools=[])


def _format_relative_time(created_at) -> str:
    """Convert timestamp to relative time string"""
    try:
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        now = datetime.now(timezone.utc)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        diff = now - created_at

        if diff.seconds < 60:
            return "just now"
        elif diff.seconds < 3600:
            mins = diff.seconds // 60
            return f"{mins} minute{'s' if mins > 1 else ''} ago"
        elif diff.seconds < 86400:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.days == 1:
            return "1 day ago"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            return created_at.strftime("%b %d, %Y")
    except:
        return "recently"

async def _search_kb_if_attached(user_emb, kb_ids, max_kb_per_kb, kb_chunk_threshold):
    """Helper function to handle KB search with proper async handling"""
    if not kb_ids:
        return []  # ← Returns empty list if no KBs
    return await _pgv.search_kb_chunks(
        vec=user_emb,
        kb_ids=kb_ids,
        limit_per_kb=max_kb_per_kb,
        threshold=kb_chunk_threshold
    )

def _build_hybrid_context(
        recent_messages: List[Dict],
        older_messages: List[Dict],
        kb_results: List[Dict],
        custom_system_prompt: Optional[str]
) -> str:
    """
    Build structured context with natural conversation format and metadata.

    Format:
    - Chat's custom system prompt (if exists)
    - Recent conversation (last 10 messages)
    - Relevant past conversation (older retrieved messages)
    - Knowledge base context (if available)
    """
    context_parts = []

    # Base system prompt
    base_prompt = custom_system_prompt if custom_system_prompt else "You are a helpful AI assistant."
    context_parts.append(base_prompt)
    context_parts.append("")

    # Recent Conversation Section
    if recent_messages:
        context_parts.append("━" * 60)
        context_parts.append("RECENT CONVERSATION (Last {} messages)".format(len(recent_messages)))
        context_parts.append("━" * 60)
        context_parts.append("")

        for msg in recent_messages:
            time_str = _format_relative_time(msg.get('created_at'))
            role = msg['role'].capitalize()
            context_parts.append(f"{role} ({time_str}):")
            context_parts.append(msg['content'])
            context_parts.append("")

    # Older Relevant Conversation Section
    if older_messages:
        context_parts.append("━" * 60)
        context_parts.append("RELEVANT PAST CONVERSATION (From earlier messages)")
        context_parts.append("━" * 60)
        context_parts.append("")

        for msg in older_messages:
            time_str = _format_relative_time(msg.get('created_at'))
            similarity = msg.get('similarity', 0)
            role = msg['role'].capitalize()
            context_parts.append(f"{role} ({time_str} - Similarity: {similarity:.2f}):")
            context_parts.append(msg['content'])
            context_parts.append("")

    # Knowledge Base Context Section
    if kb_results:
        context_parts.append("━" * 60)
        context_parts.append("KNOWLEDGE BASE CONTEXT")
        context_parts.append("━" * 60)
        context_parts.append("")

        for chunk in kb_results:
            kb_title = chunk.get("kb_title", "Unknown KB")
            filename = chunk.get("filename", "Unknown")
            similarity = chunk.get("similarity", 0)

            context_parts.append(f"📚 From: \"{filename}\" (KB: {kb_title})")
            context_parts.append(f"   Similarity: {similarity:.2f}")
            context_parts.append("")
            context_parts.append(chunk['text'])
            context_parts.append("")

    # Instructions
    context_parts.append("━" * 60)
    context_parts.append("")
    context_parts.append(
        "Instructions:\n"
        "Based on the above context, answer the user's current question "
        "naturally and conversationally. Use the information provided but "
        "respond as if you naturally know this. Do not mention that you're "
        "using conversation history or knowledge bases."
    )

    return "\n".join(context_parts)


async def generate_response_with_kb(
        chat_id: str,
        user_text: str,
        chat_history_threshold: Optional[float] = None,
        kb_chunk_threshold: Optional[float] = None,
        recent_window: Optional[int] = None,
        older_retrieval: Optional[int] = None,
        max_kb_per_kb: Optional[int] = None
) -> Dict:
    """
    Generate response using hybrid context approach:
    - Recent conversation (last N messages - always included)
    - Older relevant messages (semantic retrieval from older messages)
    - Knowledge base chunks (if KBs attached)

    Returns dict with reply and metadata.
    """
    # Use settings defaults
    chat_history_threshold = chat_history_threshold or settings.CHAT_HISTORY_THRESHOLD
    kb_chunk_threshold = kb_chunk_threshold or settings.KB_CHUNK_THRESHOLD
    recent_window = recent_window or settings.RECENT_MESSAGE_WINDOW
    older_retrieval = older_retrieval or settings.OLDER_MESSAGE_RETRIEVAL
    max_kb_per_kb = max_kb_per_kb or settings.MAX_KB_CHUNKS_PER_KB

    # 1. Generate embedding for user query
    user_emb = await get_embedding_async(user_text)

    # 2. Store user message
    await _pgv.add_message(
        session_id=chat_id,
        role="user",
        content=user_text,
        embedding=user_emb
    )

    # 3. Get chat's custom system prompt
    custom_system_prompt = await _pgv.get_chat_system_prompt(chat_id)

    # 4. Get attached KB IDs
    kb_ids = await _pgv.get_attached_kb_ids(chat_id)

    # 5. Parallel fetch: Recent messages + Older messages + KB chunks
    recent_messages, older_messages, kb_results = await asyncio.gather(
        _pgv.get_recent_messages(chat_id, limit=recent_window),
        _pgv.search_similar_excluding_recent(
            vec=user_emb,
            session_id=chat_id,
            exclude_recent_count=recent_window,
            limit=older_retrieval,
            threshold=chat_history_threshold
        ),
        _search_kb_if_attached(user_emb, kb_ids, max_kb_per_kb, kb_chunk_threshold),
        return_exceptions=True
    )

    # Handle errors
    if isinstance(recent_messages, Exception):
        print(f"Error fetching recent messages: {recent_messages}")
        recent_messages = []

    if isinstance(older_messages, Exception):
        print(f"Error fetching older messages: {older_messages}")
        older_messages = []

    if isinstance(kb_results, Exception):
        print(f"Error fetching KB chunks: {kb_results}")
        kb_results = []

    # 6. Build structured context
    system_content = _build_hybrid_context(
        recent_messages=recent_messages,
        older_messages=older_messages,
        kb_results=kb_results,
        custom_system_prompt=custom_system_prompt
    )

    # 7. Prepare messages for LLM
    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_text)
    ]

    # 8. Generate response
    assistant_reply = ""
    try:
        async for chunk in _agent.astream({"messages": messages}):
            if "agent" in chunk:
                for message in chunk["agent"]["messages"]:
                    if message.content:
                        assistant_reply = message.content
                        break
    except Exception as e:
        print(f"Error generating response: {e}")
        assistant_reply = "I apologize, but I encountered an error generating a response."

    # 9. Prepare metadata
    kb_sources = []
    for chunk in kb_results:
        kb_title = chunk.get("kb_title", "Unknown")
        filename = chunk.get("filename", "Unknown")
        source_info = f"{kb_title} - {filename}"
        if source_info not in kb_sources:
            kb_sources.append(source_info)

    sources_used = []
    if recent_messages or older_messages:
        sources_used.append("conversation history")
    if kb_results:
        sources_used.append("knowledge base")

    metadata = {
        "sources_used": sources_used,
        "kb_sources": kb_sources,
        "recent_messages_count": len(recent_messages),
        "older_messages_count": len(older_messages),
        "kb_results_count": len(kb_results),
        "using_kb": len(kb_results) > 0,
        "using_history": len(recent_messages) > 0 or len(older_messages) > 0
    }

    # 10. Store clean assistant response
    reply_emb = await get_embedding_async(assistant_reply)
    await _pgv.add_message(
        session_id=chat_id,
        role="assistant",
        content=assistant_reply,
        embedding=reply_emb
    )

    # 11. Return response with metadata
    return {
        "reply": assistant_reply,
        "metadata": metadata
    }


# Legacy function for backward compatibility
async def generate_response(
        session_id: str,
        user_text: str,
        similarity_limit: int = 5,
        similarity_threshold: Optional[float] = None
) -> str:
    """Legacy chat response function (without KB support)."""
    user_emb = await get_embedding_async(user_text)

    await _pgv.add_message(
        session_id=session_id,
        role="user",
        content=user_text,
        embedding=user_emb
    )

    similar = await _pgv.search_similar(
        user_emb,
        limit=similarity_limit,
        threshold=similarity_threshold,
        session_filter=session_id
    )

    similar_texts = [f"- ({r['role']}) {r['content']}" for r in similar]
    context = "\n".join(similar_texts)

    messages = []
    if context:
        messages.append(
            SystemMessage(content=f"Relevant past conversation (most similar):\n{context}")
        )
    messages.append(HumanMessage(content=user_text))

    async for chunk in _agent.astream({"messages": messages}):
        if "agent" in chunk:
            for message in chunk["agent"]["messages"]:
                if message.content:
                    assistant_reply = message.content

                    reply_emb = await get_embedding_async(assistant_reply)
                    await _pgv.add_message(
                        session_id=session_id,
                        role="assistant",
                        content=assistant_reply,
                        embedding=reply_emb
                    )

                    return assistant_reply

    return "No response."