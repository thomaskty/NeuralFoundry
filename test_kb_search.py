import asyncio
from app.services.wrappers.async_embedding import get_embedding_async
from app.services.vector_stores.pgvector_vs import PgVectorStore


async def test_kb_search():
    pgv = PgVectorStore()

    # Get your KB ID from database
    kb_id = "aefec72e-1acf-4435-9f5a-4d61bbee6b0b"  # Replace with actual KB ID

    # Test query
    query = "what is the salary structure for thomaskutty at cimb bank?"
    print(f"Query: {query}")

    # Generate embedding
    query_emb = await get_embedding_async(query)
    print(f"Embedding generated: {len(query_emb)} dimensions")

    # Search
    results = await pgv.search_kb_chunks(
        vec=query_emb,
        kb_ids=[kb_id],
        limit_per_kb=5,
        threshold=0.0  # No threshold
    )

    print(f"\n✅ Found {len(results)} chunks")

    for i, result in enumerate(results):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Similarity: {result['similarity']:.4f}")
        print(f"KB: {result['kb_title']}")
        print(f"File: {result['filename']}")
        print(f"Text: {result['text'][:200]}...")


if __name__ == "__main__":
    asyncio.run(test_kb_search())