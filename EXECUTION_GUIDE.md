# Complete Execution Guide

## 🎯 Overview

This guide explains the complete system architecture and how to execute the workflow end-to-end.

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Chat Interface (Primary)                        │   │
│  │  - User input                                     │   │
│  │  - Results display                                │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Orchestrator (orchestrator/workflow.py)        │
│  - Intent Extraction                                     │
│  - Workflow Coordination                                 │
│  - Agent Management                                      │
└──────┬───────────────────────┬──────────────────────────┘
       │                       │
       ▼                       ▼
┌──────────────┐      ┌─────────────────────┐
│  RAG Layer   │      │  Multi-Agent System │
│ (Vector DB)  │      └──────┬──────────────┘
│              │             │
│ - Ingest     │             ▼
│ - Vector     │   ┌────────────────────────┐
│ - Retrieve   │   │ 1. Syllabus Agent      │
└──────────────┘   │ 2. Lesson Planner      │
                   │ 3. Assessment Agent    │
                   │ 4. Evaluation Agent    │
                   │ 5. Compliance Agent    │
                   └──────┬─────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          Guardrails & Validators                         │
│  - Syllabus Compliance                                   │
│  - Bloom's Taxonomy Validation                           │
│  - Exam Pattern Compliance                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│          Evaluation Metrics Engine                       │
│  - Bloom Alignment Score                                 │
│  - Coverage Completeness                                 │
│  - Difficulty Balance                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Results Display (UI)                       │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Complete Workflow Steps

### Step 1: User Input
User types request in Streamlit chat interface:
```
"Generate a 16-week teaching plan for Data Structures course"
```

### Step 2: Intent Extraction
**Agent:** `IntentAgent`
**File:** `agents/intent_agent.py`
**Process:**
- Analyzes user input
- Extracts tasks, subject, exam type, units, etc.
- Returns structured intent

**Output:**
```json
{
  "tasks": ["teaching_plan"],
  "subject": "Data Structures",
  "weeks": 16,
  "units": []
}
```

### Step 3: Syllabus Parsing
**Agent:** `SyllabusAgent`
**File:** `agents/syllabus_agent.py`
**Process:**
- Retrieves syllabus context via RAG
- Parses structure using LLM
- Extracts units, topics, learning outcomes

**Output:**
```json
{
  "subject": "Data Structures",
  "units": [
    {
      "unit_number": 1,
      "unit_name": "Introduction",
      "topics": ["Arrays", "Linked Lists"],
      "hours": 10
    }
  ]
}
```

### Step 4: Content Generation
**Agents:** `LessonPlannerAgent`, `AssessmentAgent`
**Files:** 
- `agents/lesson_planner_agent.py`
- `agents/assessment_agent.py`

**Process:**
- Based on intent, appropriate agent generates content
- Uses RAG to retrieve relevant syllabus chunks
- Generates using LLM with syllabus context

### Step 5: Compliance Checking
**Agent:** `ComplianceAgent`
**File:** `agents/compliance_agent.py`
**Process:**
- Validates content against syllabus
- Checks Bloom's taxonomy compliance
- Verifies exam pattern rules
- Rejects or accepts generated content

### Step 6: Metrics Calculation
**Module:** `utils/evaluators.py`
**Process:**
- Calculates Bloom alignment score
- Measures coverage completeness
- Evaluates difficulty balance

### Step 7: Results Display
**Module:** `ui/components.py`
**Process:**
- Formats and displays results in UI
- Shows teaching plans, questions, metrics
- Provides download option

## 📝 Detailed Component Explanation

### 1. RAG Pipeline

**Purpose:** Retrieve relevant syllabus content for context-aware generation

**Files:**
- `rag/ingest.py` - Document ingestion (PDF/TXT)
- `rag/vector_store.py` - FAISS index management
- `rag/retriever.py` - Semantic search interface

**Usage:**
```python
from rag.retriever import RAGRetriever

retriever = RAGRetriever()
chunks = retriever.retrieve("search algorithms", top_k=5)
```

### 2. Agents

Each agent has a specific role:

#### Intent Agent
- **Input:** User natural language request
- **Output:** Structured intent JSON
- **Key Functions:** `extract_intent()`

#### Syllabus Agent
- **Input:** Syllabus file path (optional)
- **Output:** Parsed syllabus structure
- **Key Functions:** `parse_syllabus()`

#### Lesson Planner Agent
- **Input:** Parsed syllabus, number of weeks
- **Output:** Weekly teaching plan
- **Key Functions:** `create_lesson_plan()`

#### Assessment Agent
- **Input:** Syllabus, exam type, Bloom distribution
- **Output:** Generated questions
- **Key Functions:** `generate_questions()`

#### Evaluation Agent
- **Input:** Question, student answer, rubric
- **Output:** Score and feedback
- **Key Functions:** `evaluate_answer()`

#### Compliance Agent
- **Input:** Generated content, syllabus context
- **Output:** Validation result
- **Key Functions:** `validate()`, `validate_batch()`

### 3. Orchestrator

**Purpose:** Coordinates all agents in proper sequence

**File:** `orchestrator/workflow.py`

**Key Method:** `execute_workflow(user_input, syllabus_path)`

**Flow:**
1. Extract intent
2. Parse syllabus
3. Generate content (based on intent)
4. Validate compliance
5. Calculate metrics
6. Save results

