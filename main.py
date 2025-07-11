import sys
import os
from typing import Optional

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from graph.workflow import create_learning_workflow
from graph.state import ConversationState
from dotenv import load_dotenv

load_dotenv()

class LearningAssistantInterface:
    def __init__(self):
        print("🚀 Initializing Learning Assistant...")
        try:
            self.workflow = create_learning_workflow()
            self.current_state: Optional[ConversationState] = None
            print("✅ Learning Assistant ready!")
            self.show_welcome()
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            sys.exit(1)
    
    def show_welcome(self):
        """Display welcome message and instructions"""
        print("\n" + "=" * 60)
        print("🎓 CONVERSATIONAL LEARNING ASSISTANT")
        print("=" * 60)
        print("💬 Chat naturally about any topic")
        print("🔍 I'll search your knowledge base for relevant context")
        print("📝 Say 'save this as notes' to capture learning insights")
        print("❌ Type 'quit', 'exit', or 'bye' to end")
        print("🔄 Type 'new' to start fresh conversation")
        print("=" * 60)
        print()
    
    def process_user_input(self, user_input: str) -> bool:
        """
        Process user input and return False if should quit
        """
        user_input = user_input.strip()
        
        # Handle special commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye! Happy learning!")
            return False
        
        if user_input.lower() == 'new':
            self.current_state = None
            print("🆕 Starting fresh conversation...")
            return True
        
        if user_input.lower() in ['help', '?']:
            self.show_welcome()
            return True
        
        if not user_input:
            print("💭 Please enter a message...")
            return True
        
        # Process through workflow
        try:
            print("\n🤔 Thinking...")
            
            # Run the workflow
            self.current_state = self.workflow.chat(user_input, self.current_state)
            
            # Display the response immediately if available
            response = self.current_state.get("llm_response", "")
            if response:
                print(f"\n🤖 Assistant: {response}")
            
            # Check if notes were generated and workflow completed
            if self.current_state.get("obsidian_save_paths"):
                print("\n📚 Notes have been saved to your Obsidian vault!")
                print("💬 Ready for a new conversation!")
                
                # Clear state for fresh start
                self.current_state = None
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏸️ Interrupted by user")
            return True
        except Exception as e:
            print(f"\n❌ Error processing message: {e}")
            print("💬 You can continue the conversation...")
            return True
    
    def run(self):
        """
        Main conversation loop
        """
        try:
            while True:
                # Get user input
                try:
                    user_input = input("\n💭 You: ")
                except KeyboardInterrupt:
                    print("\n👋 Goodbye!")
                    break
                except EOFError:
                    print("\n👋 Goodbye!")
                    break
                
                # Process input
                should_continue = self.process_user_input(user_input)
                if not should_continue:
                    break
                
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("👋 Exiting...")

def main():
    """
    Entry point for the Learning Assistant
    """
    try:
        assistant = LearningAssistantInterface()
        assistant.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Failed to start Learning Assistant: {e}")

if __name__ == "__main__":
    main()
