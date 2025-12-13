"""
RAG Retriever - Retrieval interface for vector store
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rag.vector_store import RAGVectorStore
from config.settings import RAG_INDEX_PATH, RAG_CHUNKS_PATH, TOP_K


class RAGRetriever:
    """Retriever for RAG-based context retrieval"""
    
    def __init__(self, index_path=None, chunks_path=None):
        """
        Initialize RAG retriever.
        
        Args:
            index_path: Path to FAISS index file
            chunks_path: Path to chunks pickle file
        """
        self.index_path = index_path or RAG_INDEX_PATH
        self.chunks_path = chunks_path or RAG_CHUNKS_PATH
        self.store = None
        self._load_store()
    
    def _load_store(self):
        """Load vector store if index exists."""
        if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
            try:
                self.store = RAGVectorStore()
                self.store.load_index(self.index_path, self.chunks_path)
            except Exception as e:
                print(f"[RAG] Warning: Could not load index: {e}")
                print("[RAG] Run 'python rag/vector_store.py' to build index first.")
                self.store = None
        else:
            print(f"[RAG] Warning: Index files not found.")
            print(f"[RAG] Run 'python rag/vector_store.py' to build index first.")
            self.store = None
    
    def retrieve(self, query, top_k=None, unit_filter=None, bloom_filter=None):
        """
        Retrieve relevant chunks for query.
        
        Args:
            query: Search query
            top_k: Number of results (defaults to configured TOP_K)
            unit_filter: Optional unit name to filter by
            bloom_filter: Optional Bloom level to filter by
        
        Returns:
            List of relevant chunks
        """
        if self.store is None:
            return []
        
        top_k = top_k or TOP_K
        
        # Retrieve chunks
        results = self.store.search(query, top_k=top_k * 2)  # Get more for filtering
        
        # Apply filters
        if unit_filter:
            results = [r for r in results if unit_filter.lower() in r.get("unit", "").lower()]
        
        if bloom_filter:
            results = [r for r in results if r.get("bloom_level") == bloom_filter]
        
        # Return top_k after filtering
        return results[:top_k]
    
    def retrieve_context(self, query, top_k=None):
        """
        Retrieve and format context as text.
        
        Args:
            query: Search query
            top_k: Number of chunks
        
        Returns:
            Formatted context string
        """
        chunks = self.retrieve(query, top_k)
        
        if not chunks:
            return ""
        
        # Format chunks as context
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Chunk {i} - {chunk.get('unit', 'Unknown')}]\n{chunk['text']}")
        
        return "\n\n".join(context_parts)
    
    def is_ready(self):
        """Check if retriever is ready (index loaded)."""
        return self.store is not None


if __name__ == "__main__":
    # Test retriever
    retriever = RAGRetriever()
    
    if retriever.is_ready():
        query = "Knowledge representation and reasoning"
        results = retriever.retrieve(query)
        
        print(f"\nQuery: {query}")
        print(f"Retrieved {len(results)} chunks:\n")
        
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r.get('unit', 'Unknown')}] Score: {r.get('score', 0):.3f}")
            print(f"   {r['text'][:200]}...\n")
    else:
        print("Retriever not ready. Build index first.")

