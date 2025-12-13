"""
Configuration Settings
Update these based on your requirements
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# API CONFIGURATION
# ============================================
# Option 1: Set environment variable: export GROQ_API_KEY="your-key"
# Option 2: Set environment variable: export OPENAI_API_KEY="your-key"
# Option 3: Enter in Streamlit UI (will be saved in session)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Choose your LLM provider: "groq" or "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Change to "openai" if needed

# LLM Model Configuration
if LLM_PROVIDER == "groq":
    LLM_MODEL = "llama-3.3-70b-versatile"  # Groq model
    LLM_API_BASE = "https://api.groq.com/openai/v1"
    LLM_API_KEY = GROQ_API_KEY
else:
    LLM_MODEL = "gpt-4o-mini"  # OpenAI model
    LLM_API_BASE = "https://api.openai.com/v1"
    LLM_API_KEY = OPENAI_API_KEY

# LLM Parameters
LLM_TEMPERATURE = 0.3  # Lower for more deterministic academic content
LLM_MAX_TOKENS = 2048

# ============================================
# RAG CONFIGURATION
# ============================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # SentenceTransformer model
CHUNK_SIZE = 500  # Token size for text chunks
CHUNK_OVERLAP = 50  # Overlap between chunks
TOP_K = 3  # Number of relevant chunks to retrieve

# Vector Store Paths
RAG_INDEX_PATH = "rag_index.faiss"
RAG_CHUNKS_PATH = "chunks.pkl"

# ============================================
# DATA PATHS
# ============================================
DATA_DIR = "data"
SYLLABUS_DIR = os.path.join(DATA_DIR, "syllabus")
BLOOM_TAXONOMY_PATH = os.path.join(DATA_DIR, "bloom_taxonomy.json")
EXAM_PATTERN_PATH = os.path.join(DATA_DIR, "exam_pattern.json")
RUBRICS_PATH = os.path.join(DATA_DIR, "rubrics.json")
OUTPUTS_DIR = "outputs"

# ============================================
# AGENT CONFIGURATION
# ============================================
# Academic Calendar (default: 16 weeks semester)
ACADEMIC_WEEKS = 16
HOURS_PER_WEEK = 3

# ============================================
# VALIDATION
# ============================================
if not LLM_API_KEY and LLM_PROVIDER == "groq":
    print("Warning: GROQ_API_KEY not set. Set it as environment variable or in UI.")
if not LLM_API_KEY and LLM_PROVIDER == "openai":
    print("Warning: OPENAI_API_KEY not set. Set it as environment variable or in UI.")

