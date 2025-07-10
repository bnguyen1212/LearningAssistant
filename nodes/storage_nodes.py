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
        Save generated notes to Obsidian vault with LLM-generated organization
        """
        print("💾 Saving notes to Obsidian vault...")
        
        notes_dict = state["generated_notes"]
        
        if not notes_dict:
            print("❌ No notes to save")
            state["obsidian_save_paths"] = []
            return state
        
        try:
            # Save all notes using the obsidian service
            saved_paths = self.obsidian_service.save_multiple_notes(notes_dict)
            state["obsidian_save_paths"] = saved_paths
            
            print(f"\n✅ Successfully saved {len(saved_paths)} notes:")
            for path in saved_paths:
                print(f"   📄 {path}")
            
        except Exception as e:
            print(f"❌ Error saving notes: {e}")
            state["obsidian_save_paths"] = []
        
        return state
    
    def reindex_knowledge_base(self, state: ConversationState) -> ConversationState:
        """
        Re-index the vector store with new notes (non-blocking)
        """
        saved_paths = state["obsidian_save_paths"]
        
        if not saved_paths:
            print("⚠️ No new notes to index")
            state["reindexing_complete"] = True
            return state
        
        print("🔄 Starting knowledge base re-indexing...")
        
        def reindex_async():
            """Run re-indexing in background thread"""
            try:
                print("   📊 Rebuilding vector index with new notes...")
                success = self.vector_service.build_obsidian_index()
                
                if success:
                    print("   ✅ Re-indexing completed successfully!")
                    print("   🔍 New notes are now searchable in future conversations")
                else:
                    print("   ❌ Re-indexing failed")
                    
            except Exception as e:
                print(f"   ❌ Re-indexing error: {e}")
        
        # Start re-indexing in background thread (non-blocking)
        reindex_thread = threading.Thread(target=reindex_async, daemon=True)
        reindex_thread.start()
        
        # Mark as started (don't wait for completion)
        state["reindexing_complete"] = True
        print("🚀 Re-indexing started in background")
        
        return state
    
    def finalize_note_saving(self, state: ConversationState) -> ConversationState:
        """
        Finalize the note saving process and provide summary
        """
        saved_paths = state["obsidian_save_paths"]
        notes_count = len(saved_paths)
        
        print("\n" + "=" * 60)
        print("📚 NOTE SAVING COMPLETE")
        print("=" * 60)
        
        if notes_count > 0:
            print(f"✅ Successfully saved {notes_count} learning notes")
            print(f"📁 Notes organized in your Obsidian vault:")
            
            for path in saved_paths:
                # Extract just the relative path from vault for cleaner display
                relative_path = path.replace(str(self.obsidian_service.vault_path), "")
                print(f"   📄 {relative_path}")
            
            print("\n🔄 Vector index updated - new notes are searchable")
            print("💬 Ready for new conversation!")
            
        else:
            print("❌ No notes were saved")
        
        print("=" * 60)
        
        return state
    
    def check_save_success(self, state: ConversationState) -> str:
        """
        Conditional edge: check if notes were saved successfully
        """
        if state["obsidian_save_paths"]:
            return "save_success"
        else:
            return "save_failed"
    
    def handle_save_failure(self, state: ConversationState) -> ConversationState:
        """
        Handle case where note saving failed
        """
        print("❌ Failed to save notes to Obsidian vault")
        print("💬 Your conversation content is preserved, you can try again")
        
        # Don't clear the generated notes in case user wants to retry
        # Just reset the save-related flags
        state["obsidian_save_paths"] = []
        state["reindexing_complete"] = False
        
        return state
    
    def show_save_summary(self, state: ConversationState) -> ConversationState:
        """
        Show a final summary of what was accomplished
        """
        topics = state["identified_topics"]
        notes = state["generated_notes"]
        saved_paths = state["obsidian_save_paths"]
        
        print("\n" + "🎉" * 20)
        print("LEARNING SESSION COMPLETE")
        print("🎉" * 20)
        
        print(f"\n📊 Session Summary:")
        print(f"   💬 Messages in conversation: {len(state['full_conversation'])}")
        print(f"   🎯 Topics identified: {len(topics)}")
        print(f"   📝 Notes generated: {len(notes)}")
        print(f"   💾 Files saved: {len(saved_paths)}")
        
        if topics:
            print(f"\n📋 Topics covered:")
            for i, topic in enumerate(topics, 1):
                print(f"   {i}. {topic}")
        
        print(f"\n✨ Your knowledge base has been expanded!")
        print(f"🔄 New content is now searchable for future learning")
        
        return state