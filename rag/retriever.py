from vector_store import RAGVectorStore
from sentence_transformers import SentenceTransformer

class RAGRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.store = RAGVectorStore(self.model)
        self.store.load_index()

    def retrieve(self, query, top_k=3):
        """
        Retrieve top-k relevant chunks for the query with metadata and similarity score.
        """
        query_emb = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.store.index.search(query_emb, top_k)
        results = []
        for i, score in zip(indices[0], distances[0]):
            chunk = self.store.chunks[i]
            results.append({
                'text': chunk['text'],
                'page': chunk.get('page', 'N/A'),
                'unit': chunk.get('unit', 'Unknown'),
                'bloom_level': chunk.get('bloom_level', 'Unknown'),
                'score': float(score)
            })
        return results

if __name__ == "__main__":
    retriever = RAGRetriever()
    query = "Generate assignments for Unit-2 on Search Techniques, Bloom: Apply"
    top_chunks = retriever.retrieve(query, top_k=3)

    print(f"Query: {query}")
    for i, chunk in enumerate(top_chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Unit/Topic: {chunk['unit']}")
        print(f"Page: {chunk['page']}")
        print(f"Bloom Level: {chunk['bloom_level']}")
        print(f"Similarity Score: {chunk['score']:.4f}")
        print("Content:", chunk['text'][:250], "...")
