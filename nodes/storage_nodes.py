import threading
from typing import Dict, List

from graph.state import ConversationState
from services.obsidian_service import ObsidianService
from services.vector_store import VectorStoreService

class StorageNodes:
    def __init__(self, obsidian_service: ObsidianService, vector_service: VectorStoreService):
        self.obsidian_service = obsidian_service
        self.vector_service = vector_service
    
    def save_notes_to_obsidian(self, state: ConversationState) -> ConversationState:
        """Save generated notes to Obsidian vault with topic-based tags"""
        
        notes = state["generated_notes"]
        topics = state.get("identified_topics", [])  # Get extracted topics
        
        if not notes:
            state["obsidian_save_paths"] = []
            return state
        
        try:
            # Extract session name from first user message for folder naming
            conversation = state["full_conversation"]
            session_name = None
            if conversation:
                first_message = conversation[0].content
                session_name = first_message[:50]  # First 50 chars as session name
            
            # Save notes with topics as tags
            saved_paths = self.obsidian_service.save_session_notes(
                notes, 
                session_name,
                topics=topics  # Pass topics for tagging
            )
            
            state["obsidian_save_paths"] = saved_paths
            return state
            
        except Exception as e:
            print(f"❌ Error saving notes: {e}")
            state["obsidian_save_paths"] = []
            return state
    
    def reindex_knowledge_base(self, state: ConversationState) -> ConversationState:
        """
        Start asynchronous re-indexing of knowledge base
        """
        print("🔄 Starting knowledge base re-indexing...")
        
        def reindex_async():
            """Run re-indexing in background thread"""
            try:
                print("📊 Rebuilding vector index with new session summary...")
                success = self.vector_service.build_obsidian_index()
            except Exception as e:
                print(f"❌ Background re-indexing error: {e}")
        
        # Start re-indexing in background thread (non-blocking)
        import threading
        reindex_thread = threading.Thread(target=reindex_async, daemon=True)
        reindex_thread.start()
        
        # Show completion message immediately
        print("✅ Re-indexing started in background")
        
        state["reindexing_complete"] = True
        return state
    
    def finalize_note_saving(self, state: ConversationState) -> ConversationState:
        """
        Finalize the session summary saving process and provide summary
        """
        saved_paths = state["obsidian_save_paths"]
        
        print("\n" + "=" * 60)
        print("📚 SESSION SUMMARY SAVING COMPLETE")
        print("=" * 60)
        
        if saved_paths:
            print(f"✅ Successfully saved learning session summary")
            print(f"📁 Session summary saved to your Obsidian vault:")
            
            for path in saved_paths:
                # Extract just the relative path from vault for cleaner display
                relative_path = path.replace(str(self.obsidian_service.vault_path), "")
                print(f"   📄 {relative_path}")
            
            print("\n🔄 Vector index updated - session summary is searchable")
            print("💬 Ready for new conversation!")
            
        else:
            print("❌ No session summary was saved")
        
        print("=" * 60)
        
        return state
    
    def check_save_success(self, state: ConversationState) -> str:
        """
        Conditional edge: check if session summary was saved successfully
        """
        if state["obsidian_save_paths"]:
            return "save_success"
        else:
            return "save_failed"
    
    def handle_save_failure(self, state: ConversationState) -> ConversationState:
        """
        Handle case where session summary saving failed
        """
        print("❌ Failed to save session summary to Obsidian vault")
        print("💬 Your conversation content is preserved, you can try again")
        
        # Don't clear the generated summary in case user wants to retry
        # Just reset the save-related flags
        state["obsidian_save_paths"] = []
        state["reindexing_complete"] = False
        
        return state
    
    def show_save_summary(self, state: ConversationState) -> ConversationState:
        """
        Show a final summary of what was accomplished
        """
        notes = state["generated_notes"]
        saved_paths = state["obsidian_save_paths"]
        
        print("\n" + "🎉" * 20)
        print("LEARNING SESSION COMPLETE")
        print("🎉" * 20)
        
        print(f"\n📊 Session Summary:")
        print(f"   💬 Messages in conversation: {len(state['full_conversation'])}")
        print(f"   📝 Session summary generated: {'Yes' if notes else 'No'}")
        print(f"   💾 Files saved: {len(saved_paths)}")
        
        if notes:
            session_content = list(notes.values())[0]
            print(f"   📄 Summary length: {len(session_content)} characters")
        
        print(f"\n✨ Your knowledge base has been expanded!")
        print(f"🔄 Session summary is now searchable for future learning")
        
        return state