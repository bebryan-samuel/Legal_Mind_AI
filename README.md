# ⚖️ LegalMind AI

### 🇮🇳 AI-Powered Constitutional Research Assistant

LegalMind AI is a **Retrieval-Augmented Generation (RAG)** based legal research assistant designed to answer questions using the **Constitution of India** as its primary knowledge source.

The project combines:

* 📄 Constitution of India PDF
* 🔎 Hybrid document retrieval
* 🧠 Hugging Face embeddings
* 🗂️ FAISS vector database
* 🔤 BM25 keyword retrieval
* 🤖 Qwen3-8B through the Hugging Face Inference API
* 🎨 Streamlit frontend

The main goal is to build a system that can retrieve the relevant constitutional provisions and generate an answer based on the retrieved content rather than relying only on the language model's internal knowledge.

> ⚠️ **Disclaimer:** LegalMind AI is intended for educational and legal research purposes. It is not a substitute for professional legal advice.

---

# 🏗️ Project Architecture

```text
                    ┌──────────────────────────┐
                    │       User Question      │
                    │  "What does Article 21   │
                    │       guarantee?"        │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Streamlit Frontend    │
                    │         app.py           │
                    └────────────┬─────────────┘
                                 │
                                 │
                     CURRENTLY NOT CONNECTED
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Backend / RAG       │
                    │        project.py        │
                    └────────────┬─────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
        ┌──────────────────┐          ┌──────────────────┐
        │  FAISS Semantic  │          │ BM25 Keyword     │
        │     Search       │          │     Search       │
        └────────┬─────────┘          └────────┬─────────┘
                 │                             │
                 └──────────────┬──────────────┘
                                ▼
                    ┌──────────────────────────┐
                    │   Hybrid Retrieval       │
                    │  + Article Detection     │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Relevant Context      │
                    │ Constitution of India    │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Qwen3-8B            │
                    │ Hugging Face Inference   │
                    │          API             │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     Generated Answer     │
                    │  + Source Pages          │
                    └──────────────────────────┘
```

---

# 📂 Project Structure

```text
LegalMind AI/
│
├── app.py
├── project.py
├── requirements.txt
├── README.md
├── .env
│
├── coi/
│   └── constitution_of_india.pdf
│
└── .venv/
```

---

# 🧩 Components

## 🎨 Frontend — `app.py`

The Streamlit frontend provides the user interface for LegalMind AI.

It includes:

* ⚖️ LegalMind AI dashboard
* 🔎 Constitutional question input
* 📚 Example questions
* 🤖 Model information
* 🟢 System status
* 📄 Retrieved constitutional sources
* 💬 AI-generated answer display
* ⚠️ Legal disclaimer

Example questions include:

```text
What does Article 21 guarantee?
```

```text
What does Article 14 provide?
```

```text
What are the constitutional provisions regarding citizenship?
```

### Current Status

The Streamlit frontend is currently developed separately from the RAG backend.

The developer will connect:

```text
app.py
   ↓
project.py
```

so that the frontend can directly call the backend's question-answering function.

---

# 🧠 Backend — `project.py`

`project.py` contains the main RAG pipeline.

It is responsible for:

1. Loading the Constitution PDF
2. Splitting the document into chunks
3. Creating embeddings
4. Creating the FAISS vector database
5. Creating the BM25 keyword retriever
6. Detecting constitutional article references
7. Performing hybrid retrieval
8. Building the legal context
9. Sending the context to Qwen3-8B
10. Generating the final answer
11. Returning the retrieved sources

---

# 🔄 RAG Flow

The complete backend flow is:

```text
Constitution PDF
       │
       ▼
PyPDFLoader
       │
       ▼
Document Pages
       │
       ▼
Text Splitting
       │
       ▼
1075+ Document Chunks
       │
       ├──────────────────┐
       ▼                  ▼
Hugging Face         BM25 Retriever
Embeddings                │
       │                  │
       ▼                  │
FAISS Vector Store        │
       │                  │
       └────────┬─────────┘
                ▼
       Hybrid Retrieval
                │
                ▼
       Article Detection
                │
                ▼
       Relevant Documents
                │
                ▼
          Context
                │
                ▼
          Legal Prompt
                │
                ▼
          Qwen3-8B
                │
                ▼
        Generated Answer
                │
                ▼
      Answer + Sources
```

