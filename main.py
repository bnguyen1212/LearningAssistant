from agent.learning_agent import LearningAgent
from agent.tools import chat, storage
from services.vector_store import vector_service
from services.llm_service import llm_service
from services.obsidian_service import obsidian_service
from core.conversation import conversation_manager
from utils.output_cleaning import clean_llm_output


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
    result = chat.chat_with_context(vector_service=vector_service, user_message=user_message)
    return result

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
    return storage.save_session(referenced_files, llm_service, obsidian_service, vector_service)

tools = [
    chat_with_context_tool,
    save_session_tool,
]

llm_with_tools = llm_service.llm.bind_tools(tools)
agent = LearningAgent(llm_with_tools)



def process_user_input(user_input: str):
    """
    Process a single user input, print and return (assistant_output, status).
    status: 'exit', 'clear', or 'normal'
    """
    # Detect special commands and run same logic as manual loop
    if user_input.lower() in ("exit", "quit"):
        conversation_manager._save_session()
        return "Exiting...", "exit"
    if user_input.lower() in ("new", "clear"):
        conversation_manager.clear_session()
        conversation_manager.clear_main_session_file()
        return "Session cleared.", "clear"

    # Step 1: Get initial response from agent/LLM
    response = agent.process_user_message(user_input)
    content = getattr(response, "content", response)
    assistant_output = ""

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
                        # If the tool is chat_with_context_tool, accumulate referenced files
                        if tool_name == "chat_with_context_tool":
                            tool_result = chat_with_context_tool(tool_input.get("user_message"))
                            if isinstance(tool_result, dict):
                                new_refs = tool_result.get("referenced_files", [])
                                conversation_manager.referenced_files_state.update(new_refs)
                            vault_context = tool_result.get("vault_context", [])
                            if isinstance(vault_context, list):
                                vault_context_str = "\n".join(str(x) for x in vault_context)
                            else:
                                vault_context_str = str(vault_context)
                            followup = llm_service.invoke_context(
                                f"Vault context: {vault_context_str} User query: {tool_input.get('user_message','')}"
                            )
                            conversation_manager.add_message("assistant", followup.content)
                            assistant_output = getattr(followup, "content", followup)
                        # If the tool is save_session_tool, print the referenced files used
                        if tool_name == "save_session_tool":
                            tool_input["referenced_files"] = list(conversation_manager.referenced_files_state)
                            tool_result = tool_func(**tool_input)
                            print(f"[Session saved with referenced files]: {sorted(conversation_manager.referenced_files_state)}")
                    except Exception as e:
                        print(f"[Tool '{tool_name}' error]: {e}")
                else:
                    print(f"[Tool '{tool_name}' not found]")
    elif isinstance(content, str):
        assistant_output = content
        print("Assistant:", content)
    else:
        # Fallback for other response types
        assistant_output = str(content)
        print("Assistant:", content)
    assistant_output = clean_llm_output(assistant_output)
    print("Assistant:", assistant_output)
    return assistant_output, "normal"


def manual_reasoning_loop():
    print("Learning Assistant (type 'exit' to quit)")
    print(vector_service.get_index_stats())
    while True:
        user_input = input("You: ")
        output, status = process_user_input(user_input)
        if status == "exit":
            print(output)
            break
        elif status == "clear":
            print(output)
            continue

if __name__ == "__main__":
    manual_reasoning_loop()