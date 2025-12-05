# Technical Documentation: PDF RAG Q&A System

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (HTML/CSS/JS)                   │
│  - User Interface                                           │
│  - PDF Upload                                               │
│  - Question Input                                           │
│  - Chat Display                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP Requests
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ /api/upload │  │  /api/ask    │  │ /api/status  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
└─────────┼──────────────────┼───────────────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────┐  ┌──────────────────────────────────────┐
│  PDF Parser     │  │         RAG System                    │
│  - Extract text │  │  ┌──────────────────────────────────┐ │
│  - Split chunks │  │  │  1. Retrieve Relevant Chunks     │ │
│  - Page numbers │  │  │     (Vector Similarity Search)  │ │
└────────┬────────┘  │  └──────────────┬───────────────────┘ │
         │           │                 │                      │
         ▼           │                 ▼                      │
┌─────────────────┐ │  ┌──────────────────────────────────┐ │
│  Vector Store   │ │  │  2. Generate Embeddings          │ │
│  (ChromaDB)     │◄┼──┤     (OpenAI Embeddings API)      │ │
│  - Store        │ │  └──────────────┬───────────────────┘ │
│  - Query        │ │                 │                      │
└─────────────────┘ │                 ▼                      │
                    │  ┌──────────────────────────────────┐ │
                    │  │  3. Build Context                │ │
                    │  │     (Combine retrieved chunks)    │ │
                    │  └──────────────┬───────────────────┘ │
                    │                 │                      │
                    │                 ▼                      │
                    │  ┌──────────────────────────────────┐ │
                    │  │  4. Generate Answer               │ │
                    │  │     (OpenAI GPT-3.5-turbo)       │ │
                    │  └──────────────────────────────────┘ │
                    └────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **HTML/CSS/JavaScript**: Pure frontend, no framework
- **Features**: 
  - Drag-and-drop file upload
  - Real-time chat interface
  - Markdown rendering
  - Feedback buttons

### Backend
- **FastAPI**: Python web framework for API endpoints
- **Uvicorn**: ASGI server

### RAG Components
- **PDF Parsing**: PyPDF2 library
- **Vector Database**: ChromaDB (persistent vector store)
- **Embeddings**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **LLM**: OpenAI GPT-3.5-turbo

### Data Storage
- **Uploads**: Local file system (`uploads/` directory)
- **Vector DB**: ChromaDB persistent storage (`vector_db/` directory)

---

## RAG Pipeline: Step-by-Step

### Phase 1: Document Processing (Upload Time)

```
PDF File Upload
      │
      ▼
┌─────────────────────────────────────┐
│  PDF Parser (pdf_parser.py)        │
│                                     │
│  1. Read PDF pages                  │
│  2. Extract text from each page     │
│  3. Split text into chunks          │
│     (500 chars per chunk)           │
│  4. Add metadata:                   │
│     - page number                   │
│     - chunk index                   │
│     - PDF filename                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Generate Embeddings                │
│  (OpenAI text-embedding-3-small)    │
│                                     │
│  Input: Text chunks                 │
│  Output: 1536-dim vectors           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Vector Store (ChromaDB)            │
│                                     │
│  Store:                             │
│  - Document text                    │
│  - Embeddings (vectors)             │
│  - Metadata (page, filename, etc.)  │
└─────────────────────────────────────┘
```

**What is stored?**
- Text chunks (500 characters each)
- Embedding vectors (1536 dimensions)
- Metadata: `{pdf_filename, page, chunk_index, total_pages}`

---

### Phase 2: Question Answering (Query Time)

```
User Question: "What are the steps of data preprocessing?"
      │
      ▼
┌─────────────────────────────────────┐
│  Step 1: Generate Question Embedding│
│  (OpenAI text-embedding-3-small)    │
│                                     │
│  Question → Embedding Vector        │
│  (1536 dimensions)                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 2: Vector Similarity Search   │
│  (ChromaDB Query)                   │
│                                     │
│  - Calculate cosine similarity      │
│  - Retrieve top N most similar      │
│    chunks (default: 10)             │
│  - For step questions: 50-100 chunks│
│  - Filter by similarity threshold   │
│    (distance < 0.8)                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 3: Deduplicate Sources         │
│  (rag_system.py)                    │
│                                     │
│  - Group chunks by (pdf, page)      │
│  - Merge chunks from same source    │
│  - Assign unique source numbers     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 4: Build Context               │
│  (rag_system.py)                    │
│                                     │
│  Format:                            │
│  [Source 1 - Page 5]: chunk text... │
│  [Source 2 - Page 6]: chunk text... │
│  ...                                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 5: Generate Answer             │
│  (OpenAI GPT-3.5-turbo)             │
│                                     │
│  Prompt includes:                   │
│  - System instructions              │
│  - Retrieved context chunks          │
│  - User question                     │
│  - Formatting requirements          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Step 6: Extract Citations           │
│  (Regex pattern matching)            │
│                                     │
│  - Find [Source X] in answer        │
│  - Filter citations to only cited   │
│    sources                           │
└──────────────┬──────────────────────┘
               │
               ▼
         Final Answer
    + Source Citations
```

