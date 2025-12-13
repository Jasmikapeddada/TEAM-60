# Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
cd "AI assistant for faculty"
pip install -r requirements.txt
```

### Step 2: Set API Key
```bash
# Windows PowerShell
$env:GROQ_API_KEY="your-api-key-here"

# Linux/Mac
export GROQ_API_KEY="your-api-key-here"
```

Or enter it in the Streamlit UI sidebar.

### Step 3: Build RAG Index (ONE TIME)
```bash
python rag/vector_store.py
```

**⚠️ REQUIRED:** Must run this before using the app!

### Step 4: Run Application
```bash
streamlit run app.py
```

### Step 5: Use It!
1. Enter API key in sidebar (if not set as env var)
2. Type your request in chat
3. View results

## 📝 Example Requests

```
Generate a 16-week teaching plan for Data Structures course
```

```
Create mid-semester exam questions covering Unit 1 and Unit 2
```

```
Generate assignments for all units with Apply and Analyze level questions
```

## 📍 Files to Update

| What to Change | File Location |
|----------------|---------------|
| API Key | `config/settings.py` OR Environment variable |
| LLM Model | `config/settings.py` → `LLM_MODEL` |
| RAG Chunk Size | `config/settings.py` → `CHUNK_SIZE` |
| Academic Weeks | `config/settings.py` → `ACADEMIC_WEEKS` |
| Bloom Distribution | `agents/assessment_agent.py` → `_get_default_bloom_distribution()` |
| Rubrics | `data/rubrics.json` |
| Exam Pattern | `data/exam_pattern.json` |
| Prompts | `agents/*_agent.py` → prompt variables |

## 🎯 Project Structure Quick Reference

```
AI assistant for faculty/
├── agents/              # All agent implementations
├── config/              # Configuration (UPDATE HERE)
├── data/                # Data files (place syllabus here)
├── orchestrator/        # Workflow controller
├── rag/                 # RAG pipeline (BUILD INDEX HERE)
├── ui/                  # UI components
├── utils/               # Utilities
├── app.py              # Main app (RUN THIS)
└── requirements.txt    # Dependencies
```

## ✅ Checklist

Before running:
- [ ] Dependencies installed
- [ ] API key set
- [ ] Syllabus in `data/syllabus/`
- [ ] RAG index built (`python rag/vector_store.py`)
- [ ] Port 8501 available

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Index not found | Run `python rag/vector_store.py` |
| API key error | Set environment variable or enter in UI |
| Module not found | `pip install -r requirements.txt` |
| Syllabus not found | Place file in `data/syllabus/` |

## 📚 Documentation

- `SETUP.md` - Detailed setup instructions
- `EXECUTION_GUIDE.md` - Complete workflow explanation
- `ARCHITECTURE_EXPLANATION.md` - System architecture details

---

**Ready to go! 🚀**

