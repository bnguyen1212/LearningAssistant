import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from core.config import config

class ConversationManager:
    """Manage a single main conversation session for the learning agent"""

    def __init__(self):
        self.history_dir = Path(config.CONVERSATION_HISTORY_DIR)
        self.history_dir.mkdir(exist_ok=True)
        self.session_id = "main_session"
        self.active_session: List[Dict] = []
        self._load_session()

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the main session history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.active_session.append(message)
        # Auto-save periodically
        if config.AUTO_SAVE_CONVERSATIONS and len(self.active_session) % 10 == 0:
            self._save_session()

    def get_history(self, max_messages: int = None) -> List[Dict]:
        """Get conversation history for the main session"""
        if max_messages is None:
            max_messages = config.MAX_CONVERSATION_HISTORY
        return self.active_session[-max_messages:] if max_messages > 0 else self.active_session

    def get_recent_context(self, max_messages: int = None) -> str:
        """Get recent conversation as formatted context string"""
        if max_messages is None:
            max_messages = config.MAX_CONVERSATION_HISTORY
        history = self.get_history(max_messages)
        if not history:
            return "No previous conversation context."
        context_lines = [
            f"{msg['role'].title()}: {msg['content']}" for msg in history
        ]
        return "\n".join(context_lines)

    def get_conversation_for_summary(self) -> str:
        """Get conversation formatted for saving as Obsidian summary (no emojis)"""
        if not self.active_session:
            return ""
        conversation_text = []
        for msg in self.active_session:
            if msg["role"] in ["user", "assistant"]:
                role_label = "Human" if msg["role"] == "user" else "Assistant"
                conversation_text.append(f"{role_label}: {msg['content']}")
        return "\n\n".join(conversation_text)

    def clear_session(self) -> None:
        """Clear the main conversation session"""
        if config.SAVE_RAW_CONVERSATIONS:
            self._save_session()
        self.active_session = []
        if config.ENABLE_TOOL_DEBUGGING:
            print("Cleared main session.")

    def mark_session_as_saved(self, obsidian_path: str) -> None:
        """Mark that this session has been saved to Obsidian"""
        self.active_session.append({
            "role": "system",
            "content": f"Session saved to Obsidian: {obsidian_path}",
            "timestamp": datetime.now().isoformat(),
            "type": "save_marker"
        })
        if config.SAVE_RAW_CONVERSATIONS:
            self._save_session()

    def _save_session(self) -> None:
        """Save the main session to JSON file"""
        file_path = self.history_dir / f"{self.session_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.active_session, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if config.ENABLE_TOOL_DEBUGGING:
                print(f"Failed to save main session: {e}")

    def _load_session(self) -> None:
        """Load the main session from JSON file"""
        file_path = self.history_dir / f"{self.session_id}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.active_session = json.load(f)
            except Exception as e:
                if config.ENABLE_TOOL_DEBUGGING:
                    print(f"Failed to load main session: {e}")
                self.active_session = []
        else:
            self.active_session = []

    def save_all_sessions(self) -> None:
        """Save the main session (for compatibility with shutdown hooks)"""
        if config.SAVE_RAW_CONVERSATIONS:
            self._save_session()
            if config.ENABLE_TOOL_DEBUGGING:
                print("Saved main session.")

# Create global conversation manager instance
conversation_manager = ConversationManager()