---

## What is Retrieved?

### Retrieval Process

1. **Input**: User question (text)
2. **Embedding**: Question → 1536-dim vector
3. **Search**: Find most similar document chunks using cosine similarity
4. **Output**: Top N relevant chunks with:
   - Text content
   - Source metadata (PDF filename, page number)
   - Similarity distance

### Example Retrieval

**Question**: "What is EDA?"

**Retrieved Chunks**:
```
Chunk 1 (Page 1, distance: 0.15):
"Exploratory Data Analysis (EDA) is a process that involves analyzing 
and visualizing data to uncover patterns..."

Chunk 2 (Page 1, distance: 0.22):
"EDA makes patterns and trends more interpretable. It supports better 
data preprocessing decisions..."

Chunk 3 (Page 2, distance: 0.35):
"After EDA, you can proceed with feature engineering and model training..."
```

---

## When is Retrieval Triggered?

### Retrieval Timing

```
┌─────────────────────────────────────┐
│  User Action: Ask Question          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Check Question Type                │
│                                     │
│  Keywords: step, process, how, etc. │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
   Step Question   Normal Question
        │             │
        │             │
   Retrieve 50-100  Retrieve 10
   chunks          chunks
        │             │
        └──────┬──────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Vector Similarity Search           │
│  (ChromaDB query)                   │
└─────────────────────────────────────┘
```

**Retrieval happens**:
- **When**: Every time user asks a question
- **How many**: 
  - Normal questions: 10 chunks
  - Step/process questions: 50-100 chunks
- **Filtering**: Only chunks with similarity distance < 0.8

---

## How Retrieved Information is Used

### Information Flow

```
Retrieved Chunks
      │
      ▼
┌─────────────────────────────────────┐
│  1. Deduplication                   │
│     - Group by (PDF, page)          │
│     - Merge same-source chunks      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Context Building                │
│     Format:                          │
│     [Source 1 - Page X]: text...     │
│     [Source 2 - Page Y]: text...     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Prompt Construction              │
│     - System instructions            │
│     - Retrieved context              │
│     - User question                  │
│     - Formatting requirements        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. LLM Generation                   │
│     - Model: GPT-3.5-turbo           │
│     - Temperature: 0.7               │
│     - Max tokens: 1000               │
│     - Instruction: Use only context  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  5. Citation Extraction              │
│     - Parse [Source X] patterns      │
│     - Match to citation metadata     │
│     - Return only cited sources      │
└──────────────┬──────────────────────┘
               │
               ▼
         Final Answer
    with Citations
```

### Key Points

1. **Context Limitation**: LLM only sees retrieved chunks, not entire document
2. **Source Tracking**: Each chunk tagged with source (PDF, page)
3. **Citation Matching**: Only sources mentioned in answer are returned
4. **Formatting**: LLM instructed to use Markdown and cite sources

---

## Technical Details

### Embedding Model
- **Model**: `text-embedding-3-small`
- **Dimensions**: 1536
- **Provider**: OpenAI API
- **Purpose**: Convert text to numerical vectors for similarity search

### Vector Database
- **Technology**: ChromaDB
- **Similarity Metric**: Cosine similarity
- **Storage**: Persistent (saved to disk)
- **Query**: Returns top N similar vectors with metadata

### LLM Model
- **Model**: `gpt-3.5-turbo`
- **Provider**: OpenAI API
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Max Tokens**: 1000
- **Role**: Generate answers from retrieved context

### Chunking Strategy
- **Size**: ~500 characters per chunk
- **Method**: Sentence-aware splitting
- **Overlap**: None (simple sequential splitting)
- **Metadata**: Page number, chunk index preserved