### 4. Guardrails

**Purpose:** Ensure academic correctness

**Implementation:** `ComplianceAgent`

**Checks:**
- ✅ Syllabus boundaries
- ✅ Bloom's taxonomy levels
- ✅ Exam pattern rules
- ✅ No content outside syllabus

### 5. Evaluation Metrics

**Purpose:** Measure quality of generated content

**File:** `utils/evaluators.py`

**Metrics:**
- Bloom Alignment Score (0-1)
- Coverage Completeness (0-1)
- Difficulty Balance (0-1)
- Explainability Score (0-1)

## 🚀 Execution Steps

### Prerequisites Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set API key
export GROQ_API_KEY="your-key"

# 3. Place syllabus
# Copy syllabus to data/syllabus/sample_syllabus.txt

# 4. Build RAG index (REQUIRED)
python rag/vector_store.py
```

### Running the Application
```bash
streamlit run app.py
```

### Using the Application

1. **Configure API Key** (in sidebar)
2. **Upload Syllabus** (optional, or use default)
3. **Type Request** (in chat interface)
4. **View Results** (generated content displayed below)

## 📍 Where to Update Code

### For Your Requirements:

#### 1. Change LLM Provider/Model
**File:** `config/settings.py`
```python
LLM_PROVIDER = "groq"  # or "openai"
LLM_MODEL = "llama-3.3-70b-versatile"  # Change model name
```

#### 2. Adjust RAG Parameters
**File:** `config/settings.py`
```python
CHUNK_SIZE = 500      # Increase for longer context
CHUNK_OVERLAP = 50    # Adjust overlap
TOP_K = 3             # More chunks = more context
```

#### 3. Modify Academic Calendar
**File:** `config/settings.py`
```python
ACADEMIC_WEEKS = 16    # Change semester length
HOURS_PER_WEEK = 3     # Change weekly hours
```

#### 4. Customize Bloom Distribution
**File:** `agents/assessment_agent.py`
```python
def _get_default_bloom_distribution(self, exam_type: str):
    # Modify distribution per exam type
```

#### 5. Update Rubrics
**File:** `data/rubrics.json`
```json
{
  "answer_evaluation": {
    "criteria": [
      // Add/modify criteria
    ]
  }
}
```

#### 6. Change Exam Pattern
**File:** `data/exam_pattern.json`
```json
{
  "exam_name": "...",
  "sections": [
    // Modify sections
  ]
}
```

#### 7. Customize Prompts
**Files:**
- `agents/*_agent.py` - Each agent has prompt templates
- Modify the `prompt` variable in agent methods

#### 8. Add New Agent
1. Create file: `agents/new_agent.py`
2. Implement agent class
3. Add to `orchestrator/workflow.py`
4. Update imports

#### 9. Modify UI Components
**File:** `ui/components.py`
- Add new display functions
- Modify existing display functions

#### 10. Change Workflow Order
**File:** `orchestrator/workflow.py`
- Modify `execute_workflow()` method
- Reorder agent calls

## 🔍 Testing Individual Components

### Test RAG Index Building
```bash
python rag/vector_store.py
```

### Test Intent Agent
```python
python agents/intent_agent.py
```

### Test Orchestrator
```python
python orchestrator/workflow.py
```

### Test Full Workflow
```bash
streamlit run app.py
# Then use UI to test
```

## 📊 Output Files

Generated files:
- `rag_index.faiss` - FAISS vector index
- `chunks.pkl` - Chunk metadata
- `outputs/logs.json` - Workflow execution logs

## 🎓 Example Use Cases

### Use Case 1: Generate Teaching Plan
```
Input: "Create a 16-week teaching plan for Data Structures"
Flow:
1. Intent → teaching_plan task
2. Syllabus → Parse units
3. Lesson Planner → Generate weekly schedule
4. Compliance → Validate topics
5. Output → Display plan
```

### Use Case 2: Create Question Paper
```
Input: "Generate mid-semester exam with 10 questions"
Flow:
1. Intent → questions, exam_type=mid
2. Syllabus → Get context
3. Assessment Agent → Generate questions
4. Compliance → Check Bloom levels
5. Output → Display questions
```

### Use Case 3: Evaluate Answer
```
Input: (Question + Student Answer)
Flow:
1. Evaluation Agent → Score answer
2. Rubrics → Apply criteria
3. Output → Score + Feedback
```

## ✅ Checklist Before Running

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API key set (environment or UI)
- [ ] Syllabus file placed in `data/syllabus/`
- [ ] RAG index built (`python rag/vector_store.py`)
- [ ] All config files present
- [ ] Port 8501 available (for Streamlit)

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Index not found" | Run `python rag/vector_store.py` |
| "API key error" | Set environment variable or enter in UI |
| "Module not found" | `pip install -r requirements.txt` |
| "Syllabus not found" | Place file in `data/syllabus/` |
| "Slow performance" | First run downloads models |
| "Import error" | Check Python path, ensure all `__init__.py` exist |

## 🎯 Next Steps

1. **Customize:** Update configs for your needs
2. **Test:** Run with sample syllabus
3. **Iterate:** Modify prompts/agents as needed
4. **Deploy:** Can be deployed on Streamlit Cloud

---

**Happy Coding! 🚀**

