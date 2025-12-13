import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

class RAGVectorStore:
    def __init__(self, embedding_model=None):
        self.model = embedding_model or SentenceTransformer(MODEL_NAME)
        self.index = None
        self.chunks = []

    def build_index(self, chunks):
        """Build FAISS index from chunk texts."""
        self.chunks = chunks
        texts = [c['text'] for c in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        print(f"[RAG] FAISS index built with {len(chunks)} chunks.")

    def save_index(self, index_path="rag_index.faiss", chunks_path="chunks.pkl"):
        faiss.write_index(self.index, index_path)
        with open(chunks_path, "wb") as f:
            pickle.dump(self.chunks, f)
        print("[RAG] Index and chunks saved.")

    def load_index(self, index_path="rag_index.faiss", chunks_path="chunks.pkl"):
        self.index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            self.chunks = pickle.load(f)
        print("[RAG] Index and chunks loaded.")

if __name__ == "__main__":
    from ingest import ingest_syllabus
    chunks = ingest_syllabus("data/syllabus/sample_syllabus.pdf")
    store = RAGVectorStore()
    store.build_index(chunks)
    store.save_index()
