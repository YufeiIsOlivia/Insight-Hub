"""
RAG (Retrieval-Augmented Generation) system for answering questions about PDFs.
"""
import os
import re
from typing import List, Dict, Optional, Tuple
from openai import OpenAI
from backend.vector_store import VectorStore


class RAGSystem:
    """RAG system for question answering with source citations."""
    
    def __init__(self, vector_store: VectorStore, api_key: Optional[str] = None, use_openrouter: bool = True):
        """
        Initialize the RAG system.
        
        Args:
            vector_store: VectorStore instance for document retrieval
            api_key: API key (OpenRouter or OpenAI, if None, will try to get from environment)
            use_openrouter: Whether to use OpenRouter API (default: True)
        """
        self.vector_store = vector_store
        self.use_openrouter = use_openrouter
        
        # Initialize API client
        openrouter_key = api_key or os.getenv("OPENROUTER_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if use_openrouter:
            if not openrouter_key:
                raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
            
            # Use OpenRouter API for LLM
            # Note: OpenRouter requires specific headers for analytics
            self.client = OpenAI(
                api_key=openrouter_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "http://localhost:8000",  # Your site URL for OpenRouter analytics
                    "X-Title": "PDF RAG Q&A System"  # Your app name for OpenRouter analytics
                }
            )
            self.llm_model = "openai/gpt-3.5-turbo"  # OpenRouter model format
            
            # For embeddings, OpenRouter may not support embeddings API well
            # So we'll try to use OpenAI API if available
            if openai_key:
                # Use OpenAI directly for embeddings (more reliable)
                self.embedding_client = OpenAI(api_key=openai_key)
                self.embedding_model = "text-embedding-ada-002"
            else:
                # Try using OpenRouter for embeddings
                # Note: OpenRouter may not support all embedding models
                self.embedding_client = self.client
                # Try without the "openai/" prefix first
                self.embedding_model = "text-embedding-ada-002"
        else:
            # Use OpenAI API directly
            if not openai_key:
                raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
            self.client = OpenAI(api_key=openai_key)
            self.embedding_client = self.client
            self.embedding_model = "text-embedding-3-small"
            self.llm_model = "gpt-3.5-turbo"
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        response = self.embedding_client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )
        return [item.embedding for item in response.data]
    
    def retrieve_relevant_chunks(self, question: str, n_results: int = 10) -> List[Dict]:
        """
        Retrieve relevant document chunks for a question.
        
        Args:
            question: User's question
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            List of relevant chunks with metadata
        """
        # Get embedding for the question
        question_embedding = self.get_embeddings([question])[0]
        
        # Query vector store
        results = self.vector_store.query([question_embedding], n_results=n_results)
        
        # Format results and filter by similarity threshold
        # Note: We retrieve top N most similar chunks, not all chunks
        # This is because:
        # 1. LLM has token limits (GPT-3.5-turbo: 4096 tokens)
        # 2. Less relevant chunks can confuse the LLM
        # 3. For step questions, we already retrieve many chunks (50-100)
        retrieved_chunks = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i] if 'distances' in results and results['distances'] else None
                
                # Filter by similarity threshold
                # Cosine distance: 0 = identical, 1 = orthogonal, 2 = opposite
                # We'll keep chunks with distance < 0.8 (roughly > 0.2 cosine similarity)
                # This helps filter out completely unrelated content
                if distance is None or distance < 0.8:
                    chunk = {
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': distance
                    }
                    retrieved_chunks.append(chunk)
        
        return retrieved_chunks
    
    def generate_answer(self, question: str, context_chunks: List[Dict], question_type: str = 'Default') -> Dict[str, any]:
        """
        Generate an answer to the question using retrieved context.
        
        Args:
            question: User's question
            context_chunks: Retrieved relevant document chunks
            
        Returns:
            Dictionary with answer and citations
        """
        if not context_chunks:
            return {
                'answer': "I couldn't find relevant information in the uploaded PDFs to answer your question.",
                'citations': []
            }
        
        # Build context from retrieved chunks
        # Deduplicate chunks by (pdf_filename, page) to avoid duplicate citations
        unique_sources = {}  # Key: (pdf_filename, page), Value: {'source_num': int, 'chunks': list}
        context_parts = []
        
        source_counter = 1
        for chunk in context_chunks:
            metadata = chunk['metadata']
            page = metadata.get('page', 'Unknown')
            pdf_filename = metadata.get('pdf_filename', 'Unknown')
            source_key = (pdf_filename, page)
            
            # If we've seen this source before, add to existing chunks
            if source_key in unique_sources:
                unique_sources[source_key]['chunks'].append(chunk['text'])
            else:
                # New unique source
                unique_sources[source_key] = {
                    'source_num': source_counter,
                    'chunks': [chunk['text']],
                    'pdf_filename': pdf_filename,
                    'page': page
                }
                source_counter += 1
        
        # Build context and citations from unique sources
        citations = []
        for source_key, source_info in unique_sources.items():
            source_num = source_info['source_num']
            # Combine all chunks from the same source
            combined_text = " ".join(source_info['chunks'])
            context_parts.append(f"[Source {source_num} - Page {source_info['page']}]: {combined_text}")
            
            # Create citation with first chunk's snippet
            text_snippet = source_info['chunks'][0][:200] + "..." if len(source_info['chunks'][0]) > 200 else source_info['chunks'][0]
            citations.append({
                'source': source_num,
                'pdf_filename': source_info['pdf_filename'],
                'page': source_info['page'],
                'text_snippet': text_snippet
            })
        
        context = "\n\n".join(context_parts)
        
        # Create question type-specific prompt
        num_sources = len(unique_sources)  # Use deduplicated count
        
        # Base instructions
        base_instructions = """You are a helpful assistant that answers questions based on the provided context from PDF documents. 
CRITICAL: Use ONLY the information from the context to answer the question. 

If the context does NOT contain relevant information to answer the question, you MUST clearly state:
"I cannot answer this question based on the provided PDF documents. The documents do not contain information about [topic]."

DO NOT make up information or use knowledge outside the provided context. If the question is about something not in the documents, explicitly say so. 

IMPORTANT FORMATTING REQUIREMENTS:
1. Format your answer using Markdown for better readability:
   - Use **bold** for key terms and important concepts
   - Use bullet points (-) or numbered lists for multiple items
   - Use line breaks to separate paragraphs
   - Use headings (##) for main sections if the answer is long
2. Cite ALL relevant sources: Use [Source 1], [Source 2], etc. for each piece of information you reference.
"""
        
        # Question type-specific instructions
        type_instructions = {
            'Summary': """SPECIFIC INSTRUCTIONS FOR SUMMARY QUESTIONS:
- Extract core conclusions and key findings
- Ignore minor details, focus on main points
- Keep the answer concise and well-structured
- Organize information logically (most important points first)
- Use bullet points or short paragraphs
- Cite sources for each main point""",
            
            'Fact': """SPECIFIC INSTRUCTIONS FOR FACTUAL QUESTIONS:
- Answer the specific question directly and precisely
- Cite the source for the fact
- Do not expand on unrelated information
- Keep the answer focused and concise
- If multiple sources mention the same fact, cite all relevant sources""",
            
            'Procedure': """SPECIFIC INSTRUCTIONS FOR PROCEDURE/STEP QUESTIONS:
- List ALL steps in the correct sequence
- Use numbered lists (1., 2., 3., etc.) for sequential steps
- Include complete information from all relevant sources
- Read through ALL provided sources carefully to find every step
- If steps are mentioned across multiple sources, combine them in order
- Be thorough - do not skip any steps mentioned in the context
- Cite the source for each step or group of steps""",
            
            'Compare/Analyze': """SPECIFIC INSTRUCTIONS FOR COMPARISON/ANALYSIS QUESTIONS:
- Compare different aspects clearly
- Provide structured analysis with clear sections
- Use headings or bullet points to organize comparisons
- Cite sources for each comparison point
- Maintain clarity and structure throughout
- Highlight key differences and similarities""",
            
            'Default': """SPECIFIC INSTRUCTIONS:
- Answer the question based on the context provided
- Structure your answer clearly with proper formatting
- Start with a brief direct answer, then provide details
- Use lists when listing multiple points
- Ensure accuracy by using only information from the context"""
        }
        
        # Combine instructions
        specific_instruction = type_instructions.get(question_type, type_instructions['Default'])
        
        prompt = f"""{base_instructions}

{specific_instruction}

Context from PDF documents:
{context}

Question: {question}

Answer the question based on the context above. Make sure to cite ALL relevant sources (Source 1 through Source {num_sources}) that contain information relevant to the answer:"""
        
        # Generate answer using LLM (OpenRouter or OpenAI)
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context. Always format your answers using Markdown with proper spacing, bold text for key terms, lists, and clear paragraph breaks. Always cite your sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
        except Exception as e:
            # Provide more detailed error information
            error_msg = str(e)
            if "401" in error_msg or "User not found" in error_msg:
                raise Exception(f"Authentication failed. Please check your API key. Error: {error_msg}")
            raise Exception(f"Error calling LLM API: {error_msg}")
        
        answer = response.choices[0].message.content
        
        # Extract which sources are actually cited in the answer
        cited_source_numbers = set()
        # Find all [Source X] patterns in the answer
        source_pattern = r'\[Source\s+(\d+)\]'
        matches = re.findall(source_pattern, answer, re.IGNORECASE)
        for match in matches:
            source_num = int(match)
            # Only add if this source actually exists in our citations
            if any(c['source'] == source_num for c in citations):
                cited_source_numbers.add(source_num)
        
        # If sources were cited, only return those citations and renumber them sequentially
        # Otherwise, return all citations (fallback)
        if cited_source_numbers:
            # Filter to only cited sources
            filtered_citations = [
                citation for citation in citations 
                if citation['source'] in cited_source_numbers
            ]
            # Sort by original source number to maintain order
            filtered_citations.sort(key=lambda x: x['source'])
            # Renumber sequentially (1, 2, 3, ...) to avoid gaps
            source_remap = {}
            for idx, citation in enumerate(filtered_citations, start=1):
                old_source_num = citation['source']
                source_remap[old_source_num] = idx
                citation['source'] = idx
            
            # Update answer to use new sequential source numbers
            def replace_source(match):
                old_num = int(match.group(1))
                if old_num in source_remap:
                    return f"[Source {source_remap[old_num]}]"
                return match.group(0)  # Keep original if not in remap
            
            answer = re.sub(source_pattern, replace_source, answer, flags=re.IGNORECASE)
        else:
            # If no sources were explicitly cited, return all (but this shouldn't happen with improved prompt)
            filtered_citations = citations
        
        return {
            'answer': answer,
            'citations': filtered_citations
        }
    
    def classify_question_type(self, question: str) -> Tuple[str, int]:
        """
        Classify question type and determine retrieval strategy.
        
        Args:
            question: User's question
            
        Returns:
            Tuple of (question_type, recommended_chunk_count)
        """
        question_lower = question.lower()
        
        # Summary questions
        summary_keywords = ['summary', 'summarize', 'overview', 'main points', 'key findings', 
                           'conclusion', 'what is the gist', 'briefly explain']
        if any(keyword in question_lower for keyword in summary_keywords):
            return ('Summary', 40)  # 30-50, use 40 as middle
        
        # Procedure/Step questions
        procedure_keywords = ['step', 'steps', 'process', 'procedure', 'how to', 'how do', 
                             'method', 'way', 'list', 'sequence', 'order', 'workflow']
        if any(keyword in question_lower for keyword in procedure_keywords):
            return ('Procedure', 40)  # 30-50, use 40 as middle
        
        # Compare/Analyze questions
        compare_keywords = ['compare', 'difference', 'different', 'versus', 'vs', 'vs.', 
                           'similar', 'similarity', 'analyze', 'analysis', 'contrast', 
                           'relationship', 'between']
        if any(keyword in question_lower for keyword in compare_keywords):
            return ('Compare/Analyze', 30)  # 20-40, use 30 as middle
        
        # Fact questions (simple factual queries)
        fact_keywords = ['what is', 'what are', 'who is', 'when', 'where', 'which', 
                        'define', 'definition', 'meaning']
        # Only classify as fact if it's a simple question (not too long, no complex keywords)
        if any(keyword in question_lower for keyword in fact_keywords) and len(question.split()) < 10:
            return ('Fact', 8)  # 5-10, use 8 as middle
        
        # Default
        return ('Default', 25)  # 20-30, use 25 as middle
    
    def ask_question(self, question: str, n_results: int = None) -> Dict[str, any]:
        """
        Complete RAG pipeline: retrieve relevant chunks and generate answer.
        
        Args:
            question: User's question
            n_results: Number of relevant chunks to retrieve (if None, auto-determined by question type)
            
        Returns:
            Dictionary with answer and citations
        """
        # Classify question type and determine retrieval strategy
        question_type, recommended_chunks = self.classify_question_type(question)
        
        # Use recommended chunks if n_results not specified
        if n_results is None:
            n_results = recommended_chunks
        
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(question, n_results=n_results)
        
        # Generate answer with question type-specific prompt
        result = self.generate_answer(question, relevant_chunks, question_type=question_type)
        
        return result

