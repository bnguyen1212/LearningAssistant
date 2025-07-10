import os
import glob
from typing import List, Optional
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, Document, Settings
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
        
    def _load_obsidian_documents(self) -> List[Document]:
        """Load all markdown files from Obsidian vault"""
        if not self.obsidian_path or not os.path.exists(self.obsidian_path):
            print(f"Obsidian path not found: {self.obsidian_path}")
            return []
        
        documents = []
        print(f"Loading documents from: {self.obsidian_path}")
        
        for md_file in glob.glob(f"{self.obsidian_path}/**/*.md", recursive=True):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Skip empty files
                    if not content.strip():
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
                print(f"Error reading {md_file}: {e}")
                continue
        
        print(f"Loaded {len(documents)} documents from Obsidian vault")
        return documents
    
    def build_obsidian_index(self) -> bool:
        """Build vector index for Obsidian vault"""
        documents = self._load_obsidian_documents()
        
        if not documents:
            print("No documents found to index")
            return False
        
        try:
            # Clear any existing collection to start fresh
            try:
                self.chroma_client.delete_collection("obsidian_notes")
            except:
                pass  # Collection might not exist
            
            # Create ChromaDB collection
            collection = self.chroma_client.get_or_create_collection("obsidian_notes")
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            # Build index with chunking - explicitly pass embed_model
            print("Building vector index...")
            self.obsidian_index = VectorStoreIndex.from_documents(
                documents,
                vector_store=vector_store,
                node_parser=self.node_parser,
                embed_model=self.embed_model,  # Explicitly pass the embedding model
                show_progress=True
            )
            
            print("✅ Obsidian index built successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error building index: {e}")
            return False
    
    def search_obsidian(self, query: str, top_k: int = 3) -> List[str]:
        """Search Obsidian vault using vector similarity"""
        if not self.obsidian_index:
            print("Index not built. Call build_obsidian_index() first.")
            return []
        
        try:
            # Use retriever instead of query engine to avoid LLM requirements
            retriever = self.obsidian_index.as_retriever(
                similarity_top_k=top_k
            )
            
            # Retrieve similar nodes
            nodes = retriever.retrieve(query)
            
            results = []
            for node in nodes:
                filename = node.metadata.get('filename', 'Unknown')
                score = node.score if hasattr(node, 'score') else 'N/A'
                results.append(f"File: {filename} (Score: {score})\n{node.text[:600]}...")
            
            return results
            
        except Exception as e:
            print(f"Error searching: {e}")
            return []