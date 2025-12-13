import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


class RAGRetriever:
    def __init__(self, index_path="rag_index.faiss", chunks_path="chunks.pkl"):
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            self.chunks = pickle.load(f)

    def retrieve(self, query, top_k=3):
        query_embedding = self.model.encode([query], convert_to_numpy=True)

        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            results.append(self.chunks[idx])

        return results


if __name__ == "__main__":
    retriever = RAGRetriever()
    query = "Artificial Intelligence & Machine Learning"
    results = retriever.retrieve(query)

    print("\nRetrieved Context:\n")
    for r in results:
        print("-", r["text"][:200], "\n")
