import os
import re
from typing import List, Dict
from pathlib import Path
from datetime import datetime

class ObsidianService:
    def __init__(self, vault_path: str, llm_service=None):
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"Obsidian vault path does not exist: {vault_path}")
    
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
    
    def create_daily_folder(self) -> Path:
        """
        Create or get daily folder for organizing notes by date
        """
        # Base folder for all learning sessions
        base_folder = self.vault_path / "Learning_Sessions"
        base_folder.mkdir(exist_ok=True)
        
        # Create daily folder with clean date format: "July 11, 2025"
        today = datetime.now()
        daily_folder_name = today.strftime("%B %d, %Y")  # e.g., "July 11, 2025"
        daily_folder = base_folder / daily_folder_name
        daily_folder.mkdir(exist_ok=True)
        
        return daily_folder
    
    def generate_session_filename(self, session_name: str = None) -> str:
        """
        Generate a unique filename for a session summary within the daily folder
        """
        # Generate timestamp for uniqueness
        timestamp = datetime.now().strftime("%H%M%S")  # HHMMSS format
        
        if session_name:
            # Clean the session name for use as filename
            clean_name = self.sanitize_filename(session_name)
            clean_name = clean_name[:30]  # Limit length
            filename = f"{timestamp}_{clean_name}.md"
        else:
            filename = f"{timestamp}_Learning_Session.md"
        
        return filename
    
    def save_session_notes(self, notes_dict: Dict[str, str], session_name: str = None, topics: List[str] = None) -> List[str]:
        """
        Save session summary directly to daily folder
        """
        if not notes_dict:
            print("❌ No session summary to save")
            return []
        
        # Create daily folder
        daily_folder = self.create_daily_folder()
        
        # Generate unique filename for this session
        filename = self.generate_session_filename(session_name)
        summary_path = daily_folder / filename
        
        # Get session content (should be single entry with key "Learning Session")
        session_content = notes_dict.get("Learning Session", "")
        if not session_content:
            # Fallback to first available content
            session_content = list(notes_dict.values())[0] if notes_dict else ""
        
        # Format tags for YAML frontmatter
        tags_yaml = "[" + ", ".join(topics) + "]"
        
        # Add metadata header with daily organization info
        note_header = f"""---
created: {datetime.now().isoformat()}
type: learning_session_summary
daily_folder: {daily_folder.name}
tags: {tags_yaml}
---

# Learning Session Summary

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Daily Folder:** {daily_folder.name}

"""
        
        full_content = note_header + session_content
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            print(f"✅ Saved session summary: {filename}")
            print(f"📅 Daily folder: {daily_folder.name}")
            return [str(summary_path)]
            
        except Exception as e:
            print(f"❌ Failed to save session summary: {e}")
            return []
    
    def get_daily_sessions(self, date: datetime = None) -> List[str]:
        """
        Get list of sessions for a specific day
        """
        if date is None:
            date = datetime.now()
        
        daily_folder_name = date.strftime("%B %d, %Y")
        daily_folder = self.vault_path / "Learning_Sessions" / daily_folder_name
        
        sessions = []
        if daily_folder.exists():
            for file_path in daily_folder.glob("*.md"):
                if file_path.name != "Daily_Index.md":  # Exclude index if it exists
                    sessions.append(str(file_path))
        
        return sessions
    
    def get_recent_sessions(self, days: int = 7) -> List[str]:
        """
        Get list of recent learning sessions across multiple days
        """
        recent_sessions = []
        
        learning_sessions = self.vault_path / "Learning_Sessions"
        if learning_sessions.exists():
            for daily_folder in learning_sessions.iterdir():
                if daily_folder.is_dir():
                    # Check if folder is within the recent days range
                    folder_age = datetime.now().timestamp() - daily_folder.stat().st_mtime
                    if folder_age <= (days * 24 * 60 * 60):
                        # Add all session files from this daily folder
                        for session_file in daily_folder.glob("*.md"):
                            if session_file.name != "Daily_Index.md":
                                recent_sessions.append(str(session_file))
        
        return recent_sessions
    
    def get_session_info(self, session_file_path: str) -> Dict:
        """
        Get information about a specific session file
        """
        session_path = Path(session_file_path)
        if not session_path.exists():
            return {}
        
        return {
            "session_name": session_path.stem,  # Filename without extension
            "daily_folder": session_path.parent.name,
            "created": datetime.fromtimestamp(session_path.stat().st_ctime),
            "file_path": str(session_path)
        }