---

## Data Flow Diagram

```
┌──────────┐
│   PDF    │
└────┬─────┘
     │ Upload
     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Parse PDF   │─────▶│  Generate     │─────▶│  Store in    │
│  into chunks │      │  Embeddings  │      │  Vector DB   │
└──────────────┘      └──────────────┘      └──────────────┘
                                                      │
                                                      │ Query
                                                      ▼
┌──────────┐      ┌──────────────┐      ┌──────────────┐
│ Question │─────▶│  Retrieve     │◀─────│  Vector DB   │
│          │      │  Similar      │      │              │
└──────────┘      │  Chunks       │      └──────────────┘
                  └───────┬───────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  Build        │
                  │  Context      │
                  └───────┬───────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  Generate    │
                  │  Answer      │
                  │  (LLM)       │
                  └───────┬───────┘
                          │
                          ▼
                  ┌──────────────┐
                  │  Extract     │
                  │  Citations   │
                  └───────┬───────┘
                          │
                          ▼
                    Answer +
                  Citations
```

---

## Key Components

### 1. PDF Parser (`backend/pdf_parser.py`)
- **Purpose**: Extract and chunk PDF text
- **Output**: List of text chunks with page metadata

### 2. Vector Store (`backend/vector_store.py`)
- **Purpose**: Store and query document embeddings
- **Operations**: Add documents, query by similarity

### 3. RAG System (`backend/rag_system.py`)
- **Purpose**: Orchestrate retrieval and generation
- **Methods**:
  - `get_embeddings()`: Generate embeddings
  - `retrieve_relevant_chunks()`: Find similar content
  - `generate_answer()`: Create answer from context
  - `ask_question()`: Complete RAG pipeline

### 4. API Endpoints (`main.py`)
- `/api/upload`: Process PDF upload
- `/api/ask`: Handle question answering
- `/api/status`: System status check
- `/api/clear`: Clear all documents

---

## Retrieval Strategy Details

### When to Retrieve More Chunks?

```python
if question contains ['step', 'process', 'how', 'procedure', 'method', 'way', 'list']:
    retrieve 50-100 chunks  # Comprehensive retrieval
else:
    retrieve 10 chunks      # Standard retrieval
```

### Similarity Filtering

- **Threshold**: Distance < 0.8 (cosine distance)
- **Purpose**: Filter out irrelevant chunks
- **Effect**: Only semantically similar content is used

### Deduplication

- **Key**: `(pdf_filename, page_number)`
- **Action**: Merge chunks from same source
- **Benefit**: Avoid duplicate citations

---

## Answer Generation Process

### Prompt Structure

```
System Message:
"You are a helpful assistant that answers questions based on 
provided context. Always cite your sources."

User Prompt:
"Context from PDF documents:
[Source 1 - Page 5]: chunk text...
[Source 2 - Page 6]: chunk text...

Question: [user question]

Answer the question based on the context above..."
```

### Citation Extraction

1. Parse answer for `[Source X]` patterns
2. Extract source numbers
3. Filter citations to only cited sources
4. Return answer + filtered citations

---

## Performance Considerations

### Token Limits
- **GPT-3.5-turbo**: 4096 tokens context window
- **Strategy**: Limit retrieved chunks to fit within limit
- **Trade-off**: More chunks = more complete, but higher cost

### Retrieval Optimization
- **Similarity threshold**: Filters irrelevant content
- **Smart chunking**: 500 chars balances detail vs. context
- **Deduplication**: Reduces redundant information

### Cost Optimization
- **Embeddings**: ~$0.0001 per 1K tokens
- **LLM**: ~$0.0015-0.002 per 1K tokens
- **Strategy**: Retrieve only what's needed

---

## Summary

**What is retrieved?**
- Text chunks from PDF documents
- Based on semantic similarity to question
- Includes metadata (page, filename)

**When is retrieval triggered?**
- Every user question
- Amount depends on question type (10 vs 50-100 chunks)

**How is retrieved information used?**
- Combined into context prompt
- Passed to LLM for answer generation
- Citations extracted and matched to sources

**Technology Stack:**
- Frontend: HTML/CSS/JavaScript
- Backend: FastAPI (Python)
- Vector DB: ChromaDB
- Embeddings: OpenAI text-embedding-3-small
- LLM: OpenAI GPT-3.5-turbo

