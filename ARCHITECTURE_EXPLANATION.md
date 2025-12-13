# System Architecture & Code Explanation

## 📐 Complete Architecture Overview

This document explains how all components work together.

## 🏗️ Architecture Layers

### Layer 1: User Interface (Streamlit)
**File:** `app.py`

**Purpose:** Chat-based interface for faculty to interact with the system

**Key Features:**
- Chat interface for natural language input
- Sidebar for API configuration and syllabus upload
- Results display with formatted output
- Download functionality

**Flow:**
```
User Input → Chat Interface → Orchestrator → Results Display
```

### Layer 2: Orchestrator (Workflow Controller)
**File:** `orchestrator/workflow.py`

**Purpose:** Coordinates all agents and manages workflow execution

**Key Components:**
- `Orchestrator` class - Main controller
- `execute_workflow()` - Main execution method

**Workflow Steps:**
1. Extract user intent
2. Parse syllabus
3. Generate content (based on intent)
4. Validate compliance
5. Calculate metrics
6. Save and return results

### Layer 3: RAG Layer (Retrieval)
**Files:** `rag/ingest.py`, `rag/vector_store.py`, `rag/retriever.py`

**Purpose:** Provide syllabus context to agents via semantic search

**Components:**
- **Ingest:** Loads and chunks syllabus documents
- **Vector Store:** Builds FAISS index from embeddings
- **Retriever:** Searches for relevant chunks

**How it works:**
```
Syllabus PDF/TXT → Chunking → Embeddings → FAISS Index
Query → Embedding → Search → Relevant Chunks
```

### Layer 4: Multi-Agent System
**Files:** `agents/*.py`

**Purpose:** Specialized agents for different academic tasks

#### Agent 1: Intent Agent
- **File:** `agents/intent_agent.py`
- **Role:** Understands user's intent from natural language
- **Input:** User request text
- **Output:** Structured intent JSON

#### Agent 2: Syllabus Agent
- **File:** `agents/syllabus_agent.py`
- **Role:** Parses syllabus into structured format
- **Input:** Syllabus file path (or RAG context)
- **Output:** Parsed syllabus with units, topics, outcomes

#### Agent 3: Lesson Planner Agent
- **File:** `agents/lesson_planner_agent.py`
- **Role:** Creates teaching schedules
- **Input:** Parsed syllabus, number of weeks
- **Output:** Weekly lesson plan

#### Agent 4: Assessment Agent
- **File:** `agents/assessment_agent.py`
- **Role:** Generates questions and assignments
- **Input:** Syllabus, exam type, Bloom distribution
- **Output:** Generated questions with Bloom levels

#### Agent 5: Evaluation Agent
- **File:** `agents/evaluation_agent.py`
- **Role:** Evaluates student answers
- **Input:** Question, student answer, rubric
- **Output:** Score and detailed feedback

#### Agent 6: Compliance Agent
- **File:** `agents/compliance_agent.py`
- **Role:** Validates generated content
- **Input:** Generated content, syllabus context
- **Output:** Validation status and issues

### Layer 5: Guardrails & Validation
**File:** `agents/compliance_agent.py`

**Purpose:** Ensure academic correctness and compliance

**Validations:**
- Syllabus boundaries (no outside topics)
- Bloom's taxonomy levels
- Exam pattern rules
- Content quality

### Layer 6: Evaluation Metrics
**File:** `utils/evaluators.py`

**Purpose:** Measure quality of generated content

**Metrics:**
- Bloom Alignment Score
- Coverage Completeness
- Difficulty Balance
- Explainability Score

