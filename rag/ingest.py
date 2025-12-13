import os
from PyPDF2 import PdfReader

def load_pdf(file_path):
    """Load PDF and return list of pages as strings."""
    reader = PdfReader(file_path)
    pages = [page.extract_text() for page in reader.pages if page.extract_text()]
    return pages

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into chunks with optional overlap.
    Returns list of dicts with text and metadata.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append({"text": " ".join(chunk_words)})
        start += (chunk_size - overlap)
    return chunks

def detect_unit(text):
    """Optional: detect unit from text (simple placeholder)."""
    # In real hackathon, you can parse "Unit 1", "Unit 2" headers
    if "unit-1" in text.lower(): return "Unit-1"
    if "unit-2" in text.lower(): return "Unit-2"
    return "Unknown"

def ingest_syllabus(pdf_path):
    """Load PDF and return list of chunks with metadata."""
    pages = load_pdf(pdf_path)
    all_chunks = []
    for i, page in enumerate(pages):
        page_chunks = chunk_text(page)
        for chunk in page_chunks:
            chunk['page'] = i + 1
            chunk['unit'] = detect_unit(chunk['text'])
            # optional: assign dummy Bloom level for demo
            chunk['bloom_level'] = "Apply"
            all_chunks.append(chunk)
    print(f"[RAG] Ingested {len(all_chunks)} chunks from {pdf_path}")
    return all_chunks

if __name__ == "__main__":
    chunks = ingest_syllabus("data/syllabus/sample_syllabus.pdf")
    print(chunks[:2])
