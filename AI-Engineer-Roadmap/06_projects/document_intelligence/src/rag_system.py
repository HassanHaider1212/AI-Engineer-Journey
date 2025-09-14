"""
RAG System - Retrieval-Augmented Generation Implementation

This module implements a complete RAG system for document question-answering
using vector search and language models.
"""

from typing import List, Dict, Any, Optional, Tuple
import time
import logging
from datetime import datetime

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.vector_store import VectorStore
from src.utils.config import Settings
from src.models.document import Document, Chunk

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Retrieval-Augmented Generation system for document Q&A.
    """
    
    def __init__(self, settings: Settings, vector_store: VectorStore):
        self.settings = settings
        self.vector_store = vector_store
        
        # Initialize LLM and embeddings
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            api_key=settings.openai_api_key
        )
        
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key
        )
        
        # Initialize prompt template
        self.prompt_template = self._create_prompt_template()
        
        # Initialize chain
        self.chain = self._create_chain()
    
    def _create_prompt_template(self) -> PromptTemplate:
        """Create the prompt template for RAG."""
        template = """
        You are a helpful AI assistant that answers questions based on the provided context.
        
        Context:
        {context}
        
        Question: {question}
        
        Instructions:
        1. Answer the question based ONLY on the provided context
        2. If the answer is not in the context, say "I cannot find the answer in the provided documents"
        3. Be specific and cite relevant information from the context
        4. If you're unsure, express your uncertainty
        5. Keep your answer concise but comprehensive
        
        Answer:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _create_chain(self):
        """Create the RAG chain."""
        return (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    def query(
        self,
        question: str,
        max_results: int = 5,
        similarity_threshold: float = 0.7,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: The question to ask
            max_results: Maximum number of relevant chunks to retrieve
            similarity_threshold: Minimum similarity score for chunks
            temperature: LLM temperature for response generation
            max_tokens: Maximum tokens for response
            
        Returns:
            Dictionary containing answer, sources, and metadata
        """
        start_time = time.time()
        
        try:
            # Update LLM parameters
            self.llm.temperature = temperature
            self.llm.max_tokens = max_tokens
            
            # Retrieve relevant chunks
            relevant_chunks = self._retrieve_relevant_chunks(
                question, max_results, similarity_threshold
            )
            
            if not relevant_chunks:
                return {
                    "answer": "I cannot find relevant information in the documents to answer your question.",
                    "sources": [],
                    "processing_time": time.time() - start_time,
                    "tokens_used": 0
                }
            
            # Prepare context
            context = self._prepare_context(relevant_chunks)
            
            # Generate answer
            answer = self.chain.invoke({
                "context": context,
                "question": question
            })
            
            # Prepare sources
            sources = self._prepare_sources(relevant_chunks)
            
            processing_time = time.time() - start_time
            
            return {
                "answer": answer,
                "sources": sources,
                "processing_time": processing_time,
                "tokens_used": self._estimate_tokens(question + context + answer)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "processing_time": time.time() - start_time,
                "tokens_used": 0
            }
    
    def _retrieve_relevant_chunks(
        self,
        question: str,
        max_results: int,
        similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for the question.
        
        Args:
            question: The question to search for
            max_results: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            # Get embedding for the question
            question_embedding = self.embeddings.embed_query(question)
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=question_embedding,
                top_k=max_results,
                similarity_threshold=similarity_threshold
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            return []
    
    def _prepare_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Prepare context from retrieved chunks.
        
        Args:
            chunks: List of relevant chunks
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            chunk_text = chunk.get('chunk_text', '')
            document_title = chunk.get('document_title', 'Unknown Document')
            
            context_part = f"[Source {i} - {document_title}]\n{chunk_text}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _prepare_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare source information for the response.
        
        Args:
            chunks: List of relevant chunks
            
        Returns:
            List of source dictionaries
        """
        sources = []
        
        for chunk in chunks:
            source = {
                "chunk_text": chunk.get('chunk_text', ''),
                "document_title": chunk.get('document_title', 'Unknown'),
                "similarity": chunk.get('similarity', 0.0),
                "metadata": chunk.get('metadata', {}),
                "chunk_id": chunk.get('chunk_id', '')
            }
            sources.append(source)
        
        return sources
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            vector_stats = self.vector_store.get_stats()
            
            return {
                "vector_store_stats": vector_stats,
                "llm_model": self.settings.openai_model,
                "embedding_model": self.settings.embedding_model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}
    
    def update_llm_parameters(
        self,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None
    ):
        """
        Update LLM parameters.
        
        Args:
            temperature: New temperature value
            max_tokens: New max tokens value
            model: New model name
        """
        if temperature is not None:
            self.llm.temperature = temperature
        
        if max_tokens is not None:
            self.llm.max_tokens = max_tokens
        
        if model is not None:
            self.llm.model = model
            # Recreate the chain with new model
            self.chain = self._create_chain()
        
        logger.info(f"Updated LLM parameters: temp={self.llm.temperature}, max_tokens={self.llm.max_tokens}, model={self.llm.model}")
    
    def test_system(self) -> Dict[str, Any]:
        """
        Test the RAG system with a sample query.
        
        Returns:
            Test results
        """
        test_question = "What is the main topic of the documents?"
        
        try:
            result = self.query(test_question, max_results=3)
            
            return {
                "status": "success",
                "test_question": test_question,
                "answer_length": len(result["answer"]),
                "sources_found": len(result["sources"]),
                "processing_time": result["processing_time"],
                "error": None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "test_question": test_question,
                "error": str(e)
            }
