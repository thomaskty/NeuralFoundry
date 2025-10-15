import asyncio
from app.services.embedding.huggingface_embedding import EmbeddingClient
import numpy as np

_embedding_client = EmbeddingClient()

async def get_embedding_async(text: str) -> np.ndarray:
    # runs SentenceTransformer.encode in a thread
    return await asyncio.to_thread(_embedding_client.get_embedding, text)

async def get_batch_embeddings_async(texts: list[str]) -> list[np.ndarray]:
    return await asyncio.to_thread(_embedding_client.get_batch_embeddings, texts)



