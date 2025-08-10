import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables once at module level
load_dotenv()

class AgentConfig:
    """Configuration settings for the Learning Agent"""
    
    def __init__(self):
        """Initialize instance with configuration values"""
        # LLM Settings
        self.LLM_MODEL: str = "claude-sonnet-4-20250514"
        self.LLM_TEMPERATURE: float = 0.1
        self.LLM_MAX_TOKENS: int = 20000
        
        # Agent Settings
        self.MAX_TOOL_ITERATIONS: int = 5
        self.MAX_CONVERSATION_HISTORY: int = 2
        self.ENABLE_TOOL_DEBUGGING: bool = False
        
        # Vector Store Settings
        self.CHROMA_COLLECTION_NAME: str = "obsidian_notes"
        self.EMBED_MODEL: str = "voyage-context-3"
        self.VECTOR_SEARCH_TOP_K: int = 3
        self.VECTOR_SIMILARITY_THRESHOLD: float = 0.4
        self.NODE_CHUNK_SIZE: int = 512
        self.NODE_CHUNK_OVERLAP: int = 50
        
        # Load from environment (self = this specific config instance)
        self.OBSIDIAN_VAULT_PATH: str = os.getenv("OBSIDIAN_VAULT_PATH", "")
        self.OBSIDIAN_DAILY_NOTES_FOLDER: str = "Daily Notes"
        self.ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.VOYAGE_API_KEY: str = os.getenv("VOYAGE_API_KEY", "")
        
        # Conversation Settings
        self.CONVERSATION_HISTORY_DIR: str = "conversation_history"
        self.AUTO_SAVE_CONVERSATIONS: bool = True
        self.SAVE_RAW_CONVERSATIONS: bool = True      # Keep JSON logs  
        self.SAVE_SUMMARIES_TO_OBSIDIAN: bool = True  # Also save formatted summaries
    
    def validate_config(self) -> list[str]:  
        """Validate required configuration and return any errors"""
        errors = []
        
        if not self.ANTHROPIC_API_KEY:  # self = this instance
            errors.append("ANTHROPIC_API_KEY not found in environment variables")
        
        if not self.VOYAGE_API_KEY:
            errors.append("VOYAGE_API_KEY not found in environment variables")
        
        if not self.OBSIDIAN_VAULT_PATH:
            errors.append("OBSIDIAN_VAULT_PATH not found in environment variables")
        elif not Path(self.OBSIDIAN_VAULT_PATH).exists():
            errors.append(f"Obsidian vault path does not exist: {self.OBSIDIAN_VAULT_PATH}")
        
        return errors
    
    def print_config_summary(self):  # Note: no @classmethod, uses self
        """Print current configuration (without sensitive data)"""
        print("🔧 Agent Configuration:")
        print(f"  LLM Model: {self.LLM_MODEL}")
        print(f"  Temperature: {self.LLM_TEMPERATURE}")
        print(f"  Max Conversation History: {self.MAX_CONVERSATION_HISTORY}")
        print(f"  Vector Search Top K: {self.VECTOR_SEARCH_TOP_K}")
        print(f"  Similarity Threshold: {self.VECTOR_SIMILARITY_THRESHOLD}")
        print(f"  Vault Path: {self.OBSIDIAN_VAULT_PATH if self.OBSIDIAN_VAULT_PATH else 'NOT SET'}")
        print(f"  API Keys: {'✅ Set' if self.ANTHROPIC_API_KEY and self.VOYAGE_API_KEY else '❌ Missing'}")

# Create single global config instance
config = AgentConfig()