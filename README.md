# PDF RAG Q&A System

A web application that allows you to upload PDF files, parse their content, and ask questions using a RAG (Retrieval-Augmented Generation) agent with source citations.

## Features

- Upload PDF files
- Parse and extract text from PDFs
- Ask questions about the PDF content
- Get answers with source citations (page numbers and text snippets)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp env.example .env
# Edit .env and add your OpenRouter API key (or OpenAI API key)
```

3. Run the server:
```bash
python main.py
```

4. Open your browser and navigate to `http://localhost:8000`

## API Key Requirements

- **OpenRouter API Key** (Recommended): Supports multiple LLM models. Get your key from https://openrouter.ai/keys
- **OpenAI API Key** (Alternative or for embeddings): Direct OpenAI API access. Get your key from https://platform.openai.com/api-keys

The system will automatically use OpenRouter if `OPENROUTER_API_KEY` is set, otherwise it will use OpenAI API.

**Note**: If you encounter 401 "User not found" errors with OpenRouter:
1. Check your OpenRouter account status at https://openrouter.ai/keys
2. Verify your API key is active and has proper permissions
3. Try regenerating your API key
4. As a workaround, you can use OpenAI API key for both embeddings and LLM by setting `OPENAI_API_KEY` instead

## Project Structure

```
.
├── main.py              # FastAPI application entry point
├── backend/
│   ├── __init__.py
│   ├── pdf_parser.py    # PDF parsing utilities
│   ├── rag_system.py    # RAG agent implementation
│   └── vector_store.py  # Vector database management
├── frontend/
│   └── index.html       # Web interface
├── uploads/             # Uploaded PDF files (created automatically)
├── vector_db/           # Vector database storage (created automatically)
└── requirements.txt
```