## 🔄 Complete Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. USER INPUT                                           │
│    "Generate teaching plan for Data Structures"         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 2. INTENT AGENT                                         │
│    - Analyzes input                                      │
│    - Extracts: tasks, subject, weeks                    │
│    Output: {"tasks": ["teaching_plan"], ...}           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 3. SYLLABUS AGENT                                       │
│    - Retrieves syllabus via RAG                         │
│    - Parses structure                                   │
│    Output: {"units": [...], "topics": [...]}           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 4. CONTENT GENERATION (Based on Intent)                │
│    - Lesson Planner Agent (if teaching_plan)           │
│    - Assessment Agent (if questions)                   │
│    - Uses RAG to get relevant context                  │
│    Output: Generated content (plan/questions)          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 5. COMPLIANCE AGENT                                     │
│    - Validates against syllabus                         │
│    - Checks Bloom levels                                │
│    - Verifies rules                                     │
│    Output: Validated content or rejection              │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 6. EVALUATION METRICS                                   │
│    - Calculates quality scores                          │
│    - Measures coverage                                  │
│    Output: Metrics dict                                │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│ 7. RESULTS DISPLAY                                      │
│    - Formats output                                     │
│    - Shows in UI                                        │
│    - Provides download                                  │
└─────────────────────────────────────────────────────────┘
```

## 💻 Code Structure Details

### Configuration Layer
**Files:** `config/settings.py`, `config/constants.py`

**Purpose:** Centralized configuration

**Settings Include:**
- API keys and provider selection
- LLM model configuration
- RAG parameters (chunk size, overlap, top_k)
- Academic calendar settings
- File paths

**How to Update:**
- Edit `config/settings.py` for API/model settings
- Edit `config/constants.py` for academic constants
- Update JSON files in `data/` for rubrics/exam patterns

### Utility Layer
**Files:** `utils/*.py`

**Components:**
- `llm_client.py` - Unified LLM interface (Groq/OpenAI)
- `evaluators.py` - Metric calculation functions
- `helpers.py` - Helper utilities (file I/O, formatting)

**Purpose:** Reusable utilities across the system

### UI Components
**File:** `ui/components.py`

**Functions:**
- `display_syllabus_summary()` - Show syllabus info
- `display_teaching_plan()` - Show lesson plan
- `display_questions()` - Show generated questions
- `display_compliance_results()` - Show validation
- `display_metrics()` - Show quality metrics

**Purpose:** Reusable UI display functions

## 🔑 Key Design Patterns

### 1. Agent Pattern
Each agent is a class with:
- `__init__()` - Initialization with dependencies
- Main method(s) - Core functionality
- Convenience function - Simple interface

Example:
```python
class IntentAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def extract_intent(self, user_input):
        # Implementation
        pass

# Convenience function
def intent_agent(user_input, llm_client=None):
    agent = IntentAgent(llm_client)
    return agent.extract_intent(user_input)
```

### 2. RAG Pattern
Three-step process:
1. **Ingest** - Load and chunk documents
2. **Index** - Build vector store
3. **Retrieve** - Search for relevant chunks

### 3. Orchestrator Pattern
Central controller that:
- Manages agent lifecycle
- Coordinates execution flow
- Handles errors
- Saves results

### 4. Validation Pattern
Guardrails check:
- Before generation (input validation)
- After generation (output validation)
- Batch validation for multiple items

## 📝 How Each Component Works

### RAG Pipeline

**Step 1: Ingestion** (`rag/ingest.py`)
```python
chunks = ingest_syllabus("data/syllabus/sample_syllabus.txt")
# Returns: List of chunk dicts with text and metadata
```

**Step 2: Index Building** (`rag/vector_store.py`)
```python
store = RAGVectorStore()
store.build_index(chunks)
store.save_index()
# Creates: rag_index.faiss and chunks.pkl
```

**Step 3: Retrieval** (`rag/retriever.py`)
```python
retriever = RAGRetriever()
chunks = retriever.retrieve("search algorithms", top_k=5)
# Returns: Most relevant chunks
```

### Agent Execution

**Example: Lesson Planner Agent**

1. **Input:** Syllabus dict, number of weeks
2. **Process:**
   - Prepares syllabus context
   - Calls LLM with structured prompt
   - Parses JSON response
   - Validates structure
3. **Output:** Lesson plan dict with weekly schedule

### Compliance Checking

**Process:**
1. Extract content text
2. Check syllabus boundaries (via LLM)
3. Validate Bloom levels (keyword matching)
4. Check exam patterns (rule-based)
5. Aggregate results

### Metrics Calculation

**Process:**
1. Extract relevant data from content
2. Calculate individual metrics:
   - Bloom alignment (verb matching)
   - Coverage (topic intersection)
   - Difficulty balance (std deviation)
   - Explainability (heuristics)
3. Return aggregated scores

## 🎯 Integration Points

### Where Components Connect

1. **Orchestrator → Agents**
   - Orchestrator initializes all agents
   - Passes data between agents
   - Manages agent execution order

2. **Agents → RAG**
   - Agents use RAGRetriever to get context
   - RAG provides syllabus-relevant chunks

3. **Agents → LLM**
   - All agents use LLMClient
   - Unified interface for Groq/OpenAI

4. **UI → Orchestrator**
   - UI calls run_workflow()
   - Orchestrator returns results
   - UI displays formatted output

5. **Compliance → All Agents**
   - Validates output from content agents
   - Rejects non-compliant content

## 🔧 Extension Points

### Adding New Agent

1. Create `agents/new_agent.py`:
```python
class NewAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    def process(self, input_data):
        # Implementation
        pass
```

2. Add to orchestrator:
```python
from agents.new_agent import NewAgent

class Orchestrator:
    def __init__(self):
        self.new_agent = NewAgent(self.llm_client)
```

3. Use in workflow:
```python
result = self.new_agent.process(data)
```

### Adding New Validation

In `ComplianceAgent`:
```python
def _check_custom_rule(self, content):
    # Custom validation logic
    return {"status": "PASS/FAIL", "issue": "..."}
```

### Adding New Metric

In `utils/evaluators.py`:
```python
def calculate_custom_metric(content):
    # Calculate metric
    return score
```

## 📊 Data Structures

### Intent Structure
```python
{
    "tasks": ["teaching_plan", "questions"],
    "subject": "Data Structures",
    "exam_type": "mid",
    "units": ["Unit-1", "Unit-2"],
    "weeks": 16
}
```

### Syllabus Structure
```python
{
    "subject": "Data Structures",
    "course_code": "CS301",
    "credits": 3,
    "units": [
        {
            "unit_number": 1,
            "unit_name": "Introduction",
            "topics": ["Arrays", "Linked Lists"],
            "hours": 10,
            "learning_outcomes": [...]
        }
    ]
}
```

### Lesson Plan Structure
```python
{
    "subject": "Data Structures",
    "total_weeks": 16,
    "weeks": [
        {
            "week_number": 1,
            "topics": ["Arrays"],
            "hours": 3,
            "learning_objectives": [...],
            "teaching_methods": ["lecture"]
        }
    ]
}
```

### Question Structure
```python
{
    "exam_type": "mid",
    "questions": [
        {
            "question_number": 1,
            "question": "Explain array data structure",
            "bloom_level": "Understand",
            "marks": 5,
            "unit": "Unit-1",
            "topic": "Arrays"
        }
    ]
}
```

## 🚀 Execution Flow Summary

1. **Setup Phase:**
   - Install dependencies
   - Set API key
   - Place syllabus
   - Build RAG index

2. **Runtime Phase:**
   - Start Streamlit app
   - User enters request
   - Orchestrator executes workflow
   - Results displayed

3. **Output Phase:**
   - Generated content shown
   - Metrics displayed
   - Download option available
   - Results saved to logs

---

This architecture ensures:
- ✅ Modularity (each component independent)
- ✅ Scalability (easy to add agents/features)
- ✅ Maintainability (clear separation of concerns)
- ✅ Testability (components can be tested independently)