---

# 🔎 1. PDF Loading

The Constitution of India PDF is loaded using `PyPDFLoader`.

```text
coi/constitution_of_india.pdf
```

The PDF is converted into document objects containing:

* Page content
* Page metadata

---

# ✂️ 2. Document Chunking

The Constitution is split into smaller chunks using:

```text
RecursiveCharacterTextSplitter
```

Current configuration:

```text
Chunk Size:     1100
Chunk Overlap:  200
```

This allows the retrieval system to search smaller, relevant sections instead of processing the entire Constitution for every question.

---

# 🧠 3. Embeddings

LegalMind AI uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

to convert text into numerical vectors.

These vectors allow the system to perform semantic similarity searches.

For example:

```text
"What protection does a person have regarding life?"
```

can retrieve a passage containing:

```text
"Protection of life and personal liberty"
```

even though the wording is different.

---

# 🗂️ 4. FAISS

FAISS is used for semantic vector search.

```text
Question
   ↓
Embedding
   ↓
FAISS similarity search
   ↓
Relevant constitutional chunks
```

The backend currently retrieves multiple candidates using FAISS.

---

# 🔤 5. BM25

BM25 provides keyword-based retrieval.

This is particularly useful for legal questions containing exact references such as:

```text
Article 21
Article 14
Article 32
citizenship
fundamental rights
```

For example:

```text
"What does Article 21 guarantee?"
```

BM25 can prioritize chunks containing the exact term:

```text
21. Protection of life and personal liberty.
```

---

# 🔀 6. Hybrid Retrieval

LegalMind AI combines:

```text
FAISS
+
BM25
+
Legal Article Detection
```

This improves retrieval compared with relying on semantic search alone.

The system first performs:

```text
Semantic Search
```

and:

```text
Keyword Search
```

Then it combines the results and removes duplicates.

---

# ⚖️ 7. Article Detection

The backend detects questions containing constitutional article numbers.

For example:

```text
What does Article 21 guarantee?
```

is detected as:

```text
Article: 21
```

The system then searches the document chunks specifically for Article 21 and places those matches at the beginning of the retrieved results.

This is important because legal questions often depend on exact provisions.

---

# 📚 8. Context Construction

After retrieval, the best results are selected.

The relevant document chunks are combined into a context:

```text
Retrieved Constitution Content
          ↓
        Context
```

This context is passed to the language model.

---

# 🤖 9. Qwen3-8B

The generation model currently used is:

```text
Qwen/Qwen3-8B
```

The model is accessed through the **Hugging Face Inference API**.

The model receives:

```text
System Instructions
+
Retrieved Constitution Context
+
User Question
```

The model is instructed to answer only from the provided constitutional context.

---

# 🛡️ 10. Grounded Answer Generation

The prompt instructs the model:

```text
Answer ONLY using the provided Constitution context.

Do not invent Articles, provisions, cases, or facts.
```

If sufficient information cannot be found, the model should respond:

```text
I could not find sufficient information in the provided Constitution.
```

This helps reduce hallucination in legal research.

---

# 📄 11. Sources

After generating the answer, LegalMind AI displays the retrieved Constitution pages.

Example:

```text
========== SOURCES ==========

Source 1:
Constitution of India - Page 42

Source 2:
Constitution of India - Page 5
```

The Streamlit frontend will eventually display these sources in expandable sections.

---

# 🔌 Frontend ↔ Backend Integration

## Current State

At the moment:

```text
app.py       → Frontend
project.py   → Backend
```

They are **not fully integrated yet**.

The Streamlit UI already expects the backend to provide:

```python
response, results = project.ask_question(question)
```

The developer will connect the backend accordingly.

### Planned Integration

The final flow will be:

