from core.conversation import conversation_manager
from core.config import config

class LearningAgent:
    """
    A simple learning agent that manages a single main conversation session.
    """

    def __init__(self, llm):
        """
        Args:
            llm: The language model instance (must have a .invoke() or .generate() method)
            tools: Optional dict of tool functions (e.g., search, save, analyze)
        """
        self.llm = llm
        self.referenced_files = set()

    def process_user_message(self, user_message: str) -> str:
        """
        Handles a user message, updates conversation, and returns the agent's reply.
        """
        # Add user message to conversation history
        conversation_manager.add_message("user", user_message)

        # Prepare context for the LLM
        context = conversation_manager.get_recent_context(config.MAX_CONVERSATION_HISTORY)

        # Compose prompt for the LLM
        prompt = (
            f"Conversation so far:\n{context}\n\n"
            f"User: {user_message}\n"
            "Assistant:"
        )

        # Get response from the LLM
        agent_response = self.llm.invoke(prompt)

        # Add agent response to conversation history
        conversation_manager.add_message("assistant", agent_response)

        return agent_response

    def get_referenced_files(self) -> list:
        """
        Returns a deduplicated list of all referenced files for the current session.
        """
        return list(self.referenced_files)

    def save_session_summary(self, obsidian_path: str) -> None:
        """
        Marks the session as saved to Obsidian (for use after saving summary externally).
        """
        conversation_manager.mark_session_as_saved(obsidian_path)

    def clear_conversation(self) -> None:
        """
        Clears the main session conversation history.
        """
        conversation_manager.clear_session()
