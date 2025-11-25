# backend/app/services/vectorstore.py

import faiss
import numpy as np
from typing import List, Dict, Any


class FaissStore:
    """
    Simple FAISS wrapper to store embeddings + metadata.
    Metadata is kept in parallel for retrieval.
    """

    def __init__(self, dim: int = 384):
        """
        Initialize a FAISS flat index (L2 distance) and empty metadata list.
        """
        self.index = faiss.IndexFlatL2(dim)
        self.metadata: List[Dict[str, Any]] = []

    def add(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]):
        """
        Add vectors and their corresponding metadata to the store.
        Args:
            vectors: np.ndarray of shape (n_vectors, dim)
            metadatas: list of dicts, length n_vectors
        """
        if len(vectors) != len(metadatas):
            raise ValueError("Vectors and metadata length mismatch")
        self.index.add(np.array(vectors, dtype="float32"))
        self.metadata.extend(metadatas)

    def query(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for top_k nearest neighbors to query_vector.
        Args:
            query_vector: np.ndarray of shape (dim,) or (1, dim)
            top_k: number of results to return
        Returns:
            List of metadata dicts for top_k closest vectors
        """
        qv = query_vector.reshape(1, -1).astype("float32")
        D, I = self.index.search(qv, top_k)
        results = []
        for i in I[0]:
            if i < len(self.metadata):
                results.append(self.metadata[i])
        return results

    def count(self) -> int:
        """
        Return number of vectors stored
        """
        return self.index.ntotal
