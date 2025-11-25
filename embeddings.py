

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class EmbeddingModel:
    """
    Wrapper around a free HuggingFace sentence-transformer model.
    Used for generating embeddings for documents and queries.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        Returns numpy embeddings for a list of strings.
        """
        return self.model.encode(texts, convert_to_numpy=True)

    def embed_one(self, text: str) -> np.ndarray:
        """
        Convenience wrapper to embed a single string.
        """
        return self.model.encode([text], convert_to_numpy=True)[0]
