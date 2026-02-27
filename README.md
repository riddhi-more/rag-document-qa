# RAG Document Intelligence System

A Retrieval Augmented Generation (RAG) system that answers questions from your own documents using semantic search and vector storage. Prevents hallucination by grounding every answer strictly in retrieved source content.

## What It Does

Upload any document. Ask questions in plain language. Get accurate answers sourced directly from the document content — not from LLM training memory.

```
You:    "What are the steps in the process described in section 3?"
System: Searches all document chunks using semantic similarity
        Retrieves the 2 most relevant sections
        Generates a grounded answer from those sections only

Answer: "Based on the document, the process has four steps:
         Step 1: Initialise the configuration..."

Out of scope: "I don't know — this is not covered in the provided document."
```

## Why RAG Instead of Sending the Whole Document to the LLM?

| Problem | Without RAG | With RAG |
|---|---|---|
| Large documents | Exceed context window limits | Only relevant chunks sent |
| Private content | Cannot be included in LLM training | Stays in your vector database |
| Hallucination | LLM invents plausible-sounding answers | Grounded to retrieved content only |
| Cost | Sending full doc = very high token cost | Only top 2 chunks sent per query |
| Speed | 15+ seconds per query | Under 2 seconds per query |

## How It Works — Two Separate Pipelines

```
INDEXING PIPELINE — runs once per document
Document → PyPDFLoader → TextSplitter → all-MiniLM-L6-v2 → ChromaDB
           (read)         (1000 chars,    (embed into         (store on
                           200 overlap)    384 dimensions)     disk)

QUERY PIPELINE — runs on every question
Question → embed → ChromaDB search → top 2 chunks → LLM → grounded answer
           (same    (cosine           (inject into    (answer from
            model)   similarity)       prompt)         chunks only)
```

**Why two separate pipelines?**
Indexing is expensive and only needs to happen once per document. Running it on every query added 13 seconds of unnecessary processing. Separating the pipelines reduced query latency from 15 seconds to under 2 seconds.

## Semantic Search vs Keyword Search

```
Keyword search: "configuration error" finds ONLY pages with those exact words

Semantic search: "configuration error" also finds:
  → "setup failure detected"
  → "initialisation did not complete"
  → "system could not start"

Meaning is matched — not just words.
This is what makes RAG work across different phrasings of the same concept.
```

## Tech Stack

| Component | Development | Production Equivalent |
|---|---|---|
| LLM | Groq Llama 3.1 | Azure OpenAI GPT-4 |
| Embeddings | all-MiniLM-L6-v2 (local) | Azure OpenAI text-embedding-3-large |
| Vector DB | ChromaDB (local disk) | Pinecone / Azure AI Search |
| Document loading | LangChain PyPDFLoader | Azure Blob + Document Intelligence |
| Orchestration | LangChain | LangChain + Azure |

## Project Structure

```
rag-document-qa/
├── index.py           # indexing pipeline — run once per document
├── query.py           # query pipeline — run on every question
├── app.py             # Streamlit UI
├── chroma_db/         # persisted vector store (auto-created)
├── .env               # API keys (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. Clone and navigate
git clone <your-repo-url>
cd rag-document-qa

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install langchain langchain-community langchain-groq
pip install chromadb sentence-transformers pypdf streamlit python-dotenv

# 4. Create .env file
GROQ_API_KEY=your_key_here

# 5. Index your document first — only needed once
python index.py

# 6. Ask questions
python query.py
# or launch the UI
streamlit run app.py
```

## Key Engineering Decisions

**Why chunk_size=1000 with chunk_overlap=200?**
1000 characters gives the LLM enough context per chunk to answer completely. 200-character overlap prevents information loss at chunk boundaries — a sentence split across two chunks appears complete in at least one of them.

**Why all-MiniLM-L6-v2?**
384-dimensional embeddings trained on over 1 billion sentence pairs. Runs locally with zero API cost. Strong retrieval quality for technical and general documents. Production upgrade: Azure OpenAI text-embedding-3-large (3072 dimensions).

**Why ChromaDB with PersistentClient?**
Saves the vector index to disk so indexing only runs once. Without persistence the entire index is rebuilt from scratch on every run — defeating the purpose of separating the pipelines.

**Why answer "I don't know"?**
A hallucinated answer is worse than no answer. The system prompt instructs the LLM to answer only from retrieved context and explicitly say it does not know if the answer is not present. This eliminates confabulation for out-of-scope questions.

**Why top 2 chunks (k=2)?**
Balances context richness against token consumption and cost. Tuned against a representative set of test questions — more chunks did not improve answer quality enough to justify the additional token cost.

## Production Considerations

```
Document updates    → hash-based change detection, re-index only changed files
Access control      → document-level permissions in the vector database
Source citation     → every answer cites the source chunk and document name
Evaluation          → benchmark retrieval precision on curated Q&A test pairs
Hybrid search       → combine semantic + keyword search for improved recall
Monitoring          → track query latency, retrieval precision, abstention rate
```

## What Comes Next (Project 3)

Project 2 answers from documents. Project 3 adds an autonomous agent — the system can now search the live web, perform calculations, and chain multiple tools together in a single response without any explicit scripting.

## Skills Demonstrated

- RAG architecture with cleanly separated indexing and query pipelines
- Sentence transformer embeddings for semantic similarity search
- ChromaDB vector database with disk persistence
- Cosine similarity retrieval with configurable top-k
- Context grounding and hallucination prevention via system prompt
- Chunk size and overlap hyperparameter tuning
- Production upgrade path to Azure AI Search with hybrid retrieval
