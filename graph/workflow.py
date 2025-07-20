import os
from typing import Dict, Any
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END

from graph.state import ConversationState
from services.vector_store import VectorStoreService
from services.llm_service import LLMService
from services.obsidian_service import ObsidianService
from nodes.chat_nodes import ChatNodes
from nodes.analysis_nodes import AnalysisNodes
from nodes.storage_nodes import StorageNodes

load_dotenv()

class LearningWorkflow:
    def __init__(self):
        # Initialize services
        self.vector_service = VectorStoreService()
        self.llm_service = LLMService()
        self.obsidian_service = ObsidianService(
            vault_path=os.getenv("OBSIDIAN_VAULT_PATH"),
            llm_service=self.llm_service
        )
        
        # Initialize node classes
        self.chat_nodes = ChatNodes(self.vector_service, self.llm_service)
        self.analysis_nodes = AnalysisNodes(self.llm_service)
        self.storage_nodes = StorageNodes(self.obsidian_service, self.vector_service)
        
        # Build the workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """
        Build and compile the LangGraph workflow
        """
        # Create the state graph
        graph = StateGraph(ConversationState)
        
        # Add nodes - UPDATED FOR SESSION-BASED APPROACH
        graph.add_node("chat_with_context", self.chat_nodes.chat_with_context)
        graph.add_node("generate_summary", self.analysis_nodes.generate_session_summary)  # Changed from analyze_topics
        graph.add_node("validate_content", self.analysis_nodes.validate_generated_content)
        graph.add_node("save_notes", self.storage_nodes.save_notes_to_obsidian)
        graph.add_node("reindex_kb", self.storage_nodes.reindex_knowledge_base)
        graph.add_node("finalize_save", self.storage_nodes.finalize_note_saving)
        graph.add_node("show_summary", self.storage_nodes.show_save_summary)
        graph.add_node("clear_conversation", self.chat_nodes.clear_conversation)
        graph.add_node("handle_analysis_failure", self.analysis_nodes.handle_analysis_failure)
        graph.add_node("handle_save_failure", self.storage_nodes.handle_save_failure)
        
        # Set entry point
        graph.set_entry_point("chat_with_context")
        
        # Add conditional edges - UPDATED WORKFLOW
        graph.add_conditional_edges(
            "chat_with_context",
            self.chat_nodes.should_generate_notes,
            {
                "generate_notes": "generate_summary",  # Changed from "analyze_topics"
                "continue_chat": END
            }
        )
        
        graph.add_conditional_edges(
            "validate_content", 
            self.analysis_nodes.check_analysis_complete,
            {
                "save_notes": "save_notes",
                "analysis_failed": "handle_analysis_failure"
            }
        )
        
        graph.add_conditional_edges(
            "finalize_save",
            self.storage_nodes.check_save_success,
            {
                "save_success": "reindex_kb",
                "save_failed": "handle_save_failure"
            }
        )
        
        # Add sequential edges - SIMPLIFIED WORKFLOW
        graph.add_edge("generate_summary", "validate_content")  # Direct from summary to validation
        graph.add_edge("save_notes", "finalize_save")
        graph.add_edge("reindex_kb", "show_summary")
        graph.add_edge("show_summary", "clear_conversation")
        graph.add_edge("clear_conversation", END)
        graph.add_edge("handle_analysis_failure", END)
        graph.add_edge("handle_save_failure", END)
        
        # Compile the graph
        return graph.compile()
    
    def create_initial_state(self, user_message: str) -> ConversationState:
        """
        Create initial state for a new conversation turn
        """
        return {
            "full_conversation": [],
            "recent_messages": [],
            "current_user_message": user_message,
            "relevant_context": [],
            "llm_response": "",
            "note_request_detected": False,
            "identified_topics": [],  # Still in state for compatibility but unused
            "generated_notes": {},
            "obsidian_save_paths": [],
            "reindexing_complete": False
        }
    
    def chat(self, user_message: str, existing_state: ConversationState = None) -> ConversationState:
        """
        Process a user message through the workflow
        """
        if existing_state is None:
            state = self.create_initial_state(user_message)
        else:
            # Update existing state with new message
            state = existing_state.copy()
            state["current_user_message"] = user_message
            # Reset note-related fields for new interaction
            state["relevant_context"] = []
            state["llm_response"] = ""
        
        # Run through the workflow
        result = self.workflow.invoke(state)
        return result
    
    def get_workflow_image(self, output_path: str = "workflow_diagram.png") -> str:
        """
        Generate and save a visual representation of the workflow
        """
        try:
            # Get the workflow visualization
            img_data = self.workflow.get_graph().draw_mermaid_png()
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(img_data)
            
            print(f"✅ Workflow diagram saved to: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Failed to generate workflow diagram: {e}")
            return ""

# Factory function for easy workflow creation
def create_learning_workflow() -> LearningWorkflow:
    """
    Factory function to create and initialize the learning workflow
    """
    return LearningWorkflow()