"""
Vector database management for storing and retrieving PDF embeddings.
"""
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid


class VectorStore:
    """Manage vector database for storing PDF document embeddings."""
    
    def __init__(self, persist_directory: str = "./vector_db"):
        """
        Initialize the vector store.
        
        Args:
            persist_directory: Directory to persist the vector database
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Delete existing collection if it exists (to avoid dimension mismatch)
        try:
            self.client.delete_collection(name="pdf_documents")
        except:
            pass  # Collection doesn't exist, that's fine
        
        # Create new collection
        self.collection = self.client.get_or_create_collection(
            name="pdf_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict[str, any]], pdf_filename: str, embeddings: Optional[List[List[float]]] = None):
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of document chunks with text and metadata
            pdf_filename: Name of the source PDF file
            embeddings: Pre-computed embeddings for the chunks (required to avoid dimension mismatch)
        """
        texts = [chunk['text'] for chunk in chunks]
        metadatas = []
        ids = []
        
        for chunk in chunks:
            # Create metadata with source information
            metadata = {
                'pdf_filename': pdf_filename,
                'page': chunk['page'],
                'chunk_index': chunk['chunk_index'],
                'total_pages': chunk.get('total_pages', 0)
            }
            metadatas.append(metadata)
            
            # Generate unique ID
            ids.append(str(uuid.uuid4()))
        
        # Add to collection with embeddings (required to ensure correct dimension)
        if embeddings is None:
            raise ValueError("Embeddings are required. Please provide embeddings when adding documents.")
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
    
    def query(self, query_embeddings: List[List[float]], n_results: int = 5, 
              where: Optional[Dict] = None) -> Dict:
        """
        Query the vector store for similar documents.
        
        Args:
            query_embeddings: Query embedding vectors
            n_results: Number of results to return (use a large number to get all relevant results)
            where: Optional metadata filter
            
        Returns:
            Dictionary with documents, metadatas, and distances
        """
        # Get total collection size to determine max results
        total_docs = self.collection.count()
        
        # If n_results is very large, retrieve all documents (up to collection size)
        # This is useful for step-by-step questions that need comprehensive information
        actual_n_results = min(n_results, total_docs) if total_docs > 0 else n_results
        
        query_params = {
            "query_embeddings": query_embeddings,
            "n_results": actual_n_results
        }
        
        if where:
            query_params["where"] = where
        
        results = self.collection.query(**query_params)
        
        return results
    
    def delete_collection(self):
        """Delete the entire collection (use with caution)."""
        self.client.delete_collection(name="pdf_documents")
        self.collection = self.client.get_or_create_collection(
            name="pdf_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_collection_size(self) -> int:
        """Get the number of documents in the collection."""
        return self.collection.count()

