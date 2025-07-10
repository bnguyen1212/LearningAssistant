import sys
import os

# Add the parent directory (LearningAssistant) to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from services.vector_store import VectorStoreService
from services.llm_service import LLMService
from services.obsidian_service import ObsidianService
from dotenv import load_dotenv

load_dotenv()

def test_basic_integration():
    """Test basic integration of services"""
    
    print("🚀 Testing Basic Service Integration")
    print("=" * 50)
    
    # Test 1: Initialize all services
    print("1. Initializing services...")
    try:
        vector_service = VectorStoreService()
        llm_service = LLMService()
        obsidian_service = ObsidianService(
            vault_path=os.getenv("OBSIDIAN_VAULT_PATH"),
            llm_service=llm_service
        )
        print("✅ All services initialized successfully")
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return
    
    # Test 2: Test LLM service basic functionality
    print("\n2. Testing LLM service...")
    try:
        # Test note request detection
        is_request = llm_service.detect_note_request("save this as notes")
        print(f"✅ Note request detection: {is_request}")
        
        # Test basic chat (no context)
        response = llm_service.chat_with_context("What is machine learning?", [])
        print(f"✅ Basic chat response: {response[:100]}...")
        
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return
    
    # Test 3: Test Obsidian service
    print("\n3. Testing Obsidian service...")
    try:
        # Test filename sanitization
        sanitized = obsidian_service.sanitize_filename("Test Topic: With/Special?Characters")
        print(f"✅ Filename sanitization: {sanitized}")
        
        # Test category generation
        category = obsidian_service.generate_category_path("Machine Learning Basics")
        print(f"✅ Category generation: {category}")
        
    except Exception as e:
        print(f"❌ Obsidian service test failed: {e}")
        return
    
    print("\n" + "=" * 50)
    print("✅ Basic integration test completed successfully!")
    print("Ready to proceed to LangGraph workflow implementation.")

if __name__ == "__main__":
    test_basic_integration()