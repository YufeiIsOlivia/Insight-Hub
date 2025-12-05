# Quick Start Guide

## Your OpenRouter API Key is Already Configured! ✅

Your `.env` file has been created with your OpenRouter API key. You're ready to go!

## Steps to Run:

1. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

2. **Start the server**:
```bash
python main.py
```

3. **Open your browser** and go to:
```
http://localhost:8000
```

4. **Upload a PDF** and start asking questions!

## What's Different with OpenRouter?

- The system now uses OpenRouter API, which gives you access to multiple LLM models
- Current model: `openai/gpt-3.5-turbo` (you can change this in `backend/rag_system.py`)
- Embeddings use: `text-embedding-ada-002`

## Troubleshooting

If you encounter any issues:
1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Check that the `.env` file exists and contains your API key
3. Check the terminal for error messages

Enjoy your PDF RAG Q&A system! 🚀

