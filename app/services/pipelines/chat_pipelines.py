# app/services/pipelines/chat_pipelines.py
import asyncio
from typing import Optional, List, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_mistralai import ChatMistralAI

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
_agent = create_react_agent(model=_llm, tools=[])


async def _search_kb_if_attached(user_emb, kb_ids, max_kb_per_kb, kb_chunk_threshold):
    """Helper function to handle KB search with proper async handling"""
    if not kb_ids:
        return []
    return await _pgv.search_kb_chunks(
        vec=user_emb,
        kb_ids=kb_ids,
        limit_per_kb=max_kb_per_kb,
        threshold=kb_chunk_threshold
    )


def _estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 chars)"""
    return len(text) // 4


def _truncate_to_token_limit(items: List[Dict], max_tokens: int, text_key: str = "content") -> List[Dict]:
    """Truncate list of items to fit within token budget"""
    result = []
    current_tokens = 0

    for item in items:
        item_tokens = _estimate_tokens(item[text_key])
        if current_tokens + item_tokens > max_tokens:
            break
        result.append(item)
        current_tokens += item_tokens

    return result


async def generate_response_with_kb(
        chat_id: str,
        user_text: str,
        chat_history_threshold: Optional[float] = None,
        kb_chunk_threshold: Optional[float] = None,
        max_chat_history: Optional[int] = None,
        max_kb_per_kb: Optional[int] = None
) -> str:
    """
    Generate response using both chat history and knowledge base context.

    This function implements a RAG (Retrieval Augmented Generation) pipeline that:
    1. Searches chat history for relevant past messages
    2. Searches attached knowledge bases for relevant information
    3. Combines both contexts and generates a response

    Args:
        chat_id: Chat session ID
        user_text: User's input message
        chat_history_threshold: Min similarity for chat history (default from settings)
        kb_chunk_threshold: Min similarity for KB chunks (default from settings)
        max_chat_history: Max chat history results (default from settings)
        max_kb_per_kb: Max chunks per KB (default from settings)

    Returns:
        Generated assistant response
    """
    # Use settings defaults if not provided
    chat_history_threshold = chat_history_threshold or settings.CHAT_HISTORY_THRESHOLD
    kb_chunk_threshold = kb_chunk_threshold or settings.KB_CHUNK_THRESHOLD
    max_chat_history = max_chat_history or settings.MAX_CHAT_HISTORY_RESULTS
    max_kb_per_kb = max_kb_per_kb or settings.MAX_KB_CHUNKS_PER_KB

    # 1. Generate embedding for user query
    user_emb = await get_embedding_async(user_text)

    # 2. Store user message in database
    await _pgv.add_message(
        session_id=chat_id,
        role="user",
        content=user_text,
        embedding=user_emb
    )

    # 3. Get attached KB IDs
    kb_ids = await _pgv.get_attached_kb_ids(chat_id)

    # 4. Parallel search: Chat history + KB chunks
    chat_results, kb_results = await asyncio.gather(
        _pgv.search_similar(
            vec=user_emb,
            limit=max_chat_history,
            threshold=chat_history_threshold,
            session_filter=chat_id
        ),
        _search_kb_if_attached(user_emb, kb_ids, max_kb_per_kb, kb_chunk_threshold),
        return_exceptions=True
    )

    # Handle potential errors from parallel execution
    if isinstance(chat_results, Exception):
        print(f"Error searching chat history: {chat_results}")
        chat_results = []

    if isinstance(kb_results, Exception):
        print(f"Error searching KB chunks: {kb_results}")
        kb_results = []

    # 5. Apply token limits
    chat_results = _truncate_to_token_limit(
        chat_results,
        settings.MAX_CHAT_HISTORY_TOKENS,
        text_key="content"
    )

    kb_results = _truncate_to_token_limit(
        kb_results,
        settings.MAX_KB_CONTEXT_TOKENS,
        text_key="text"
    )

    # 6. Build context for LLM
    messages = []
    context_parts = []
    sources_used = []

    # Add KB context (general knowledge first)
    if kb_results:
        sources_used.append("knowledge base")
        kb_context_lines = []

        # Group by KB for better organization
        kb_grouped = {}
        for chunk in kb_results:
            kb_title = chunk.get("kb_title", "Unknown KB")
            if kb_title not in kb_grouped:
                kb_grouped[kb_title] = []
            kb_grouped[kb_title].append(chunk)

        for kb_title, chunks in kb_grouped.items():
            kb_context_lines.append(f"\n[Knowledge Base: {kb_title}]")
            for chunk in chunks:
                filename = chunk.get("filename", "Unknown")
                similarity = chunk.get("similarity", 0)
                kb_context_lines.append(
                    f"  • [From: {filename}] (relevance: {similarity:.2f})\n"
                    f"    {chunk['text'][:500]}..."  # Limit chunk display
                )

        context_parts.append("### Knowledge Base Information:\n" + "\n".join(kb_context_lines))

    # Add chat history context (specific conversation context)
    if chat_results:
        sources_used.append("conversation history")
        chat_context_lines = ["\n### Previous Conversation:"]
        for msg in chat_results:
            similarity = msg.get("similarity", 0)
            chat_context_lines.append(
                f"  • [{msg['role']}] (relevance: {similarity:.2f})\n"
                f"    {msg['content'][:300]}..."
            )
        context_parts.append("\n".join(chat_context_lines))

    # Build system message with context
    if context_parts:
        system_content = (
                "You are a helpful AI assistant. Use the following information to answer the user's question accurately.\n\n"
                + "\n\n".join(context_parts) +
                "\n\n---\n"
                "Important: Base your answer on the provided context. If the context doesn't contain relevant information, "
                "say so clearly. Always cite which source you're using (knowledge base or conversation history)."
        )
        messages.append(SystemMessage(content=system_content))

        # Add source transparency note
        sources_note = f"[Using: {', '.join(sources_used)}]"
    else:
        sources_note = "[Note: No relevant context found in knowledge base or conversation history]"
        messages.append(SystemMessage(
            content="You are a helpful AI assistant. Answer based on your general knowledge."
        ))

    # Add user query
    messages.append(HumanMessage(content=user_text))

    # 7. Generate response with streaming
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

    # 8. Add source transparency to response
    final_reply = f"{sources_note}\n\n{assistant_reply}"

    # 9. Store assistant response
    reply_emb = await get_embedding_async(assistant_reply)
    await _pgv.add_message(
        session_id=chat_id,
        role="assistant",
        content=final_reply,
        embedding=reply_emb
    )

    return final_reply


# Legacy function for backward compatibility
async def generate_response(
        session_id: str,
        user_text: str,
        similarity_limit: int = 5,
        similarity_threshold: Optional[float] = None
) -> str:
    """
    Legacy chat response function (without KB support).
    Kept for backward compatibility.
    """
    # 1. Generate embedding
    user_emb = await get_embedding_async(user_text)

    # 2. Store user message
    await _pgv.add_message(
        session_id=session_id,
        role="user",
        content=user_text,
        embedding=user_emb
    )

    # 3. Search similar messages
    similar = await _pgv.search_similar(
        user_emb,
        limit=similarity_limit,
        threshold=similarity_threshold,
        session_filter=session_id
    )

    # 4. Build context
    similar_texts = [f"- ({r['role']}) {r['content']}" for r in similar]
    context = "\n".join(similar_texts)

    messages = []
    if context:
        messages.append(
            SystemMessage(content=f"Relevant past conversation (most similar):\n{context}")
        )
    messages.append(HumanMessage(content=user_text))

    # 5. Generate response
    async for chunk in _agent.astream({"messages": messages}):
        if "agent" in chunk:
            for message in chunk["agent"]["messages"]:
                if message.content:
                    assistant_reply = message.content

                    # Store reply
                    reply_emb = await get_embedding_async(assistant_reply)
                    await _pgv.add_message(
                        session_id=session_id,
                        role="assistant",
                        content=assistant_reply,
                        embedding=reply_emb
                    )

                    return assistant_reply

    return "No response."