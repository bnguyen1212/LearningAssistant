from typing import Dict, List
from datetime import datetime

from graph.state import ConversationState, Message
from services.vector_store import VectorStoreService
from services.llm_service import LLMService

class ChatNodes:
    def __init__(self, vector_service: VectorStoreService, llm_service: LLMService):
        self.vector_service = vector_service
        self.llm_service = llm_service
    
    def chat_with_context(self, state: ConversationState) -> ConversationState:
        """
        Generate chat response OR skip directly to summary if note request detected
        """
        # Check if note request was detected - if so, skip chat and prep for summary
        if state.get("note_request_detected", False):
            print("📝 Note request detected - preparing for summary generation...")
            
            # Set minimal required state for summary generation
            state["llm_response"] = "Generating session summary..."
            
            # Don't search for new context - we'll use existing conversation
            return state
        
        # Normal chat flow when no note request
        user_message = state["current_user_message"]
        conversation_history = state["recent_messages"]
        
        # Search for relevant context and track referenced files
        relevant_context, referenced_files = self.vector_service.search_obsidian(user_message, top_k=3)
        
        # Store referenced files in state
        state["referenced_files"] = state.get("referenced_files", set())
        state["referenced_files"].update(referenced_files)
        
        # Store relevant context in state
        state["relevant_context"] = relevant_context
        
        try:
            # Use the existing LLMService method
            response = self.llm_service.chat_with_context(
                user_message=user_message,
                recent_messages=conversation_history,
                relevant_context=relevant_context
            )
            
            state["llm_response"] = response
            
            print(f"🔗 Referenced files: {', '.join(referenced_files) if referenced_files else 'None'}")
            
            return state
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            state["llm_response"] = "I encountered an error generating a response. Please try again."
            return state
    