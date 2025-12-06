"""
Main FastAPI application for PDF RAG Q&A system.
"""
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional
import shutil
from pathlib import Path

from backend.pdf_parser import PDFParser
from backend.vector_store import VectorStore
from backend.rag_system import RAGSystem
import time

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="PDF RAG Q&A System")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

VECTOR_DB_DIR = Path("vector_db")
VECTOR_DB_DIR.mkdir(exist_ok=True)

# Initialize components
pdf_parser = PDFParser()
vector_store = VectorStore(persist_directory=str(VECTOR_DB_DIR))
rag_system = None  # Will be initialized on first use


def get_rag_system():
    """Get or initialize RAG system."""
    global rag_system
    if rag_system is None:
        # Check if we should force OpenRouter (useful for evaluation/testing different models)
        force_openrouter = os.getenv("FORCE_OPENROUTER", "false").lower() == "true"
        
        openai_key = os.getenv("OPENAI_API_KEY")
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        
        if force_openrouter:
            # Force OpenRouter (for evaluation/testing different models)
            if not openrouter_key:
                raise HTTPException(
                    status_code=500,
                    detail="OpenRouter API key is required when FORCE_OPENROUTER=true. Set OPENROUTER_API_KEY in .env file."
                )
            rag_system = RAGSystem(vector_store, openrouter_key, use_openrouter=True)
        elif openai_key:
            # Use OpenAI API (recommended for normal use)
            rag_system = RAGSystem(vector_store, openai_key, use_openrouter=False)
        elif openrouter_key:
            # Fallback to OpenRouter
            rag_system = RAGSystem(vector_store, openrouter_key, use_openrouter=True)
        else:
            raise HTTPException(
                status_code=500,
                detail="API key not found. Please set OPENAI_API_KEY in .env file. Get your key from https://platform.openai.com/api-keys"
            )
    return rag_system


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page."""
    html_path = Path("frontend/index.html")
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Frontend not found</h1>")




@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process a PDF file.
    
    Args:
        file: Uploaded PDF file
        
    Returns:
        JSON response with upload status
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse PDF
        chunks = pdf_parser.parse_pdf(str(file_path))
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Get embeddings for the chunks
        rag = get_rag_system()
        texts = [chunk['text'] for chunk in chunks]
        embeddings = rag.get_embeddings(texts)
        
        # Add to vector store with embeddings
        vector_store.add_documents(chunks, file.filename, embeddings=embeddings)
        
        return JSONResponse({
            "status": "success",
            "message": f"PDF uploaded and processed successfully",
            "filename": file.filename,
            "chunks": len(chunks),
            "total_documents": vector_store.get_collection_size()
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/api/ask")
async def ask_question(data: dict):
    """
    Ask a question about the uploaded PDFs.
    
    Args:
        data: Dictionary with 'question' key and optional 'model_name' key
        
    Returns:
        JSON response with answer and citations
    """
    question = data.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    model_name = data.get("model_name")  # Optional model override
    
    try:
        rag = get_rag_system()
        
        # Format model name for API call
        api_model_name = None
        if model_name:
            if rag.use_openrouter:
                # Format for OpenRouter - use same logic as notebook
                # If already has provider prefix, check if it needs conversion
                if '/' in model_name:
                    # Handle special cases for OpenRouter model IDs
                    # OpenRouter uses claude-3-5-sonnet (with hyphen) not claude-3.5-sonnet (with dot)
                    if 'claude-3.5' in model_name:
                        api_model_name = model_name.replace('claude-3.5', 'claude-3-5')
                    else:
                        # Keep model name as-is if it already has provider prefix
                        api_model_name = model_name
                else:
                    # Map common model names to providers
                    if model_name.startswith('gpt'):
                        api_model_name = f"openai/{model_name}"
                    elif model_name.startswith('claude'):
                        # OpenRouter uses claude-3-5-sonnet (hyphen) not claude-3.5-sonnet (dot)
                        formatted = model_name.replace('3.5', '3-5')
                        api_model_name = f"anthropic/{formatted}"
                    elif model_name.startswith('llama'):
                        api_model_name = f"meta/{model_name}"
                    elif model_name.startswith('gemini'):
                        api_model_name = f"google/{model_name}"
                    else:
                        # Default: assume OpenAI format
                        api_model_name = f"openai/{model_name}"
            else:
                # For OpenAI direct API, use model name as-is
                api_model_name = model_name
        
        # Ask question with optional model override
        result = rag.ask_question(question, model_name=api_model_name)
        
        return JSONResponse({
            "status": "success",
            "answer": result["answer"],
            "citations": result["citations"],
            "retrieved_docs": result.get("retrieved_docs", [])  # Include retrieved documents for evaluation
        })
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@app.get("/api/status")
async def get_status():
    """Get system status."""
    try:
        # Try to get collection size, but handle case where collection doesn't exist yet
        try:
            total_docs = vector_store.get_collection_size()
        except Exception:
            total_docs = 0
        
        # Check actual RAG system configuration
        rag = get_rag_system()
        force_openrouter = os.getenv("FORCE_OPENROUTER", "false").lower() == "true"
        
        return JSONResponse({
            "status": "success",
            "total_documents": total_docs,
            "has_api_key": bool(os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")),
            "using_openai": not rag.use_openrouter,
            "using_openrouter": rag.use_openrouter,
            "force_openrouter": force_openrouter
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@app.delete("/api/clear")
async def clear_documents():
    """Clear all uploaded documents from the vector store."""
    try:
        # Delete collection from ChromaDB
        vector_store.delete_collection()
        
        # Clear uploaded PDF files
        for file in UPLOAD_DIR.glob("*.pdf"):
            file.unlink()
        
        # Clear vector database directory completely
        # ChromaDB's delete_collection() may leave files behind, so we need to clean them up
        if VECTOR_DB_DIR.exists():
            # Remove all files and subdirectories in vector_db
            for item in VECTOR_DB_DIR.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        
        # Reinitialize the collection (empty)
        vector_store.collection = vector_store.client.get_or_create_collection(
            name="pdf_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        return JSONResponse({
            "status": "success",
            "message": "All documents cleared"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")




@app.post("/api/generate-quiz")
async def generate_quiz(data: dict = None):
    """
    Generate quiz questions based on uploaded PDFs.
    
    Args:
        data: Optional dictionary with 'num_questions' key (default: 10)
        
    Returns:
        JSON response with quiz questions
    """
    num_questions = 10
    if data and 'num_questions' in data:
        try:
            num_questions = int(data['num_questions'])
            if num_questions < 1 or num_questions > 20:
                num_questions = 10  # Default to 10 if invalid
        except (ValueError, TypeError):
            num_questions = 10
    
    try:
        rag = get_rag_system()
        questions = rag.generate_quiz_questions(num_questions=num_questions)
        
        return JSONResponse({
            "status": "success",
            "questions": questions,
            "total_questions": len(questions)
        })
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating quiz: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)

