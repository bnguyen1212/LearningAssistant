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
        """
        Save session summary to Obsidian vault organized by session
        """
        print("💾 Saving session summary to Obsidian vault...")
        
        notes_dict = state["generated_notes"]
        
        if not notes_dict:
            print("❌ No session summary to save")
            state["obsidian_save_paths"] = []
            return state
        
        try:
            # Generate session name from first few words of conversation
            if state["full_conversation"]:
                first_user_msg = next((msg.content for msg in state["full_conversation"] if msg.role == "user"), "")
                # Use first 3 words as session name
                session_words = first_user_msg.split()[:3]
                session_name = "_".join(session_words) if session_words else "learning_session"
            else:
                session_name = "learning_session"
            
            # Save session summary using the session-based approach
            saved_paths = self.obsidian_service.save_session_notes(notes_dict, session_name)
            state["obsidian_save_paths"] = saved_paths
            
            if saved_paths:
                print(f"\n✅ Successfully saved session summary")
                for path in saved_paths:
                    print(f"   📄 {path}")
            else:
                print("❌ No files were saved")
        
        except Exception as e:
            print(f"❌ Error saving session summary: {e}")
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