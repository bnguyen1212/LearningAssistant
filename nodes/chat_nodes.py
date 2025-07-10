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
        Main chat node: search for context and respond to user
        """
        user_message = state["current_user_message"]
        
        # Search for relevant context from knowledge base
        print(f"🔍 Searching knowledge base for: '{user_message[:50]}...'")
        relevant_context = self.vector_service.search_obsidian(user_message, top_k=3)
        
        # Get recent messages for LLM context (last 3)
        recent_messages = []
        if state["full_conversation"]:
            # Convert Message objects to dict format for LLM service
            recent_msgs = state["full_conversation"][-6:]  # Last 6 messages (3 exchanges)
            recent_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in recent_msgs
            ]
        
        # Get LLM response
        print("💭 Generating response...")
        llm_response = self.llm_service.chat_with_context(
            user_message=user_message,
            recent_messages=recent_messages,
            relevant_context=relevant_context
        )
        
        # Create message objects
        user_msg = Message(
            role="user",
            content=user_message,
            timestamp=datetime.now()
        )
        
        assistant_msg = Message(
            role="assistant", 
            content=llm_response,
            timestamp=datetime.now()
        )
        
        # Update state
        state["full_conversation"].append(user_msg)
        state["full_conversation"].append(assistant_msg)
        
        # Update recent messages (last 6 messages for next iteration)
        state["recent_messages"] = state["full_conversation"][-6:]
        
        state["relevant_context"] = relevant_context
        state["llm_response"] = llm_response
        
        # Check if user requested note generation
        note_requested = self.llm_service.detect_note_request(user_message)
        state["note_request_detected"] = note_requested
        
        if note_requested:
            print("📝 Note generation requested!")
        
        return state
    
    def should_generate_notes(self, state: ConversationState) -> str:
        """
        Conditional edge: determine if we should generate notes or continue chatting
        """
        if state["note_request_detected"]:
            return "generate_notes"
        else:
            return "continue_chat"
    
    def clear_conversation(self, state: ConversationState) -> ConversationState:
        """
        Clear conversation after notes are saved (fresh start)
        """
        print("🧹 Clearing conversation history for fresh start...")
        
        state["full_conversation"] = []
        state["recent_messages"] = []
        state["current_user_message"] = ""
        state["relevant_context"] = []
        state["llm_response"] = ""
        state["note_request_detected"] = False
        state["identified_topics"] = []
        state["generated_notes"] = {}
        state["obsidian_save_paths"] = []
        state["reindexing_complete"] = False
        
        return state