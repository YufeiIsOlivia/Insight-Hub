"""
PDF parsing utilities for extracting text and metadata from PDF files.
"""
import os
from typing import List, Dict
from PyPDF2 import PdfReader


class PDFParser:
    """Parse PDF files and extract text with page information."""
    
    def __init__(self):
        """Initialize the PDF parser."""
        pass
    
    def parse_pdf(self, file_path: str) -> List[Dict[str, any]]:
        """
        Parse a PDF file and extract text chunks with page numbers.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing text chunks with metadata
            Each dict has: 'text', 'page', 'chunk_index'
        """
        chunks = []
        
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            
            for page_num in range(total_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                # Split text into chunks (approximately 500 characters per chunk)
                # This helps with better retrieval and citation
                chunk_size = 500
                page_chunks = self._split_text_into_chunks(text, chunk_size)
                
                for chunk_idx, chunk_text in enumerate(page_chunks):
                    if chunk_text.strip():  # Only add non-empty chunks
                        chunks.append({
                            'text': chunk_text.strip(),
                            'page': page_num + 1,  # 1-indexed page numbers
                            'chunk_index': chunk_idx,
                            'total_pages': total_pages
                        })
            
            return chunks
            
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def _split_text_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """
        Split text into chunks of approximately chunk_size characters.
        Tries to split at sentence boundaries when possible.
        
        Args:
            text: Text to split
            chunk_size: Target size for each chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences first
        sentences = text.replace('\n', ' ').split('. ')
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk_size, save current chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = sentence + '. '
            else:
                current_chunk += sentence + '. '
        
        # Add remaining text
        if current_chunk:
            chunks.append(current_chunk)
        
        # If chunks are still too large, split by character
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by character if necessary
                for i in range(0, len(chunk), chunk_size):
                    final_chunks.append(chunk[i:i + chunk_size])
        
        return final_chunks

