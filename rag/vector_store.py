"""
Vector Store - FAISS index management for RAG
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from config.settings import (
    EMBEDDING_MODEL, RAG_INDEX_PATH, RAG_CHUNKS_PATH,
    CHUNK_SIZE, CHUNK_OVERLAP
)
from rag.ingest import ingest_syllabus


class RAGVectorStore:
    """FAISS-based vector store for syllabus embeddings"""
    
    def __init__(self, embedding_model=None):
        """
        Initialize vector store.
        
        Args:
            embedding_model: SentenceTransformer model (defaults to configured model)
        """
        self.model = embedding_model or SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.chunks = []
        self.dimension = None
    
    def build_index(self, chunks):
        """
        Build FAISS index from chunks.
        
        Args:
            chunks: List of chunk dicts with 'text' key
        """
        if not chunks:
            raise ValueError("No chunks provided for indexing")
        
        self.chunks = chunks
        
        # Extract texts
        texts = [chunk.get("text", "") for chunk in chunks if chunk.get("text")]
        
        if not texts:
            raise ValueError("No valid text chunks found")
        
        print(f"[RAG] Encoding {len(texts)} chunks...")
        
        # Generate embeddings
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        
        # Ensure 2D array
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)
        
        self.dimension = embeddings.shape[1]
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
        print(f"[RAG] FAISS index built with {len(texts)} chunks (dim={self.dimension})")
    
    def save_index(self, index_path=None, chunks_path=None):
        """Save FAISS index and chunks to disk."""
        index_path = index_path or RAG_INDEX_PATH
        chunks_path = chunks_path or RAG_CHUNKS_PATH
        
        if self.index is None:
            raise ValueError("No index to save. Build index first.")
        
        # Create directories if needed
        os.makedirs(os.path.dirname(index_path) if os.path.dirname(index_path) else ".", exist_ok=True)
        os.makedirs(os.path.dirname(chunks_path) if os.path.dirname(chunks_path) else ".", exist_ok=True)
        
        # Save index
        faiss.write_index(self.index, index_path)
        
        # Save chunks
        with open(chunks_path, "wb") as f:
            pickle.dump(self.chunks, f)
        
        print(f"[RAG] Index saved to {index_path}")
        print(f"[RAG] Chunks saved to {chunks_path}")
    
    def load_index(self, index_path=None, chunks_path=None):
        """Load FAISS index and chunks from disk."""
        index_path = index_path or RAG_INDEX_PATH
        chunks_path = chunks_path or RAG_CHUNKS_PATH
        
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not os.path.exists(chunks_path):
            raise FileNotFoundError(f"Chunks file not found: {chunks_path}")
        
        # Load index
        self.index = faiss.read_index(index_path)
        self.dimension = self.index.d
        
        # Load chunks
        with open(chunks_path, "rb") as f:
            self.chunks = pickle.load(f)
        
        print(f"[RAG] Index loaded from {index_path}")
        print(f"[RAG] Chunks loaded from {chunks_path} ({len(self.chunks)} chunks)")
    
    def search(self, query, top_k=3):
        """
        Search for similar chunks.
        
        Args:
            query: Search query text
            top_k: Number of results to return
        
        Returns:
            List of similar chunks with scores
        """
        if self.index is None:
            raise ValueError("Index not loaded. Load or build index first.")
        
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Return results
        results = []
        for i, idx in enumerate(indices[0]):
            if 0 <= idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                chunk["distance"] = float(distances[0][i])
                chunk["score"] = 1.0 / (1.0 + float(distances[0][i]))  # Convert distance to similarity
                results.append(chunk)
        
        return results


def build_index_from_file(file_path, file_type=None):
    """
    Convenience function to build index from syllabus file.
    
    Args:
        file_path: Path to syllabus file (PDF or TXT)
        file_type: 'pdf' or 'txt' (auto-detected if None)
    
    Returns:
        RAGVectorStore instance
    """
    # Ingest syllabus
    chunks = ingest_syllabus(file_path, file_type)
    
    # Build index
    store = RAGVectorStore()
    store.build_index(chunks)
    
    return store


if __name__ == "__main__":
    # Build index from sample syllabus
    import sys
    
    syllabus_file = "data/syllabus/sample_syllabus.txt"
    if not os.path.exists(syllabus_file):
        syllabus_file = "data/syllabus/sample_syllabus.pdf"
    
    if os.path.exists(syllabus_file):
        print(f"[RAG] Building index from {syllabus_file}...")
        store = build_index_from_file(syllabus_file)
        store.save_index()
        print("[RAG] Index built and saved successfully!")
    else:
        print(f"[RAG] Error: Syllabus file not found. Please add syllabus to {syllabus_file}")

