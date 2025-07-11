import sys
import os

# Add parent directory to Python path (go up one level from services folder)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from services.vector_store import VectorStoreService
from dotenv import load_dotenv
import glob

load_dotenv()

def debug_vault_contents(obsidian_path):
    """Debug what's actually in the vault"""
    print(f"\n🔍 DEBUGGING VAULT CONTENTS")
    print("=" * 50)
    print(f"📂 Vault path: {obsidian_path}")
    print(f"📂 Path exists: {os.path.exists(obsidian_path)}")
    print(f"📂 Is directory: {os.path.isdir(obsidian_path)}")
    
    # List all files in vault
    print(f"\n📄 All files in vault:")
    all_files = []
    for root, dirs, files in os.walk(obsidian_path):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)
            print(f"   {full_path}")
    
    print(f"\n📊 Total files found: {len(all_files)}")
    
    # Look specifically for .md files
    md_files = glob.glob(f"{obsidian_path}/**/*.md", recursive=True)
    print(f"📝 Markdown files found: {len(md_files)}")
    
    for md_file in md_files[:5]:  # Show first 5
        print(f"   📝 {md_file}")
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"      📏 Length: {len(content)} characters")
                if content.strip():
                    print(f"      📋 Preview: {content[:100]}...")
                else:
                    print(f"      ⚠️ File is empty")
        except Exception as e:
            print(f"      ❌ Error reading: {e}")
    
    if len(md_files) > 5:
        print(f"   ... and {len(md_files) - 5} more")

def main():
    """Build or rebuild the vector index for your Obsidian vault"""
    print("🚀 Building Vector Index for Obsidian Vault")
    print("=" * 50)
    
    # Check environment variables
    obsidian_path = os.getenv("OBSIDIAN_VAULT_PATH")
    voyage_key = os.getenv("VOYAGE_API_KEY")
    
    if not obsidian_path:
        print("❌ OBSIDIAN_VAULT_PATH not set in .env file")
        return
    
    if not voyage_key:
        print("❌ VOYAGE_API_KEY not set in .env file")
        return
    
    if not os.path.exists(obsidian_path):
        print(f"❌ Obsidian vault path does not exist: {obsidian_path}")
        return
    
    # Debug vault contents
    debug_vault_contents(obsidian_path)
    
    # Ask user if they want to continue
    print(f"\n❓ Continue with index building? (y/n): ", end="")
    response = input().lower().strip()
    
    if response != 'y':
        print("⏹️ Index building cancelled")
        return
    
    try:
        # Initialize vector store service
        print(f"\n🔄 Initializing vector store service...")
        vector_service = VectorStoreService()
        
        # Build index
        print("\n🔄 Building vector index...")
        success = vector_service.build_obsidian_index()
        
        if success:
            stats = vector_service.get_index_stats()
            print(f"\n✅ Index built successfully!")
            print(f"📊 ChromaDB documents: {stats.get('documents', 0)}")
            print(f"📊 Index nodes: {stats.get('nodes', 'unknown')}")
            print(f"📊 Status: {stats.get('status', 'unknown')}")
            
            if stats.get('documents', 0) > 0:
                print(f"🔍 Your knowledge base is ready for search!")
            else:
                print(f"⚠️ No documents were indexed - ChromaDB collection is empty")
                print(f"🔍 This might be due to:")
                print(f"   • All files being empty")
                print(f"   • Files being too short to create meaningful chunks")
                print(f"   • Encoding issues when reading files")
        else:
            print("\n❌ Failed to build index")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()