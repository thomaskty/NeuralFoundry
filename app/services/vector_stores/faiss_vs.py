# app/services/vector_stores/faiss_vs.py
import faiss
import numpy as np
from typing import Optional, Dict, Any, List
import asyncio
import os
import threading

class VectorStore:
    """
    FAISS-based vector store supporting multiple chat sessions.
    Includes async safety, batch add, and persistence.
    """
    def __init__(self, embedding_dim, persist_dir: Optional[str] = None):
        self.embedding_dim = embedding_dim
        self.persist_dir = persist_dir
        self._lock = threading.Lock()  # async safety
        self._indices: Dict[str, faiss.IndexFlatL2] = {}  # chat_id -> FAISS index
        self._metadata: Dict[str, List[Dict[str, Any]]] = {}  # chat_id -> list of metadata

        if persist_dir:
            os.makedirs(persist_dir, exist_ok=True)
            self._load_all()

    def add(self, vector: np.ndarray, meta: Dict[str, Any]):
        """
        Add a vector to the store.
        Meta must include 'chat_id', optionally 'user_id'.
        """
        chat_id = meta.get("chat_id")
        if chat_id is None:
            raise ValueError("Metadata must include 'chat_id'")
        if vector.shape[0] != self.embedding_dim:
            raise ValueError(f"Vector dimension {vector.shape[0]} does not match {self.embedding_dim}")

        with self._lock:
            if chat_id not in self._indices:
                self._indices[chat_id] = faiss.IndexFlatL2(self.embedding_dim)
                self._metadata[chat_id] = []

            self._indices[chat_id].add(np.array([vector], dtype=np.float32))
            self._metadata[chat_id].append(meta)

            if self.persist_dir:
                self._save_index(chat_id)

    def add_batch(self, vectors: np.ndarray, metas: List[Dict[str, Any]]):
        if vectors.shape[0] != len(metas):
            raise ValueError("Vectors and metas length mismatch")

        for vec, meta in zip(vectors, metas):
            self.add(vec, meta)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        chat_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Search for top_k vectors similar to query_vector.
        Can filter by chat_id and user_id.
        """
        with self._lock:
            if chat_id:
                if chat_id not in self._indices:
                    return [], []
                D, I = self._indices[chat_id].search(np.array([query_vector], dtype=np.float32), top_k)
                results = [self._metadata[chat_id][i] for i in I[0]]
                distances = D[0].tolist()
                if user_id:
                    # apply user_id filter
                    filtered_results = []
                    filtered_distances = []
                    for r, d in zip(results, distances):
                        if r.get("user_id") == user_id:
                            filtered_results.append(r)
                            filtered_distances.append(d)
                    return filtered_results, filtered_distances
                return results, distances

            # No chat_id: merge all
            all_results, all_distances = [], []
            for cid, index in self._indices.items():
                D, I = index.search(np.array([query_vector], dtype=np.float32), top_k)
                for i, d in zip(I[0], D[0]):
                    meta = self._metadata[cid][i]
                    if not user_id or meta.get("user_id") == user_id:
                        all_results.append(meta)
                        all_distances.append(float(d))
            return all_results[:top_k], all_distances[:top_k]

    def _save_index(self, chat_id: str):
        if not self.persist_dir:
            return
        faiss.write_index(self._indices[chat_id], os.path.join(self.persist_dir, f"{chat_id}.index"))
        # Save metadata
        import json
        with open(os.path.join(self.persist_dir, f"{chat_id}_meta.json"), "w") as f:
            json.dump(self._metadata[chat_id], f)

    def _load_all(self):
        import json
        for fname in os.listdir(self.persist_dir):
            if fname.endswith(".index"):
                chat_id = fname.replace(".index", "")
                self._indices[chat_id] = faiss.read_index(os.path.join(self.persist_dir, fname))
                # load metadata
                meta_path = os.path.join(self.persist_dir, f"{chat_id}_meta.json")
                if os.path.exists(meta_path):
                    with open(meta_path, "r") as f:
                        self._metadata[chat_id] = json.load(f)
                else:
                    self._metadata[chat_id] = []
