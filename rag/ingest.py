import os

def load_txt(file_path):
    """Load TXT file and return full text as a string."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return text


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into chunks with overlap.
    Returns list of dicts with text.
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
    """Detect unit from text (simple heuristic)."""
    text = text.lower()

    if "unit 1" in text or "unit-1" in text:
        return "Unit-1"
    if "unit 2" in text or "unit-2" in text:
        return "Unit-2"
    if "unit 3" in text or "unit-3" in text:
        return "Unit-3"

    return "Unknown"


def ingest_syllabus(txt_path):
    """Load TXT syllabus and return list of chunks with metadata."""
    text = load_txt(txt_path)
    chunks = chunk_text(text)

    all_chunks = []
    for i, chunk in enumerate(chunks):
        chunk["chunk_id"] = i
        chunk["unit"] = detect_unit(chunk["text"])
        chunk["bloom_level"] = "Apply"  # placeholder
        all_chunks.append(chunk)

    print(f"[RAG] Ingested {len(all_chunks)} chunks from TXT syllabus.")
    return all_chunks


if __name__ == "__main__":
    chunks = ingest_syllabus("data/syllabus/sample_syllabus.txt")
    print(chunks[:2])
