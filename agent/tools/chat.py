# agent/tools/chat.py
def chat_with_context(
    vector_service,
    user_message: str
) -> dict:
    """
    The LLM, when reasoning, can call this tool to fetch additional context from the vault.
    Returns: {
        "vault_context": list,
        "referenced_files": list,
    }
    """
    vault_context = []
    referenced_files = []
    try:
        vault_context, referenced_files = vector_service.search_obsidian(user_message)
    except Exception as e:
        print("I encountered an error using chat_with_context tool")
    return {
        "vault_context": vault_context,
        "referenced_files": referenced_files
    }