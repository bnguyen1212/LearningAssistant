import os
import glob
from typing import List, Optional
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Document, Settings, StorageContext
from llama_index.embeddings.voyageai import VoyageEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.node_parser import SimpleNodeParser
import chromadb

load_dotenv()

class VectorStoreService:
    def __init__(self):
        # Initialize Voyage AI embeddings with voyage-3-lite
        self.embed_model = VoyageEmbedding(
            api_key=os.getenv("VOYAGE_API_KEY"),
            model_name="voyage-3-lite"
        )
        
        # Set global settings - this is crucial for query time
        Settings.embed_model = self.embed_model
        
        # Get paths from environment
        self.obsidian_path = os.getenv("OBSIDIAN_VAULT_PATH")
        self.code_path = os.getenv("CODE_PATH")
        
        # Initialize node parser for chunking
        self.node_parser = SimpleNodeParser.from_defaults(
            chunk_size=512,
            chunk_overlap=50
        )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Initialize indexes (will be None if paths don't exist)
        self.obsidian_index = None
        
        # Try to load existing index or build new one
        self._initialize_obsidian_index()
    
    def _initialize_obsidian_index(self):
        """Initialize Obsidian index - try to load existing or build new"""
        try:
            # Try to load existing collection
            collection = self.chroma_client.get_collection("obsidian_notes")
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            # Create StorageContext from existing vector store
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create index from existing vector store with StorageContext
            self.obsidian_index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            
        except Exception as e:
            if self.build_obsidian_index():
                pass  # Index built successfully
            else:
                pass  # Search will be unavailable
    
    def _load_obsidian_documents(self) -> List[Document]:
        """Load all markdown files from Obsidian vault"""
        if not self.obsidian_path or not os.path.exists(self.obsidian_path):
            return []
        
        documents = []
        
        for md_file in glob.glob(f"{self.obsidian_path}/**/*.md", recursive=True):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Skip empty files
                    if not content.strip():
                        continue
                    
                    # Skip very short files (less than 10 characters)
                    if len(content.strip()) < 10:
                        continue
                    
                    # Create document with metadata
                    doc = Document(
                        text=content,
                        metadata={
                            'filename': os.path.basename(md_file),
                            'filepath': md_file,
                            'file_type': 'markdown',
                            'source': 'obsidian'
                        }
                    )
                    documents.append(doc)
                
            except Exception as e:
                continue
        
        return documents
    
    def build_obsidian_index(self) -> bool:
        """Build vector index for Obsidian vault"""
        # Load documents
        documents = self._load_obsidian_documents()
        
        if not documents:
            return False
        
        try:
            # Clear existing collection
            try:
                self.chroma_client.delete_collection("obsidian_notes")
            except:
                pass
            
            # Create ChromaDB collection and vector store
            collection = self.chroma_client.get_or_create_collection("obsidian_notes")
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            # Create StorageContext with the vector store
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Build index with StorageContext
            self.obsidian_index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                node_parser=self.node_parser,
                embed_model=self.embed_model,
                show_progress=False
            )
            
            return True
            
        except Exception as e:
            return False
    
    def search_obsidian(self, query: str, top_k: int = 3, min_similarity: float = 0.7) -> List[str]:
        """Search Obsidian vault using vector similarity with minimum score threshold"""
        # If no index, try to build it
        if not self.obsidian_index:
            if not self.build_obsidian_index():
                return []
        
        try:
            # Use retriever with similarity cutoff
            retriever = self.obsidian_index.as_retriever(
                similarity_top_k=top_k,
                similarity_cutoff=min_similarity  # Only return results above this threshold
            )
            
            # Retrieve similar nodes
            nodes = retriever.retrieve(query)
            
            if not nodes:
                return []
            
            results = []
            for node in nodes:
                filename = node.metadata.get('filename', 'Unknown')
                # Truncate content for context
                content = node.text[:500] + "..." if len(node.text) > 500 else node.text
                results.append(f"From: {filename}\n{content}")
            
            return results
        
        except Exception as e:
            return []
    
    def has_index(self) -> bool:
        """Check if index is available"""
        return self.obsidian_index is not None
    
    def get_index_stats(self) -> dict:
        """Get statistics about the current index"""
        if not self.obsidian_index:
            return {"status": "no_index", "documents": 0}
        
        try:
            # Get collection info from ChromaDB
            collection = self.chroma_client.get_collection("obsidian_notes")
            doc_count = collection.count()
            
            return {
                "status": "ready",
                "documents": doc_count,
                "obsidian_path": self.obsidian_path
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "documents": 0}