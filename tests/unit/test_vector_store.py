import numpy as np
from app.services.vector_store import VectorStore


def test_vector_store_basic():
    dim = 5
    store = VectorStore(dim=dim)

    v1 = np.array([1, 2, 3, 4, 5], dtype=np.float32)
    v2 = np.array([1, 78, 3, 4, 5], dtype=np.float32)

    store.add(v1, {"id": 1, "content": "hello world"})
    store.add(v2, {"id": 2, "content": "hello world 2"})

    query = np.array([1, 35, 3, 4, 5], dtype=np.float32)
    results, distances = store.search(query, top_k=2)

    assert len(results) == 2
    assert "id" in results[0]
    assert "content" in results[0]

    print("Search results:", results)
    print("Distances:", distances)
