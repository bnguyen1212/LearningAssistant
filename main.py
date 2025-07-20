from agent.learning_agent import LearningAgent
from agent.tools import chat, storage
from services.vector_store import VectorStoreService
from services.llm_service import LLMService
from services.obsidian_service import ObsidianService

vector_service = VectorStoreService()
llm_service = LLMService()
obsidian_service = ObsidianService()

def chat_with_context_tool(user_message: str) -> dict:
    """
    Fetch relevant context from the Obsidian vault using a semantic search.

    Args:
        user_message (str): The user's query or message to search for relevant context.

    Returns:
        dict: {
            "vault_context": list of relevant context strings,
            "referenced_files": list of filenames referenced in the context
        }
    """
    return chat.chat_with_context(user_message=user_message, vector_service=vector_service)


def save_session_tool(
    referenced_files: list
) -> str:
    """
    Save a session note to Obsidian using the provided summary, topics, subject, referenced files, and llm_service.

    Args:
        referenced_files (list): List of referenced file names.

    Returns:
        str: Path of the saved session note.
    """
    return storage.save_session(referenced_files, llm_service, obsidian_service)

tools = [
    chat_with_context_tool,
    save_session_tool,
]

llm_with_tools = llm_service.llm.bind_tools(tools)
agent = LearningAgent(llm_with_tools)


def manual_reasoning_loop():
    print("Learning Assistant (type 'exit' to quit)")
    referenced_files_state = set()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            break

        # Step 1: Get initial response from agent/LLM
        response = agent.process_user_message(user_input)
        content = getattr(response, "content", response)

        # Step 2: Check if the response contains tool calls
        # If content is a list, look for tool_use dicts
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    tool_name = item.get("name")
                    tool_input = item.get("input", {})
                    # Find the tool function by name
                    tool_func = None
                    for t in tools:
                        if hasattr(t, "__name__") and t.__name__ == tool_name:
                            tool_func = t
                            break
                    if tool_func:
                        try:
                            # For save_session_tool, always use accumulated referenced_files
                            if tool_name == "save_session_tool":
                                tool_input["referenced_files"] = list(referenced_files_state)
                            tool_result = tool_func(**tool_input)
                            print(f"[Tool '{tool_name}' result]: {tool_result}")
                            # If the tool is chat_with_context_tool, accumulate referenced files
                            if tool_name == "chat_with_context_tool" and isinstance(tool_result, dict):
                                new_refs = tool_result.get("referenced_files", [])
                                referenced_files_state.update(new_refs)
                                print(f"[Accumulated referenced files]: {sorted(referenced_files_state)}")
                                if not tool_result.get("vault_context"):
                                    followup = llm_service.invoke_prompt(f"No relevant context was found. Please answer the user's question using your own knowledge: {tool_input.get('user_message','')}")
                                    print("Assistant:", getattr(followup, "content", followup))
                            # If the tool is save_session_tool, print the referenced files used
                            if tool_name == "save_session_tool":
                                print(f"[Session saved with referenced files]: {sorted(referenced_files_state)}")
                        except Exception as e:
                            print(f"[Tool '{tool_name}' error]: {e}")
                    else:
                        print(f"[Tool '{tool_name}' not found]")
                elif item.get("type") == "text":
                    print("Assistant:", item.get("text", ""))
        elif isinstance(content, str):
            print("Assistant:", content)
        else:
            # Fallback for other response types
            print("Assistant:", content)

if __name__ == "__main__":
    manual_reasoning_loop()