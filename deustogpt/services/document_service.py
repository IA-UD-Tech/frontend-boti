"""
Document processing service for agent knowledge bases.
"""

import os
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple
import streamlit as st

from langchain.document_loaders import (
    UnstructuredFileLoader, 
    PyPDFLoader,
    TextLoader,
    CSVLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from deustogpt.config import OPENAI_API_KEY, UPLOAD_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentService:
    """Service for processing documents and creating knowledge bases."""
    
    def __init__(self):
        """Initialize the document service."""
        self.upload_dir = UPLOAD_DIR
        self.embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Ensure upload directory exists
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def process_uploaded_file(self, uploaded_file) -> str:
        """
        Process a file uploaded through Streamlit and save it to disk.
        
        Args:
            uploaded_file: File uploaded via st.file_uploader
            
        Returns:
            str: Path to the saved file
        """
        file_path = os.path.join(self.upload_dir, uploaded_file.name)
        
        # Save the uploaded file to disk
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        logger.info(f"File saved: {file_path}")
        return file_path
    
    def load_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load and process a document from the given file path.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of document chunks with text content
            
        Raises:
            ValueError: If the file format is not supported
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            # Select appropriate loader based on file extension
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension in ['.txt', '.md']:
                loader = TextLoader(file_path)
            elif file_extension == '.csv':
                loader = CSVLoader(file_path)
            else:
                # Try with UnstructuredFileLoader for other formats
                loader = UnstructuredFileLoader(file_path)
                
            # Load document
            documents = loader.load()
            logger.info(f"Loaded document: {file_path} with {len(documents)} pages/sections")
            
            # Split into chunks
            document_chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(document_chunks)} chunks")
            
            return document_chunks
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise ValueError(f"Could not process file {file_path}: {str(e)}")
    
    def create_vector_store(self, documents: List[Dict[str, Any]], agent_id: str) -> FAISS:
        """
        Create a vector store from document chunks.
        
        Args:
            documents: List of document chunks
            agent_id: ID of the agent this knowledge base is for
            
        Returns:
            FAISS vector store with embedded documents
        """
        # Create vector store
        vector_store = FAISS.from_documents(documents, self.embeddings)
        
        # Save the vector store
        vector_store_path = os.path.join(self.upload_dir, f"vector_store_{agent_id}")
        vector_store.save_local(vector_store_path)
        
        logger.info(f"Created vector store for agent {agent_id} at {vector_store_path}")
        return vector_store
    
    def load_vector_store(self, agent_id: str) -> Optional[FAISS]:
        """
        Load a vector store for a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            FAISS vector store or None if it doesn't exist
        """
        vector_store_path = os.path.join(self.upload_dir, f"vector_store_{agent_id}")
        
        if os.path.exists(vector_store_path):
            try:
                vector_store = FAISS.load_local(vector_store_path, self.embeddings)
                logger.info(f"Loaded vector store for agent {agent_id}")
                return vector_store
            except Exception as e:
                logger.error(f"Error loading vector store for agent {agent_id}: {str(e)}")
                return None
        else:
            logger.info(f"No vector store found for agent {agent_id}")
            return None
    
    def create_knowledge_base_for_agent(self, agent_id: str, file_paths: List[str]) -> bool:
        """
        Create a knowledge base for an agent from multiple documents.
        
        Args:
            agent_id: ID of the agent
            file_paths: List of paths to document files
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            all_documents = []
            
            # Process each file
            for file_path in file_paths:
                documents = self.load_document(file_path)
                all_documents.extend(documents)
            
            if not all_documents:
                logger.warning(f"No documents processed for agent {agent_id}")
                return False
                
            # Create and save vector store
            self.create_vector_store(all_documents, agent_id)
            
            # Store in session state for quick access
            if "agent_knowledge_bases" not in st.session_state:
                st.session_state.agent_knowledge_bases = {}
            
            st.session_state.agent_knowledge_bases[agent_id] = {
                "file_count": len(file_paths),
                "chunk_count": len(all_documents),
                "file_paths": file_paths
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating knowledge base for agent {agent_id}: {str(e)}")
            return False
    
    def similarity_search(self, agent_id: str, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform a similarity search against an agent's knowledge base.
        
        Args:
            agent_id: ID of the agent
            query: Query string to search for
            k: Number of results to return
            
        Returns:
            List of relevant document chunks with content and metadata
        """
        vector_store = self.load_vector_store(agent_id)
        
        if not vector_store:
            logger.warning(f"No vector store available for agent {agent_id}")
            return []
            
        try:
            # Perform the search
            results = vector_store.similarity_search_with_score(query, k=k)
            
            # Format the results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing similarity search for agent {agent_id}: {str(e)}")
            return []