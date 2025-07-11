import sys
import os

# Add the parent directory (LearningAssistant) to the Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from services.vector_store import VectorStoreService
from dotenv import load_dotenv

load_dotenv()

def test_vector_store():
    """Test the VectorStoreService functionality"""
    
    print("🚀 Testing Vector Store Service")
    print("=" * 50)
    
    # Initialize service
    print("1. Initializing VectorStoreService...")
    service = VectorStoreService()
    
    # Check if Obsidian path exists
    if not service.obsidian_path:
        print("❌ OBSIDIAN_VAULT_PATH not set in .env")
        return
    
    if not os.path.exists(service.obsidian_path):
        print(f"❌ Obsidian path doesn't exist: {service.obsidian_path}")
        return
    
    print(f"✅ Obsidian path found: {service.obsidian_path}")
    
    # Test document loading
    print("\n2. Loading documents...")
    documents = service._load_obsidian_documents()
    
    if not documents:
        print("❌ No documents found. Please add some .md files to your Obsidian vault.")
        return
    
    print(f"✅ Loaded {len(documents)} documents")
    
    # Show first document preview
    if documents:
        first_doc = documents[0]
        print(f"\n📄 First document preview:")
        print(f"   Filename: {first_doc.metadata['filename']}")
        print(f"   Content preview: {first_doc.text[:200]}...")
    
    # Test indexing
    print("\n3. Building vector index...")
    success = service.build_obsidian_index()
    
    if not success:
        print("❌ Failed to build index")
        return
    
    print("✅ Index built successfully!")
    
    # Test search
    print("\n4. Testing search functionality...")
    
    test_queries = [
        "machine learning",
        "python programming",
        "deep learning neural networks",
        "data science"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = service.search_obsidian(query, top_k=2)
        
        if results:
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   \n   Result {i}:")
                #print(f"   {result}")
        else:
            print("   No results found")
    
    print("\n" + "=" * 50)
    print("✅ Vector store test completed!")

if __name__ == "__main__":
    test_vector_store()