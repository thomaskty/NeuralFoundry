# services/embedding/huggingface_embedding.py
import os
import requests
import numpy as np
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingClient:
    def __init__(self):
        self.model_name = "intfloat/e5-small-v2"
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def get_embedding(self, text: str) -> np.ndarray:
        print('getting the embedding from huggingface')
        vec = self.model.encode(text, convert_to_numpy=True)
        return np.array(vec, dtype=np.float32)

    def get_batch_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [np.array(e, dtype=np.float32) for e in embeddings]


# embedding_client = EmbeddingClient()
# output = embedding_client.get_embedding('i like hugging face')
# print(output)
