import os
from mistralai import Mistral
from app.core.config import settings
import numpy as np


class EmbeddingClient:
    embedding_dim = 1024  # dimension of the embeddings

    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.model = "mistral-embed"
        self.embedding_dim = 1024
        self.client = Mistral(api_key=self.api_key)

    def get_embedding(self, text: str) -> np.ndarray:
        resp = self.client.embeddings.create(model=self.model, inputs=[text])
        vec = resp.data[0].embedding
        return np.array(vec, dtype=np.float32)

    def get_batch_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        resp = self.client.embeddings.create(model=self.model, inputs=texts)
        return [np.array(d.embedding, dtype=np.float32) for d in resp.data]
