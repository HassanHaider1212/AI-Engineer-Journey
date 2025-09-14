"""
Document Intelligence System - RAG-powered document Q&A

A production-ready system for processing documents and answering questions
using Retrieval-Augmented Generation (RAG) with vector search.
"""

import streamlit as st
import os
from typing import List, Dict, Any, Optional
import tempfile
import logging
from pathlib import Path

from src.document_processor import DocumentProcessor
from src.rag_system import RAGSystem
from src.vector_store import VectorStore
from src.utils.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Page configuration
st.set_page_config(
    page_title="Document Intelligence System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_services():
    """Initialize document processing and RAG services."""
    try:
        # Initialize vector store
        vector_store = VectorStore(settings)
        
        # Initialize document processor
        doc_processor = DocumentProcessor(settings)
        
        # Initialize RAG system
        rag_system = RAGSystem(settings, vector_store)
        
        return doc_processor, rag_system, vector_store
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        return None, None, None

def display_header():
    """Display application header."""
    st.markdown('<h1 class="main-header">📄 Document Intelligence System</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Upload documents and ask questions using AI-powered document analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

def upload_documents(doc_processor: DocumentProcessor):
    """Handle document upload and processing."""
    st.subheader("📁 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'txt', 'docx', 'md'],
        accept_multiple_files=True,
        help="Upload PDF, TXT, DOCX, or Markdown files"
    )
    
    if uploaded_files:
        st.write(f"Uploaded {len(uploaded_files)} file(s)")
        
        # Process documents
        if st.button("Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                processed_docs = []
                
                for uploaded_file in uploaded_files:
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Process document
                        doc = doc_processor.process_document(tmp_path)
                        processed_docs.append(doc)
                        
                        # Clean up temporary file
                        os.unlink(tmp_path)
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                
                if processed_docs:
                    st.success(f"Successfully processed {len(processed_docs)} documents!")
                    
                    # Store processed documents in session state
                    st.session_state.processed_documents = processed_docs
                    
                    # Show document summaries
                    st.subheader("📋 Document Summaries")
                    for i, doc in enumerate(processed_docs):
                        with st.expander(f"Document {i+1}: {doc.metadata.get('title', 'Untitled')}"):
                            st.write(f"**Type:** {doc.metadata.get('type', 'Unknown')}")
                            st.write(f"**Pages:** {doc.metadata.get('pages', 'N/A')}")
                            st.write(f"**Chunks:** {len(doc.chunks)}")
                            st.write(f"**Preview:** {doc.content[:200]}...")

def build_knowledge_base(vector_store: VectorStore):
    """Build knowledge base from processed documents."""
    if 'processed_documents' not in st.session_state:
        st.warning("Please upload and process documents first.")
        return
    
    st.subheader("🧠 Build Knowledge Base")
    
    if st.button("Build Knowledge Base", type="primary"):
        with st.spinner("Building knowledge base..."):
            try:
                # Add documents to vector store
                for doc in st.session_state.processed_documents:
                    vector_store.add_document(doc)
                
                st.success("Knowledge base built successfully!")
                st.session_state.knowledge_base_built = True
                
                # Show statistics
                stats = vector_store.get_stats()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Documents", stats['total_documents'])
                with col2:
                    st.metric("Total Chunks", stats['total_chunks'])
                with col3:
                    st.metric("Vector Dimensions", stats['vector_dimensions'])
                
            except Exception as e:
                st.error(f"Error building knowledge base: {str(e)}")

def query_documents(rag_system: RAGSystem):
    """Query the document knowledge base."""
    if not st.session_state.get('knowledge_base_built', False):
        st.warning("Please build the knowledge base first.")
        return
    
    st.subheader("❓ Ask Questions")
    
    # Query input
    query = st.text_area(
        "Enter your question:",
        placeholder="What is the main topic of the documents?",
        height=100
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        with col1:
            max_results = st.slider("Max Results", 1, 10, 5)
            similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.7)
        with col2:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
            max_tokens = st.slider("Max Tokens", 100, 1000, 500)
    
    if st.button("Ask Question", type="primary") and query:
        with st.spinner("Searching documents and generating answer..."):
            try:
                # Get answer from RAG system
                result = rag_system.query(
                    question=query,
                    max_results=max_results,
                    similarity_threshold=similarity_threshold,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                # Display answer
                st.subheader("🤖 Answer")
                st.write(result['answer'])
                
                # Display sources
                if result['sources']:
                    st.subheader("📚 Sources")
                    for i, source in enumerate(result['sources']):
                        with st.expander(f"Source {i+1} (Similarity: {source['similarity']:.3f})"):
                            st.write(f"**Document:** {source['document_title']}")
                            st.write(f"**Chunk:** {source['chunk_text'][:200]}...")
                            st.write(f"**Metadata:** {source['metadata']}")
                
                # Display query statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sources Found", len(result['sources']))
                with col2:
                    st.metric("Processing Time", f"{result['processing_time']:.2f}s")
                with col3:
                    st.metric("Tokens Used", result.get('tokens_used', 'N/A'))
                
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")

def display_analytics(vector_store: VectorStore):
    """Display knowledge base analytics."""
    if not st.session_state.get('knowledge_base_built', False):
        st.warning("Please build the knowledge base first.")
        return
    
    st.subheader("📊 Knowledge Base Analytics")
    
    try:
        stats = vector_store.get_stats()
        
        # Display statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Documents", stats['total_documents'])
            st.metric("Total Chunks", stats['total_chunks'])
            st.metric("Average Chunk Size", f"{stats['avg_chunk_size']:.0f} chars")
        
        with col2:
            st.metric("Vector Dimensions", stats['vector_dimensions'])
            st.metric("Storage Size", f"{stats['storage_size']:.2f} MB")
            st.metric("Last Updated", stats['last_updated'])
        
        # Document breakdown
        if 'document_breakdown' in stats:
            st.subheader("📋 Document Breakdown")
            for doc_type, count in stats['document_breakdown'].items():
                st.write(f"**{doc_type}:** {count} documents")
        
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def main():
    """Main application function."""
    display_header()
    
    # Initialize services
    doc_processor, rag_system, vector_store = initialize_services()
    
    if not all([doc_processor, rag_system, vector_store]):
        st.error("Failed to initialize services. Please check your configuration.")
        return
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Upload Documents", "Build Knowledge Base", "Query Documents", "Analytics"]
    )
    
    # Main content based on selected page
    if page == "Upload Documents":
        upload_documents(doc_processor)
    elif page == "Build Knowledge Base":
        build_knowledge_base(vector_store)
    elif page == "Query Documents":
        query_documents(rag_system)
    elif page == "Analytics":
        display_analytics(vector_store)
    
    # Sidebar information
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 About")
    st.sidebar.markdown("""
    This Document Intelligence System uses:
    - **RAG (Retrieval-Augmented Generation)** for accurate answers
    - **Vector Search** for semantic document retrieval
    - **LangChain** for AI workflow orchestration
    - **Streamlit** for interactive interface
    """)
    
    # Session state info
    if st.sidebar.checkbox("Show Session State"):
        st.sidebar.json({
            "processed_documents": len(st.session_state.get('processed_documents', [])),
            "knowledge_base_built": st.session_state.get('knowledge_base_built', False)
        })

if __name__ == "__main__":
    main()
