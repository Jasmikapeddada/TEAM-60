"""
RAG Document Ingestion - PDF and TXT processing
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyPDF2 import PdfReader
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


def load_pdf(file_path):
    """Load PDF and return list of pages as strings."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text.strip():
            pages.append(text)
    return pages


def load_txt(file_path):
    """Load text file and return content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Text file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text, chunk_size=None, overlap=None):
    """
    Split text into chunks with optional overlap.
    Returns list of dicts with text and metadata.
    """
    chunk_size = chunk_size or CHUNK_SIZE
    overlap = overlap or CHUNK_OVERLAP
    
    words = text.split()
    chunks = []
    start = 0
    
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        
        if chunk_text.strip():
            chunks.append({
                "text": chunk_text,
                "start_word": start,
                "end_word": min(end, len(words))
            })
        
        start += (chunk_size - overlap)
        if start >= len(words):
            break
    
    return chunks


def detect_unit(text, unit_patterns=None):
    """
    Detect unit number from text.
    Looks for patterns like "Unit 1", "UNIT-1", etc.
    """
    if unit_patterns is None:
        unit_patterns = [
            r"unit[\s-]*(\d+)",
            r"UNIT[\s-]*(\d+)",
            r"chapter[\s-]*(\d+)",
            r"CHAPTER[\s-]*(\d+)"
        ]
    
    import re
    text_lower = text.lower()
    
    for pattern in unit_patterns:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            unit_num = match.group(1)
            return f"Unit-{unit_num}"
    
    return "Unknown"


def ingest_syllabus(file_path, file_type=None):
    """
    Ingest syllabus from PDF or TXT file.
    Returns list of chunks with metadata.
    """
    # Detect file type
    if file_type is None:
        if file_path.lower().endswith('.pdf'):
            file_type = 'pdf'
        elif file_path.lower().endswith('.txt'):
            file_type = 'txt'
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
    
    # Load content
    if file_type == 'pdf':
        pages = load_pdf(file_path)
        full_text = "\n\n".join(pages)
    else:
        full_text = load_txt(file_path)
    
    # Chunk the text
    all_chunks = []
    page_chunks = chunk_text(full_text)
    
    for i, chunk in enumerate(page_chunks):
        # Detect unit from chunk text
        unit = detect_unit(chunk["text"])
        
        chunk_metadata = {
            "text": chunk["text"],
            "chunk_id": i,
            "unit": unit,
            "page": 1,  # For PDF, could track page numbers
            "bloom_level": "Apply"  # Default, can be updated later
        }
        all_chunks.append(chunk_metadata)
    
    print(f"[RAG] Ingested {len(all_chunks)} chunks from {file_path}")
    return all_chunks


if __name__ == "__main__":
    # Test ingestion
    test_file = "data/syllabus/sample_syllabus.txt"
    if os.path.exists(test_file):
        chunks = ingest_syllabus(test_file)
        print(f"Total chunks: {len(chunks)}")
        print(f"Sample chunk: {chunks[0]}")
    else:
        print(f"Test file not found: {test_file}")

