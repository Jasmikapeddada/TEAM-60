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
        """Build FAISS index from chunk texts safely."""
        self.chunks = chunks

        texts = [c["text"] for c in chunks if c.get("text")]

        if len(texts) == 0:
            raise ValueError("No valid text chunks found for embedding.")

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        # Force 2D shape
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)

        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        print(f"[RAG] FAISS index built with {len(texts)} chunks.")

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


# 🔽 TXT FILE INGESTION
def ingest_txt_syllabus(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Simple chunking (same logic as PDF pipeline)
    words = text.split()
    chunks = []
    chunk_size = 200
    overlap = 40
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_text = " ".join(words[start:end])
        chunks.append({
            "text": chunk_text,
            "page": 1,
            "unit": "Unknown",
            "bloom_level": "Apply"
        })
        start += (chunk_size - overlap)

    print(f"[RAG] Ingested {len(chunks)} chunks from TXT syllabus.")
    return chunks


if __name__ == "__main__":
    # 🔥 USE TXT FILE INSTEAD OF PDF
    chunks = ingest_txt_syllabus("data/syllabus/sample_syllabus.txt")

    store = RAGVectorStore()
    store.build_index(chunks)
    store.save_index()
