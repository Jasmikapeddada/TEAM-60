# 🎓 AI Teaching Assistant for Faculty  
### Agentic RAG-based Auto Planning & Auto Assessment System

## 📌 Problem Statement

Faculty members spend a significant amount of time on manual academic tasks such as syllabus analysis, lesson planning, question paper creation, and student answer evaluation.  
Existing AI tools act like generic chatbots and **do not enforce syllabus boundaries, Bloom’s taxonomy, exam patterns, or academic compliance**, making them unsuitable for real academic workflows.

---

## 💡 Solution Overview

This project presents an **Agentic AI Teaching Assistant** that automates:

- 📘 Lesson planning from syllabus
- 📝 Question paper generation aligned with Bloom’s Taxonomy
- 📊 Student answer evaluation with explainable feedback

The system is built using **LLMs + Retrieval Augmented Generation (RAG) + Guardrails + Multi-Agent Architecture**, ensuring academic correctness, transparency, and compliance.

---

## 🏗️ System Architecture


![Architecture Diagram]("C:\Users\Neelam Sirisha\OneDrive\Pictures\Screenshots\Screenshot 2025-12-13 151746.png")


---

## 🧠 Agent Roles

### 1️⃣ Orchestrator Agent
- Controls execution flow
- Manages inter-agent communication
- Logs evaluation metrics

### 2️⃣ Syllabus Understanding Agent
- Extracts units, topics, learning outcomes
- Converts syllabus PDF into structured JSON

### 3️⃣ Lesson Planner Agent
- Allocates topics across academic weeks
- Ensures balanced syllabus coverage

### 4️⃣ Assessment Generator Agent
- Generates questions per Bloom’s level
- Follows exam pattern rules
- Avoids repetition and difficulty imbalance

### 5️⃣ Evaluation Agent
- Scores student answers using rubrics
- Provides explainable feedback
- Highlights missing concepts

### 6️⃣ Compliance Agent (Guardrails)
- Prevents out-of-syllabus content
- Enforces Bloom’s taxonomy balance
- Rejects or regenerates invalid outputs

---

## 📚 RAG Pipeline

1. **Document Ingestion**
   - Syllabus PDF → Text → Chunks (500–700 tokens)
   - Embeddings stored in FAISS Vector DB

2. **Contextual Retrieval**
   - Retrieves syllabus-relevant chunks only
   - Filters by unit, topic, and Bloom level

3. **Grounded Generation**
   - LLM generates outputs strictly from retrieved context

---

## 🛡️ Guardrails

### Hard Guardrails
- Syllabus-only content generation
- Exam pattern enforcement
- Bloom distribution limits

### Soft Guardrails
- Difficulty balancing
- Topic diversity
- No repeated verbs or questions

---

## 📊 Evaluation Metrics

| Metric | Description |
|------|------------|
| Bloom Alignment Score | Match between intended and generated Bloom level |
| Coverage Completeness | Topics covered vs total syllabus |
| Difficulty Balance | Standard deviation across questions |
| Explainability Score | Quality of feedback provided |

---

## 🖥️ Streamlit UI Flow

1. **Upload Page**
   - Upload syllabus PDF
   - Select subject and output type

2. **Generation Page**
   - Displays agent execution status
   - Shows intermediate outputs

3. **Results Page**
   - Lesson plan table
   - Generated question paper
   - Bloom’s taxonomy distribution chart
   - Evaluation feedback

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| UI | Streamlit |
| Agents | LangChain / CrewAI |
| LLM | Groq / OpenAI |
| Embeddings | SentenceTransformers |
| Vector DB | FAISS |
| Backend | Python |

---

## 🎯 Key Highlights

* Not a chatbot — a **rule-enforced academic AI system**
* Fully **syllabus-grounded using RAG**
* **Multi-agent reasoning** with compliance checks
* Designed for **government universities**
* Hackathon-ready & scalable

---

## 🎤 One-Line Pitch

> “An agentic, syllabus-grounded AI Teaching Assistant that automates academic planning and assessment while enforcing Bloom’s taxonomy, exam rules, and compliance — something a normal chatbot cannot do.”

---

## 🔮 Future Enhancements

* LMS integration
* Multilingual syllabus support
* Department-level analytics dashboard
* Adaptive learning recommendations
