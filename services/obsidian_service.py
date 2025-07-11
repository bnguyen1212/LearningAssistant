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
    
    def create_session_folder(self, session_name: str = None) -> Path:
        """
        Create a session-based folder for organizing notes by learning session
        """
        # Base folder for all learning sessions
        base_folder = self.vault_path / "Learning_Sessions"
        
        # Generate session folder name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if session_name:
            sanitized_session = self.sanitize_filename(session_name)
            session_folder_name = f"{timestamp}_{sanitized_session}"
        else:
            session_folder_name = f"{timestamp}_session"
        
        session_folder = base_folder / session_folder_name
        
        # Create the directory structure
        session_folder.mkdir(parents=True, exist_ok=True)
        
        return session_folder
    
    def save_session_notes(self, notes_dict: Dict[str, str], session_name: str = None) -> List[str]:
        """
        Save session summary to a single file in session folder
        """
        if not notes_dict:
            print("❌ No session summary to save")
            return []
        
        # Create session folder
        session_folder = self.create_session_folder(session_name)
        
        # Get session content (should be single entry with key "Learning Session")
        session_content = notes_dict.get("Learning Session", "")
        if not session_content:
            # Fallback to first available content
            session_content = list(notes_dict.values())[0] if notes_dict else ""
        
        # Create single session summary file
        summary_path = session_folder / "Learning_Session_Summary.md"
        
        # Add metadata header
        note_header = f"""---
created: {datetime.now().isoformat()}
type: learning_session_summary
session: {session_folder.name}
tags: [learning, session, summary]
---

# Learning Session Summary

**Session:** {session_folder.name}  
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
        
        full_content = note_header + session_content
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            print(f"✅ Saved session summary: {summary_path.name}")
            print(f"📁 Session folder: {session_folder.name}")
            return [str(summary_path)]
            
        except Exception as e:
            print(f"❌ Failed to save session summary: {e}")
            return []
    
    def get_recent_sessions(self, days: int = 7) -> List[str]:
        """
        Get list of recent learning sessions
        """
        recent_sessions = []
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        learning_sessions = self.vault_path / "Learning_Sessions"
        if learning_sessions.exists():
            for session_folder in learning_sessions.iterdir():
                if session_folder.is_dir() and session_folder.stat().st_mtime > cutoff_date:
                    recent_sessions.append(str(session_folder))
        
        return recent_sessions
    
    def get_session_info(self, session_folder_path: str) -> Dict:
        """
        Get information about a specific session
        """
        session_path = Path(session_folder_path)
        if not session_path.exists():
            return {}
        
        # Check if session summary exists
        summary_file = session_path / "Learning_Session_Summary.md"
        has_summary = summary_file.exists()
        
        return {
            "session_name": session_path.name,
            "created": datetime.fromtimestamp(session_path.stat().st_ctime),
            "has_summary": has_summary,
            "summary_path": str(summary_file) if has_summary else None
        }