# 📄 RAG Document Q&A Chatbot

An AI-powered document question answering system built with Python. Upload any PDF and ask questions — the AI answers using only your document's content, preventing hallucination.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![LangChain](https://img.shields.io/badge/LangChain-Community-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-orange)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-purple)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![Free](https://img.shields.io/badge/API-Free_Tier-brightgreen)

---

## 🚀 Demo

Upload a PDF → Ask questions → Get grounded answers instantly.

If the answer is not in the document, the AI says **"I don't know"** — no hallucination.

---

## 🧠 What It Does

- Accepts any PDF document via web interface
- Splits document into semantic chunks
- Converts chunks to vector embeddings (locally, no API)
- Stores embeddings in a persistent ChromaDB vector database
- On every question, retrieves only the most relevant chunks
- Sends retrieved chunks + question to Groq LLM for grounded answers
- Prevents hallucination by grounding answers strictly in document content

---

## 🏗️ Architecture — RAG Pipeline

```
INDEXING (runs once per PDF upload)
PDF → PyPDFLoader → RecursiveTextSplitter → SentenceTransformer → ChromaDB

QUERYING (runs on every question)
Question → SentenceTransformer → ChromaDB Search → Groq LLM → Answer
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| LangChain | Document loading and text splitting |
| sentence-transformers | Local embedding generation (all-MiniLM-L6-v2) |
| ChromaDB | Persistent vector database |
| Groq API | LLM inference (free tier) |
| Llama 3.1 8B | Language model |
| Streamlit | Web UI |

---

## 📁 Project Structure

```
rag-document-qa/
│
├── index.py        # Indexing pipeline — runs once per PDF
├── query.py        # Query pipeline — runs on every question
├── app.py          # Streamlit UI layer
├── .env            # API key (not committed)
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/your-username/rag-document-qa.git
cd rag-document-qa
```

### 2. Install dependencies
```bash
pip install groq streamlit langchain-community langchain-text-splitters sentence-transformers chromadb python-dotenv pypdf
```

### 3. Get a free Groq API key
- Sign up at [console.groq.com](https://console.groq.com)
- Create an API key (free, no credit card)

### 4. Add your API key
Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## 💡 Key Engineering Decisions

**Why separate index.py and query.py?**
Indexing is expensive — reading, chunking, and embedding a PDF only needs to happen once. Separating indexing from querying means users get instant answers without re-processing the document on every question.

**Why all-MiniLM-L6-v2?**
Lightweight 384-dimensional embedding model that runs locally with no API cost. Excellent speed-accuracy tradeoff for semantic search tasks.

**Why ChromaDB PersistentClient?**
In-memory databases are lost when the program ends. PersistentClient saves the vector database to disk so the index survives between sessions.

**Why "I don't know" grounding?**
A single instruction in the system prompt prevents the LLM from hallucinating answers not found in the document — critical for production document Q&A systems.

---

## 🔮 Coming Soon

- [ ] Multi-PDF support
- [ ] Re-indexing on document update with version detection
- [ ] AI Agents
- [ ] Fine-tuning

---

## 📄 License

MIT License — free to use and modify.
