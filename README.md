# 🎓 AI Teaching Assistant for Faculty

### Agentic RAG-based Auto Planning & Auto Assessment System

---

## 📌 Problem Context (Why This Solution?)

In real academic environments, faculty members spend a significant amount of time on **manual, repetitive, and regulation-heavy tasks**, such as:

* Analyzing large syllabus PDFs (40–60 pages)
* Planning weekly lesson schedules
* Designing question papers aligned with **Bloom’s Taxonomy**
* Evaluating student answers using structured rubrics

### Why Existing AI Tools Fail

Generic AI chatbots:

* ❌ Hallucinate topics outside syllabus
* ❌ Ignore Bloom’s taxonomy
* ❌ Do not follow exam patterns
* ❌ Provide no academic compliance guarantees

👉 **Academic workflows require controlled, verifiable, and syllabus-grounded intelligence — not a chatbot.**

---

## 💡 Proposed Solution

We built an **Agentic AI Teaching Assistant** that behaves like a **digital academic assistant**, not a conversational bot.

### What Makes It Different

* ✅ Strictly syllabus-grounded using **RAG (Retrieval-Augmented Generation)**
* ✅ Enforces **Bloom’s Taxonomy** and exam rules
* ✅ Uses **multiple specialized agents** for reliability
* ✅ Validates output through a **Compliance Agent**
* ✅ Fully explainable and auditable

---

## 🧠 High-Level System Workflow

```
Faculty Input
   ↓
Orchestrator (Controller)
   ↓
Intent Understanding Agent
   ↓
RAG (Syllabus Retrieval)
   ↓
Academic Content Agents
   ↓
Compliance & Validation Agent
   ↓
Final Output to Faculty
```

Each step is independently verified, ensuring **trustworthy academic output**.

---

## 🏗️ System Architecture

### Core Design Principles

* One agent = one academic responsibility
* Agents do NOT talk directly to each other
* Orchestrator controls execution flow
* RAG is the **single source of truth**

### Architecture Overview

```
UI (Streamlit)
   ↓
Orchestrator Agent
   ↓
┌──────────────┬──────────────┬──────────────┐
│ Intent Agent │ Syllabus RAG │ Content Agents│
└──────────────┴──────────────┴──────────────┘
   ↓
Compliance Agent
   ↓
Final Output + Metrics
```

---

## 📚 RAG Pipeline (Why Outputs Are Trustworthy)

### Step 1: Document Ingestion

* Input: Syllabus PDF / TXT
* Text extraction
* Chunking (500–700 tokens with overlap)
* Metadata tagging (unit, topic)

### Step 2: Vector Storage

* Embeddings: `SentenceTransformers (all-MiniLM-L6-v2)`
* Vector DB: **FAISS**

### Step 3: Context Retrieval

* Query-based semantic search
* Retrieves only **relevant syllabus chunks**

### Step 4: Grounded Generation

* LLM generates content using **retrieved context only**
* No retrieved context → No generation

👉 This eliminates hallucinations completely.

---

## 🤖 Multi-Agent Architecture

### 1️⃣ Intent Understanding Agent

**Purpose:**

* Converts faculty natural language into structured intent

**Output Example:**

```json
{
  "tasks": ["lesson_plan", "question_paper"],
  "units": ["Unit-2"],
  "weeks": 6,
  "bloom_levels": ["Understand", "Apply"]
}
```

---

### 2️⃣ Orchestrator Agent

**Purpose:**

* Central controller
* Decides which agents to invoke
* Maintains execution order and logs

❌ No content generation

---

### 3️⃣ Syllabus Understanding Agent

**Purpose:**

* Converts syllabus text into structured JSON

**Extracts:**

* Units
* Topics
* Learning Outcomes

Acts as the **academic source of truth**.

---

### 4️⃣ Lesson Planner Agent

**Purpose:**

* Allocates syllabus topics week-wise
* Balances workload
* Prevents topic overload

---

### 5️⃣ Assessment Generator Agent

**Purpose:**

* Generates questions based on Bloom’s Taxonomy
* Enforces exam patterns

**Guarantees:**

* No repetition
* Balanced difficulty
* Syllabus-only questions

---

### 6️⃣ Evaluation Agent

**Purpose:**

* Rubric-based student answer evaluation

**Outputs:**

* Marks
* Strengths
* Weak areas
* Improvement suggestions

---

### 7️⃣ Compliance Agent (Critical Safety Layer)

**Purpose:**

* Validates all generated content

**Checks:**

* Syllabus boundaries
* Bloom distribution
* Exam rule violations

**Behavior:**

* PASS → Output shown
* FAIL → Regeneration triggered

👉 Enables **institution-level trust**.

---

## 🔄 Agent Communication Pattern

* Agents never talk directly
* Orchestrator mediates all data flow

```
User Input
   ↓
Intent Agent
   ↓
Orchestrator
   ↓
Syllabus Agent (RAG)
   ↓
Content Agent (RAG)
   ↓
Compliance Agent
   ↓
Final Output
```

---

## 📊 Quality Metrics

| Metric             | Description            |
| ------------------ | ---------------------- |
| Bloom Alignment    | Bloom verb correctness |
| Coverage Score     | % of syllabus covered  |
| Difficulty Balance | Even distribution      |
| Explainability     | Feedback clarity       |

---

## 🖥️ Streamlit Application Flow

1. Upload syllabus
2. Select output type
3. Live agent execution
4. View validated results
5. Download outputs

---

## 🛠️ Technology Stack

| Layer      | Technology               |
| ---------- | ------------------------ |
| UI         | Streamlit                |
| Agents     | Python (Agentic Pattern) |
| LLM        | Groq / OpenAI            |
| Embeddings | SentenceTransformers     |
| Vector DB  | FAISS                    |

---

## 🎯 Key Differentiators

✔ Not a chatbot
✔ Fully syllabus-grounded (RAG)
✔ Multi-agent academic reasoning
✔ Deterministic compliance checks
✔ University-ready design

---

## 🎤 One-Line Pitch (For Jury)

> "An agentic, syllabus-grounded AI Teaching Assistant that automates academic planning and assessment while enforcing Bloom’s taxonomy, exam rules, and compliance — something a normal chatbot cannot do."

---

## 🔮 Future Scope

* LMS integration
* Multilingual syllabus support
* Department-level analytics
* Adaptive learning recommendations

---

✅ **This system transforms academic workflows from manual, error-prone processes into a safe, intelligent, and scalable AI-driven pipeline.**
