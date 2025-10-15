from typing import Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_mistralai import ChatMistralAI
from mistralai import Mistral
from app.core.config import settings
from app.services.vector_stores.pgvector_vs import PgVectorStore
from app.services.wrappers.async_embedding import get_embedding_async

# initialize components (module-level singletons)
_pgv = PgVectorStore()
_mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)
_llm = ChatMistralAI(api_key=settings.MISTRAL_API_KEY, model_name="mistral-tiny")
_agent = create_react_agent(model=_llm, tools=[])  # add tools if needed

async def generate_response(session_id: str, user_text: str, similarity_limit: int = 5, similarity_threshold: Optional[float] = None):
    # 1. create embedding for user
    user_emb = await get_embedding_async(user_text)

    # 2. store user message
    await _pgv.add_message(session_id=session_id, role="user", content=user_text, embedding=user_emb)

    # 3. retrieve similar messages (you can try session_filter=session_id to prefer same-session)
    similar = await _pgv.search_similar(user_emb, limit=similarity_limit, threshold=similarity_threshold, session_filter=session_id)

    # 4. build context
    similar_texts = [f"- ({r['role']}) {r['content']}" for r in similar]
    context = "\n".join(similar_texts)

    messages = []
    if context:
        messages.append(SystemMessage(content=f"Relevant past conversation (most similar):\n{context}"))
    messages.append(HumanMessage(content=user_text))

    # 5. ask the agent (streaming)
    async for chunk in _agent.astream({"messages": messages}):
        if "agent" in chunk:
            for message in chunk["agent"]["messages"]:
                # tool call handling omitted — copy your process_chunks behavior if you need tool calls streamed
                if message.content:
                    assistant_reply = message.content

                    # store assistant reply and embedding
                    reply_emb = await get_embedding_async(assistant_reply)
                    await _pgv.add_message(session_id=session_id, role="assistant", content=assistant_reply, embedding=reply_emb)

                    return assistant_reply

    return "No response."
