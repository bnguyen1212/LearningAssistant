from typing import Dict, List
from datetime import datetime

from graph.state import ConversationState, Message
from services.llm_service import LLMService

class AnalysisNodes:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def generate_session_summary(self, state: ConversationState) -> ConversationState:
        """Generate comprehensive session summary with topics"""
        
        conversation = state["full_conversation"]
        
        if not conversation or len(conversation) < 2:
            state["generated_notes"] = {}
            state["identified_topics"] = []  # Store topics here
            return state
        
        try:
            # Convert to format for LLM
            conversation_messages = [
                {"role": msg.role, "content": msg.content} 
                for msg in conversation
            ]
            
            # Extract topics BEFORE generating summary
            topics = self.llm_service.extract_conversation_topics(conversation_messages)
            state["identified_topics"] = topics
            
            # Generate summary (existing logic)
            session_summary = self.llm_service.generate_session_summary(conversation_messages)
            
            state["generated_notes"] = {
                "Learning Session": session_summary
            }
            
            return state
            
        except Exception as e:
            print(f"❌ Error generating session summary: {e}")
            state["generated_notes"] = {}
            state["identified_topics"] = []
            return state
    
    def validate_generated_content(self, state: ConversationState) -> ConversationState:
        """
        Validate that we have session summary to save
        """
        notes = state["generated_notes"]
        
        print("\n" + "=" * 50)
        print("📊 SESSION SUMMARY GENERATION")
        print("=" * 50)
        
        if not notes:
            print("❌ No session summary generated")
            return state
        
        session_content = notes.get("Learning Session", "")
        if session_content:
            print(f"✅ Session summary generated")
            print(f"📄 Content length: {len(session_content)} characters")
            print(f"📋 Preview: {session_content[:150]}...")
        else:
            print("❌ Session summary is empty")
        
        print("\n" + "=" * 50)
        print("✅ Ready to save session summary!")
        
        return state
    
    def check_analysis_complete(self, state: ConversationState) -> str:
        """
        Conditional edge: check if session summary generation is complete
        """
        if state["generated_notes"]:
            return "save_notes"
        else:
            return "analysis_failed"
    
    def handle_analysis_failure(self, state: ConversationState) -> ConversationState:
        """
        Handle case where session summary generation failed
        """
        print("❌ Session summary generation failed")
        print("💬 Continuing conversation without saving notes")
        
        # Reset note-related state
        state["note_request_detected"] = False
        state["identified_topics"] = []
        state["generated_notes"] = {}
        
        return state