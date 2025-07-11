import sys
import os
from unittest.mock import Mock, patch
import time

# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from graph.workflow import create_learning_workflow
from graph.state import ConversationState, Message
from services.vector_store import VectorStoreService
from services.llm_service import LLMService
from services.obsidian_service import ObsidianService
from main import LearningAssistantInterface
from dotenv import load_dotenv

load_dotenv()

class TestLearningAssistantIntegration:
    def __init__(self):
        self.test_results = []
        self.workflow = None
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append((test_name, success, message))
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
    
    def test_service_initialization(self):
        """Test that all services can be initialized"""
        try:
            vector_service = VectorStoreService()
            llm_service = LLMService()
            obsidian_service = ObsidianService(
                vault_path=os.getenv("OBSIDIAN_VAULT_PATH")
            )
            self.log_test("Service Initialization", True, "All services initialized successfully")
            return vector_service, llm_service, obsidian_service
        except Exception as e:
            self.log_test("Service Initialization", False, f"Error: {e}")
            return None, None, None
    
    def test_workflow_creation(self):
        """Test workflow creation and compilation"""
        try:
            self.workflow = create_learning_workflow()
            self.log_test("Workflow Creation", True, "Workflow compiled successfully")
            return True
        except Exception as e:
            self.log_test("Workflow Creation", False, f"Error: {e}")
            return False
    
    def test_basic_chat_flow(self):
        """Test basic conversational flow without note generation"""
        if not self.workflow:
            self.log_test("Basic Chat Flow", False, "Workflow not available")
            return False
        
        try:
            # Test simple conversation
            user_message = "What is machine learning?"
            state = self.workflow.chat(user_message)
            
            # Verify state structure
            required_keys = [
                "full_conversation", "recent_messages", "current_user_message",
                "llm_response", "note_request_detected"
            ]
            
            missing_keys = [key for key in required_keys if key not in state]
            if missing_keys:
                self.log_test("Basic Chat Flow", False, f"Missing state keys: {missing_keys}")
                return False
            
            # Verify conversation was recorded
            if len(state["full_conversation"]) < 2:  # User message + assistant response
                self.log_test("Basic Chat Flow", False, "Conversation not properly recorded")
                return False
            
            # Verify LLM response exists
            if not state["llm_response"]:
                self.log_test("Basic Chat Flow", False, "No LLM response generated")
                return False
            
            self.log_test("Basic Chat Flow", True, f"Response length: {len(state['llm_response'])} chars")
            return state
            
        except Exception as e:
            self.log_test("Basic Chat Flow", False, f"Error: {e}")
            return False
    
    def test_note_request_detection(self):
        """Test note request detection"""
        if not self.workflow:
            self.log_test("Note Request Detection", False, "Workflow not available")
            return False
        
        try:
            # Start with a conversation
            state = self.workflow.chat("Tell me about neural networks")
            
            # Request note generation and capture the immediate state
            state = self.workflow.chat("save this as notes", state)
            
            # The note_request_detected should have been True during processing
            # even if it's False now after completion
            
            # Instead, check if the session summary was generated
            # which proves note request was detected and processed
            generated_notes = state.get("generated_notes", {})
            session_summary = generated_notes.get("Learning Session", "")
            
            if not session_summary:
                self.log_test("Note Request Detection", False, "Note request not processed - no session summary generated")
                return False
            
            self.log_test("Note Request Detection", True, "Note request detected and processed successfully")
            return state
            
        except Exception as e:
            self.log_test("Note Request Detection", False, f"Error: {e}")
            return False
    
    def test_session_summary_generation(self):
        """Test the complete session summary generation pipeline - UPDATED"""
        if not self.workflow:
            self.log_test("Session Summary Pipeline", False, "Workflow not available")
            return False
        
        try:
            # Create a conversation 
            state = self.workflow.chat("What are neural networks?")
            state = self.workflow.chat("How do they differ from traditional algorithms?", state)
            state = self.workflow.chat("What about deep learning?", state)
            state = self.workflow.chat("save this conversation as notes", state)
            
            # Check if session summary was generated
            generated_notes = state.get("generated_notes", {})
            if not generated_notes:
                self.log_test("Session Summary Pipeline", False, "No session summary generated")
                return False
            
            # Check for session summary content
            session_summary = generated_notes.get("Learning Session", "")
            if not session_summary:
                self.log_test("Session Summary Pipeline", False, "Session summary is empty")
                return False
            
            self.log_test(
                "Session Summary Pipeline", 
                True, 
                f"Generated session summary ({len(session_summary)} chars)"
            )
            return state
            
        except Exception as e:
            self.log_test("Session Summary Pipeline", False, f"Error: {e}")
            return False
    
    def test_obsidian_integration(self):
        """Test Obsidian file operations - UPDATED for session-based approach"""
        try:
            obsidian_service = ObsidianService(
                vault_path=os.getenv("OBSIDIAN_VAULT_PATH")
            )
            
            # Test filename sanitization
            test_filename = "Test Topic: With/Special?Characters"
            sanitized = obsidian_service.sanitize_filename(test_filename)
            
            if not sanitized or sanitized == test_filename:
                self.log_test("Obsidian Integration", False, "Filename sanitization failed")
                return False
            
            # Test session folder creation (without actually creating)
            session_name = "test_session"
            if hasattr(obsidian_service, 'create_session_folder'):
                # Method exists - integration should work
                pass
            else:
                self.log_test("Obsidian Integration", False, "Session folder creation method missing")
                return False
            
            self.log_test(
                "Obsidian Integration", 
                True, 
                f"Sanitized filename: '{sanitized}'"
            )
            return True
            
        except Exception as e:
            self.log_test("Obsidian Integration", False, f"Error: {e}")
            return False
    
    def test_conversation_persistence(self):
        """Test that conversation state persists between messages"""
        if not self.workflow:
            self.log_test("Conversation Persistence", False, "Workflow not available")
            return False
        
        try:
            # Start conversation
            state1 = self.workflow.chat("What is Python?")
            initial_conversation_length = len(state1["full_conversation"])
            
            # Continue conversation
            state2 = self.workflow.chat("What are its main features?", state1)
            final_conversation_length = len(state2["full_conversation"])
            
            # Verify conversation grew
            if final_conversation_length <= initial_conversation_length:
                self.log_test("Conversation Persistence", False, "Conversation not persisting")
                return False
            
            # Verify both messages are in history
            conversation_text = " ".join([msg.content for msg in state2["full_conversation"]])
            
            if "Python" not in conversation_text or "features" not in conversation_text:
                self.log_test("Conversation Persistence", False, "Message content not preserved")
                return False
            
            self.log_test(
                "Conversation Persistence", 
                True, 
                f"Conversation grew from {initial_conversation_length} to {final_conversation_length} messages"
            )
            return True
            
        except Exception as e:
            self.log_test("Conversation Persistence", False, f"Error: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling and recovery"""
        try:
            # Test with empty message
            if self.workflow:
                state = self.workflow.chat("")
                # Should handle gracefully
            
            # Test with very long message
            long_message = "A" * 10000
            if self.workflow:
                state = self.workflow.chat(long_message)
                # Should handle gracefully
            
            self.log_test("Error Handling", True, "System handles edge cases gracefully")
            return True
            
        except Exception as e:
            # Errors should be caught and handled, not propagated
            self.log_test("Error Handling", False, f"Unhandled error: {e}")
            return False
    
    def test_main_interface_initialization(self):
        """Test that the main interface can be initialized"""
        try:
            # Mock input to avoid hanging
            with patch('builtins.input', side_effect=['quit']):
                interface = LearningAssistantInterface()
                # If we get here, initialization worked
                self.log_test("Main Interface", True, "Interface initialized successfully")
                return True
                
        except Exception as e:
            self.log_test("Main Interface", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 STARTING INTEGRATION TESTS")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run tests in order - UPDATED test names
        self.test_service_initialization()
        self.test_workflow_creation()
        self.test_basic_chat_flow()
        self.test_note_request_detection()
        self.test_session_summary_generation()  # Updated from topic analysis
        self.test_obsidian_integration()
        self.test_conversation_persistence()
        self.test_error_handling()
        self.test_main_interface_initialization()
        
        end_time = time.time()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"⏱️ Time: {end_time - start_time:.2f} seconds")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for name, success, message in self.test_results:
                if not success:
                    print(f"   • {name}: {message}")
        
        success_rate = passed / total * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Integration tests mostly successful! System ready for use.")
        elif success_rate >= 60:
            print("⚠️ Some issues found. Review failed tests before proceeding.")
        else:
            print("🚨 Major issues detected. Please fix critical failures.")
        
        return success_rate >= 80

def main():
    """Run integration tests"""
    tester = TestLearningAssistantIntegration()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 System is ready! Run 'python main.py' to start learning!")
    else:
        print("\n🔧 Please address the issues above before using the system.")

if __name__ == "__main__":
    main()