```text
User
 │
 ▼
Streamlit UI
 │
 │ question
 ▼
project.ask_question()
 │
 ▼
Hybrid RAG Pipeline
 │
 ├── FAISS
 ├── BM25
 ├── Article Detection
 └── Context Construction
 │
 ▼
Qwen3-8B
 │
 ▼
Answer + Sources
 │
 ▼
Streamlit UI
```

Once connected, the user will not need to interact with `project.py` directly.

---

# 🚀 Running the Project

## 1. Create Virtual Environment

Windows PowerShell:

```powershell
py -3.13 -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 3. Configure Hugging Face

Create:

```text
.env
```

Add:

```text
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

Do not commit `.env` to GitHub.

---

# ▶️ Run Backend

The current backend can be tested using:

```powershell
python project.py
```

It will ask:

```text
Ask your question:
```

Example:

```text
What does Article 21 guarantee?
```

---

# 🎨 Run Streamlit Frontend

After frontend/backend integration:

```powershell
python -m streamlit run app.py
```

Streamlit will open the LegalMind AI interface in your browser.

---

# 📦 Requirements

The project currently uses:

```text
streamlit
langchain-huggingface
langchain-community
langchain-text-splitters
faiss-cpu
sentence-transformers
pypdf
python-dotenv
rank-bm25
huggingface-hub
```

---

# 🛠️ Technology Stack

| Component       | Technology                         |
| --------------- | ---------------------------------- |
| Frontend        | Streamlit                          |
| Backend         | Python                             |
| RAG Framework   | LangChain                          |
| PDF Processing  | PyPDF                              |
| Text Splitting  | RecursiveCharacterTextSplitter     |
| Embeddings      | Hugging Face Sentence Transformers |
| Vector Database | FAISS                              |
| Keyword Search  | BM25                               |
| LLM             | Qwen3-8B                           |
| LLM Provider    | Hugging Face Inference API         |
| Knowledge Base  | Constitution of India              |
| Environment     | Python Virtual Environment         |

---

# 🎯 Current Development Status

### ✅ Completed

* [x] Constitution PDF ingestion
* [x] PDF page extraction
* [x] Document chunking
* [x] Hugging Face embeddings
* [x] FAISS vector search
* [x] BM25 keyword search
* [x] Hybrid retrieval
* [x] Article number detection
* [x] Citizenship query detection
* [x] Qwen3-8B integration
* [x] Hugging Face Inference API
* [x] Constitutional context-based prompting
* [x] Streamlit frontend
* [x] Source display UI

### 🔄 In Progress

* [ ] Connect Streamlit frontend with RAG backend
* [ ] Expose `ask_question()` backend function
* [ ] Improve retrieval ranking
* [ ] Improve legal answer formatting
* [ ] Improve citation handling
* [ ] Add more Indian legal documents
* [ ] Add conversation history
* [ ] Add advanced legal search

---

# 🔮 Future Improvements

Possible future versions can include:

### 📚 Expanded Legal Knowledge Base

```text
Constitution
    +
Supreme Court Judgments
    +
High Court Judgments
    +
Acts
    +
Rules
    +
Government Notifications
```

### 🔎 Advanced Legal Search

Users could search for:

```text
Articles
Sections
Acts
Judgments
Cases
Legal concepts
```

### 💬 Conversational Legal Assistant

Instead of asking one question at a time:

```text
User:
What does Article 21 provide?

AI:
Article 21 protects life and personal liberty...

User:
Does this apply to foreigners?

AI:
Based on the available constitutional context...
```

---

# ⚠️ Legal Disclaimer

LegalMind AI is an experimental AI-based legal research system.

It is designed to assist with:

* Constitutional research
* Educational purposes
* Document retrieval
* Legal information exploration

It should **not** be relied upon as a replacement for a qualified lawyer or professional legal advice.

Always verify important legal information against the authoritative legal source and seek professional legal advice where appropriate.

---

# 👨‍💻 Development

LegalMind AI is being developed as a modular system where the:

```text
Frontend
```

and

```text
Backend / RAG Engine
```

can be developed independently and connected through a clean interface.

The immediate integration target is:

```python
response, results = project.ask_question(question)
```

This allows the Streamlit application to remain focused on the UI while `project.py` handles the complete RAG and LLM pipeline.
