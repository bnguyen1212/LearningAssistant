# Create test_config.py (temporary file)
from core.config import config

def test_config():
    """Test the configuration setup"""
    print("🧪 Testing Configuration...")
    print("=" * 40)
    
    # Test 1: Print config summary
    config.print_config_summary()
    print()
    
    # Test 2: Validate configuration
    errors = config.validate_config()
    if errors:
        print("❌ Configuration Errors Found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration is valid!")
    
    # Test 3: Test specific values
    print("\n🔍 Testing specific values:")
    print(f"  LLM Model: {config.LLM_MODEL}")
    print(f"  Temperature: {config.LLM_TEMPERATURE}")
    print(f"  Vault path exists: {bool(config.OBSIDIAN_VAULT_PATH)}")
    print(f"  API keys loaded: {bool(config.ANTHROPIC_API_KEY and config.VOYAGE_API_KEY)}")
    
    return len(errors) == 0

if __name__ == "__main__":
    success = test_config()
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")