import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384  # embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.function_map = []  # maps index position → function metadata

    def add_functions(self, functions):
        embeddings = []

        for fn in functions:
            vector = self.model.encode(fn.source_code)
            embeddings.append(vector)
            self.function_map.append(fn)

        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)

    def search_similar(self, query_text, top_k=3):
        query_vector = self.model.encode(query_text)
        query_vector = np.array([query_vector]).astype("float32")

        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.function_map):
                results.append(self.function_map[idx])

        return results