from typing import Dict, List
from datetime import datetime

from graph.state import ConversationState, Message
from services.llm_service import LLMService

class AnalysisNodes:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def generate_session_summary(self, state: ConversationState) -> ConversationState:
        """
        Generate a single comprehensive session summary from the full conversation
        """
        print("📝 Generating session summary...")
        
        # Convert full conversation to format expected by LLM service
        conversation_dict = []
        for msg in state["full_conversation"]:
            conversation_dict.append({
                "role": msg.role,
                "content": msg.content
            })
        
        if not conversation_dict:
            print("⚠️ No conversation to summarize")
            state["generated_notes"] = {}
            return state
        
        try:
            # Generate session summary using LLM
            session_content = self.llm_service.generate_session_summary(conversation_dict)
            
            if session_content:
                # Use a single "Learning Session" key for the session summary
                state["generated_notes"] = {"Learning Session": session_content}
                print(f"✅ Generated session summary ({len(session_content)} chars)")
            else:
                print("❌ Failed to generate session summary")
                state["generated_notes"] = {}
                
        except Exception as e:
            print(f"❌ Error generating session summary: {e}")
            state["generated_notes"] = {}
        
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