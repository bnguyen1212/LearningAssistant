from typing import TypedDict, List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    """Single message in conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    
class ConversationState(TypedDict):
    """State for managing conversation and note generation"""
    
    # Full conversation history (for complete analysis)
    full_conversation: List[Message]
    
    # Recent context window (last 3 messages for LLM)
    recent_messages: List[Message]
    
    # Current interaction data
    current_user_message: str
    relevant_context: List[str]  # From vector search
    llm_response: str
    
    # Note generation trigger and results
    note_request_detected: bool
    identified_topics: List[str]
    generated_notes: Dict[str, str]  # topic -> note content
    obsidian_save_paths: List[str]
    
    # Processing flags
    reindexing_complete: bool