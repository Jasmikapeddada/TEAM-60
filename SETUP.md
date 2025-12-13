# Setup and Execution Guide

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API Key (recommended) OR OpenAI API Key
  - Get Groq API Key: https://console.groq.com/
  - Get OpenAI API Key: https://platform.openai.com/

## 🚀 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
cd "AI assistant for faculty"
pip install -r requirements.txt
```

**Note:** First installation may take a few minutes as it downloads:
- SentenceTransformer models (~80MB)
- FAISS library
- Other dependencies

### Step 2: Set Up API Key

**Option A: Environment Variable (Recommended)**

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="your-groq-api-key-here"
# OR
$env:OPENAI_API_KEY="your-openai-api-key-here"
```

**Windows (CMD):**
```cmd
set GROQ_API_KEY=your-groq-api-key-here
set OPENAI_API_KEY=your-openai-api-key-here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="your-groq-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Option B: .env File**

Create a `.env` file in the project root:
```
GROQ_API_KEY=your-groq-api-key-here
# OR
OPENAI_API_KEY=your-openai-api-key-here
```

**Option C: Enter in Streamlit UI** (will be used for current session)

### Step 3: Prepare Syllabus Data

Place your syllabus file in `data/syllabus/`:

- **Preferred:** `sample_syllabus.txt` (text format)
- **Alternative:** `sample_syllabus.pdf` (PDF format)

If you don't have a syllabus, the system will still run but may not work optimally.

### Step 4: Build RAG Index (REQUIRED - First Time Only)

Before running the app, build the FAISS vector index:

```bash
python rag/vector_store.py
```

This will:
1. Load the syllabus from `data/syllabus/sample_syllabus.txt` (or PDF)
2. Chunk the text into smaller pieces
3. Generate embeddings using sentence-transformers
4. Build FAISS index
5. Save as `rag_index.faiss` and `chunks.pkl`

**Expected output:**
```
[RAG] Ingested X chunks from data/syllabus/sample_syllabus.txt
[RAG] Encoding X chunks...
[RAG] FAISS index built with X chunks (dim=384)
[RAG] Index saved to rag_index.faiss
[RAG] Chunks saved to chunks.pkl
```

**⚠️ Important:** You must rebuild the index if you change the syllabus file!

### Step 5: Run the Streamlit Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎯 How to Use the Application

### Interface Overview

1. **Sidebar (Left):**
   - API Configuration: Enter your API key
   - Syllabus Upload: Upload your syllabus (optional)
   - Quick Actions: Clear chat history

2. **Main Area (Center):**
   - Chat Interface: Type your requests
   - Results Display: View generated content

### Example Requests

#### 1. Generate Teaching Plan
```
Generate a 16-week teaching plan for Data Structures and Algorithms course
```

#### 2. Create Questions
```
Create a question paper for mid-semester exam with 10 questions covering all units
```

#### 3. Generate Assignments
```
Generate assignments for Unit 2 and Unit 3 with questions from Apply and Analyze levels
```

#### 4. Combined Request
```
Create a teaching plan and generate mid-semester questions for Data Structures course
```

### Workflow Execution

When you submit a request:

1. **Intent Extraction** → System understands what you want
2. **Syllabus Parsing** → Extracts structure from syllabus
3. **Content Generation** → Agents create the requested content
4. **Compliance Checking** → Validates against syllabus and rules
5. **Metrics Calculation** → Evaluates quality
6. **Results Display** → Shows generated content

## 📁 Project Structure

```
AI assistant for faculty/
├── agents/              # Agent implementations
│   ├── intent_agent.py
│   ├── syllabus_agent.py
│   ├── lesson_planner_agent.py
│   ├── assessment_agent.py
│   ├── evaluation_agent.py
│   └── compliance_agent.py
├── config/              # Configuration
│   ├── settings.py      # ← Update API keys/model here
│   └── constants.py
├── data/                # Data files
│   ├── bloom_taxonomy.json
│   ├── exam_pattern.json
│   ├── rubrics.json
│   └── syllabus/        # ← Place syllabus here
├── orchestrator/        # Workflow controller
│   └── workflow.py
├── rag/                 # RAG implementation
│   ├── ingest.py
│   ├── vector_store.py  # ← Run this to build index
│   └── retriever.py
├── ui/                  # UI components
│   └── components.py
├── utils/               # Utilities
│   ├── llm_client.py
│   ├── evaluators.py
│   └── helpers.py
├── app.py              # ← Main Streamlit app
├── requirements.txt
└── SETUP.md            # This file
```

## ⚙️ Configuration Updates

### Change LLM Provider

Edit `config/settings.py`:
```python
LLM_PROVIDER = "groq"  # or "openai"
LLM_MODEL = "llama-3.3-70b-versatile"  # Groq model
# OR
LLM_MODEL = "gpt-4o-mini"  # OpenAI model
```

### Adjust RAG Parameters

Edit `config/settings.py`:
```python
CHUNK_SIZE = 500      # Size of text chunks
CHUNK_OVERLAP = 50    # Overlap between chunks
TOP_K = 3             # Number of retrieved chunks
```

### Change Academic Calendar

Edit `config/settings.py`:
```python
ACADEMIC_WEEKS = 16    # Number of weeks in semester
HOURS_PER_WEEK = 3     # Hours per week
```

## 🔧 Troubleshooting

### Error: "GROQ_API_KEY not found"
- Set the API key as environment variable OR enter in UI sidebar

### Error: "Index files not found"
- Run `python rag/vector_store.py` to build the index first

### Error: "No module named 'xxx'"
- Install dependencies: `pip install -r requirements.txt`

### Error: "Syllabus file not found"
- Place syllabus in `data/syllabus/sample_syllabus.txt` or upload via UI

### App runs but generates errors
- Check that RAG index is built: `ls rag_index.faiss`
- Verify API key is correct
- Check syllabus file exists and is readable

### Slow performance
- First run downloads sentence-transformer model (~80MB)
- API calls depend on provider (Groq is typically faster)
- Large syllabus files take longer to process

## 📝 Notes

- **First Run:** May take longer as models download
- **Internet Required:** For API calls to Groq/OpenAI
- **Syllabus Format:** Works best with structured text (TXT preferred over PDF)
- **Rebuild Index:** Must rebuild if syllabus changes
- **Session State:** API key entered in UI is session-only (refresh clears it)

## 🎓 Example Workflow

1. **Setup:**
   ```bash
   pip install -r requirements.txt
   export GROQ_API_KEY="your-key"
   python rag/vector_store.py
   ```

2. **Run:**
   ```bash
   streamlit run app.py
   ```

3. **Use:**
   - Enter API key in sidebar (if not in environment)
   - Type: "Generate a 16-week teaching plan for Data Structures"
   - Click enter
   - View results in main area

## 🚨 Important Reminders

1. ✅ Build RAG index BEFORE first run: `python rag/vector_store.py`
2. ✅ Set API key (environment variable OR UI)
3. ✅ Place syllabus in `data/syllabus/`
4. ✅ Rebuild index if syllabus changes

## 📞 Support

For issues:
1. Check error messages in terminal/UI
2. Verify all prerequisites are met
3. Check that index is built
4. Verify API key is valid

Happy teaching! 🎓

