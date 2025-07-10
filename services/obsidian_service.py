import os
import re
from typing import List, Dict
from pathlib import Path
from datetime import datetime

from utils.prompt_templates import CATEGORY_GENERATION_PROMPT

class ObsidianService:
    def __init__(self, vault_path: str, llm_service=None):
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"Obsidian vault path does not exist: {vault_path}")
        self.llm_service = llm_service
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be safe for use as a filename
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove extra whitespace and replace with underscores
        sanitized = re.sub(r'\s+', '_', sanitized.strip())
        # Remove leading/trailing underscores and dots
        sanitized = sanitized.strip('_.')
        # Ensure it's not empty
        if not sanitized:
            sanitized = "untitled"
        return sanitized
    
    def generate_category_path(self, topic: str) -> str:
        """
        Use LLM to generate appropriate category path for the topic
        """
        if not self.llm_service:
            # Fallback to a simple default if no LLM service
            return "General"
        
        category_prompt = CATEGORY_GENERATION_PROMPT.format(topic=topic)

        try:
            from langchain_core.messages import HumanMessage
            response = self.llm_service.llm.invoke([HumanMessage(content=category_prompt)])
            category_path = response.content.strip().strip('/')
            
            # Clean up the response and sanitize
            category_parts = [self.sanitize_filename(part) for part in category_path.split('/')]
            return '/'.join(category_parts)
            
        except Exception as e:
            print(f"Warning: Failed to generate category path, using default: {e}")
            return "General"
    
    def create_topic_hierarchy(self, topic: str) -> Path:
        """
        Create a topic-based folder hierarchy using LLM-generated categories
        """
        # Base folder for all learning sessions
        base_folder = self.vault_path / "Learning_Sessions"
        
        # Get LLM-generated category path
        category_path = self.generate_category_path(topic)
        
        # Create full path
        full_path = base_folder
        for part in category_path.split('/'):
            full_path = full_path / part
        
        # Add topic-specific subfolder
        topic_folder = full_path / self.sanitize_filename(topic)
        
        # Create the directory structure
        topic_folder.mkdir(parents=True, exist_ok=True)
        
        return topic_folder
    
    def generate_note_filename(self, topic: str) -> str:
        """
        Generate a filename for the note based on topic and timestamp
        """
        date_str = datetime.now().strftime("%Y%m%d")
        sanitized_topic = self.sanitize_filename(topic)
        return f"{date_str}_{sanitized_topic}.md"
    
    def save_note(self, topic: str, content: str) -> str:
        """
        Save a note to the appropriate topic hierarchy
        
        Returns:
            str: Full path where the note was saved
        """
        # Create topic hierarchy
        topic_folder = self.create_topic_hierarchy(topic)
        
        # Generate filename
        filename = self.generate_note_filename(topic)
        file_path = topic_folder / filename
        
        # Add metadata header to the note
        note_header = f"""---
        created: {datetime.now().isoformat()}
        topic: {topic}
        type: learning_session
        tags: [learning, {self.sanitize_filename(topic).lower()}]
        ---

        # {topic}

        """
        
        full_content = note_header + content
        
        # Write the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return str(file_path)
    
    def save_multiple_notes(self, notes_dict: Dict[str, str]) -> List[str]:
        """
        Save multiple notes from a dictionary of topic -> content
        
        Returns:
            List[str]: List of file paths where notes were saved
        """
        saved_paths = []
        
        for topic, content in notes_dict.items():
            try:
                path = self.save_note(topic, content)
                saved_paths.append(path)
                print(f"✅ Saved note: {topic} -> {path}")
            except Exception as e:
                print(f"❌ Failed to save note for {topic}: {e}")
        
        return saved_paths
    
    def get_recent_notes(self, days: int = 7) -> List[str]:
        """
        Get list of recently created notes (for debugging/verification)
        """
        recent_notes = []
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        learning_sessions = self.vault_path / "Learning_Sessions"
        if learning_sessions.exists():
            for file_path in learning_sessions.rglob("*.md"):
                if file_path.stat().st_mtime > cutoff_date:
                    recent_notes.append(str(file_path))
        
        return recent_notes