# 📘 Automated RAG with Metadata Tagging
*A retrieval-augmented question lookup system with structured metadata tagging, built using Google Vertex AI RAG + ADK.*

---

## ⭐ Overview

This project implements an **end-to-end Retrieval-Augmented Generation (RAG)** system that stores exam questions with **metadata tags** and retrieves them intelligently using:

- **Free-text search**  
- **Concept-based search**  
- **Question ID lookup**

The system uses:

- **Vertex AI RAG Corpus**  
- **Google Cloud Storage**  
- **Metadata normalization + tagging**  
- **Custom RAG retrieval tools**  
- **ADK Web Interface**  

It is designed for a future larger system where teachers can upload questions, match them to concepts, and retrieve them instantly.

---

## 🧩 Architecture Summary

```mermaid
flowchart TD
    A[Teacher JSON (questions & matches)] --> B[Normalization<br>metadata_input.json → normalized_metadata.json]
    B --> C[Corpus Text Builder<br>(metadata_tagging_file.txt)]
    C --> D[Upload to Google Cloud Storage]
    D --> E[Reimport to Vertex RAG Corpus]
    E --> F[RAG Search Engine]

    F --> G1[Search by Text]
    F --> G2[Search by Concept]
    F --> G3[Search by Question ID]

    G1 --> H[ADK Web Agent UI]
    G2 --> H
    G3 --> H
```

---

## 📁 Project Structure

```
Automated_RAG/
│
├── question_rag/
│   ├── agent.py                     # ADK Agent (root agent)
│   ├── config.py                    # Project, bucket, corpus info
│   ├── ingestion.py                 # Full ingestion pipeline
│   ├── metadata_tagging_file.txt    # Auto-generated RAG file
│   ├── input/
│   │   ├── metadata_input.json      # Teacher raw input
│   │   └── normalized_metadata.json # Auto-normalized metadata
│   ├── agents/
│   │   ├── retrieval_tools.py       # RAG search helpers
│   │   └── retrieval_agent_system_prompt.txt
│   └── rag_retrieval_test.py        # Test retrieval script
```

---

# 🚀 Features

### 🔍 Intelligent Question Retrieval

Retrieve questions by:

#### **1. Free-text**
```
"strategic risks SSBR"
```

#### **2. Concept**
```
"Corporate Governance"
```

#### **3. Question ID**
```
"q_005"
```

All work instantly inside ADK Web UI.

---

### 🧠 Metadata Tagging Format

Questions are stored in RAG using a structured block:

```
[ID: q_001]
[MAIN_CONCEPT: Partnerships]
[CONCEPTS: Partnerships; Corporate Income; Tax]

Actual question text...

---
```

This ensures:
- Traceability  
- Filtering  
- Clean structured retrieval  

---

# 📦 Ingestion Workflow

Run the full ingestion (recommended):

```
py -m question_rag.ingestion
```

Pipeline steps:

1. Load `input/metadata_input.json`
2. Normalize → `normalized_metadata.json`
3. Build `metadata_tagging_file.txt`
4. Upload file to GCS
5. Import file into Vertex RAG corpus

Output example:

```
[INGEST] Uploaded corpus file to gs://<bucket>/metadata_tagging_file.txt
[INGEST] RAG import request sent.
=== Ingestion complete ===
```

---

# 🔍 Retrieval Testing

### 1️⃣ CLI Test (Basic)
```
py question_rag/rag_retrieval_test.py
```

### 2️⃣ ADK Agent Load Test
```
py -c "from question_rag.agent import root_agent; print(root_agent.name)"
```

### 3️⃣ ADK Web UI
Start:

```
adk web
```

Visit:

```
http://127.0.0.1:8000
```

Select app:
```
question_rag
```

Try queries:

- “strategic risks”
- “capital allowances”
- “q_003”

---

# 🔄 How New Data Works

### ✔ When new data is added:
Only modify:

```
input/metadata_input.json
```

### ✔ The ingestion pipeline **automatically overwrites**:
- normalized_metadata.json  
- metadata_tagging_file.txt  
- RAG corpus contents  

### ❗ No duplication  
The system always regenerates metadata (clean & controlled).

---

# 🧪 Example RAG Output

```json
{
  "id": "q_001",
  "main_concept": "Corporate Governance",
  "concepts": ["Corporate Governance", "Tax", "Income"],
  "text": "Identify and explain strategic risks...",
  "score": 0.23
}
```

---

# 🧑‍💻 Technologies Used

- Python 3.10+
- Google Vertex AI RAG
- Google Cloud Storage
- Google ADK
- Gemini 2.5 Pro

---

# 📌 Summary for Supervisor

This prototype demonstrates:

✔ A real working RAG ingestion pipeline  
✔ Metadata tagging system  
✔ Clean parsing + normalization  
✔ Concept and ID-based filtering  
✔ A working Agent in ADK Web  
✔ Fully cloud-integrated system  

This forms the foundation for:
- A question generator
- Multi-agent system
- LMS or classroom tool
- Automated ingestion from CSV/Sheets

---

# 📄 License
MIT License  
© 2025 Automated RAG with Metadata Tagging

