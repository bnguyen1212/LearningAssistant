import re
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from core.config import config

class ObsidianService:
    def __init__(self):
        self.vault_path = Path(config.OBSIDIAN_VAULT_PATH)
        if not self.vault_path.exists():
            raise ValueError("Obsidian vault path does not exist")
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be safe for use as a filename
        """
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
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
        base_folder = self.vault_path / config.OBSIDIAN_DAILY_NOTES_FOLDER
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
            clean_name = clean_name[:100]  # Limit length
            filename = f"{clean_name}_{timestamp}.md"
        else:
            filename = f"Learning_Session_{timestamp}.md"
        
        return filename
    
    def save_session_notes(
        self,
        session_summary: str,
        session_name: str = None,
        topics: List[str] = None,
        referenced_files: List[str] = None
    ) -> str:
        """
        Save session summary to daily organized folder structure with backlinks
        """
        if not session_summary:
            print("❌ No session summary to save")
            return ""
        
        # Create daily folder
        daily_folder = self.create_daily_folder()
        
        # Generate unique filename for this session
        filename = self.generate_session_filename(session_name)
        summary_path = daily_folder / filename
        
        topic_tags = topics if topics else []
        # Format tags for YAML frontmatter
        tags_yaml = "[" + ", ".join(topic_tags) + "]"
        
        # Build referenced files section
        referenced_section = ""
        if referenced_files:
            referenced_section = "\n\n## Referenced Files\n\n"
            for ref_file in referenced_files:
                print(ref_file)
                # Create Obsidian-style wikilink (without .md extension)
                file_base = ref_file.replace('.md', '') if ref_file.endswith('.md') else ref_file
                referenced_section += f"- [[{file_base}]]\n"
        
        # Add metadata header with daily organization info
        note_header = f"""---
created: {datetime.now().isoformat()}
type: learning_session_summary
daily_folder: {daily_folder.name}
tags: {tags_yaml}
---

# Learning Session Summary

"""
        # Combine all content
        full_content = note_header + session_summary + referenced_section
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            # Add backlinks to referenced files
            if referenced_files:
                self._add_backlinks_to_referenced_files(referenced_files, filename, daily_folder.name)
            
            print(f"Saved session summary: {filename}")
            if referenced_files:
                print(f"Added backlinks to {len(referenced_files)} files")
            return str(summary_path)
            
        except Exception as e:
            print(f"Failed to save session summary: {e}")
            return ""
    
    def _add_backlinks_to_referenced_files(self, referenced_files: List[str], session_filename: str, daily_folder_name: str):
        """Add backlinks to the original files that were referenced"""
        session_link = f"[[{config.OBSIDIAN_DAILY_NOTES_FOLDER}/{daily_folder_name}/{session_filename.replace('.md', '')}]]"
        
        for ref_filename in referenced_files:
            try:
                # Find the actual file path
                ref_file_path = self._find_file_in_vault(ref_filename)
                if not ref_file_path:
                    print(f"Could not find file: {ref_filename}")
                    continue
                
                # Read current content
                with open(ref_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if backlink already exists
                if session_link in content:
                    continue
                
                # Add backlink section
                backlink_section = f"\n\n## References\n\n- {session_link}\n"
                
                # Check if "Learning Sessions" section already exists
                if "## References" in content:
                    # Add to existing section
                    content = content.replace("## References", f"## References\n\n- {session_link}")
                else:
                    # Add new section at the end
                    content += backlink_section
                
                # Write back to file
                with open(ref_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Added backlink to {ref_filename}")
                
            except Exception as e:
                print(f"❌ Failed to add backlink to {ref_filename}: {e}")

    def _find_file_in_vault(self, filename: str) -> Optional[Path]:
        """Find a file in the Obsidian vault by filename"""
        vault_path = Path(self.vault_path)
        
        # Try direct match first
        for md_file in vault_path.rglob(filename):
            if md_file.is_file():
                return md_file
        
        # Try with .md extension if not provided
        if not filename.endswith('.md'):
            for md_file in vault_path.rglob(f"{filename}.md"):
                if md_file.is_file():
                    return md_file
        
        return None
    
    def get_daily_sessions(self, date: datetime = None) -> List[str]:
        """
        Get list of sessions for a specific day
        """
        if date is None:
            date = datetime.now()
        
        daily_folder_name = date.strftime("%B %d, %Y")
        daily_folder = self.vault_path / config.OBSIDIAN_DAILY_NOTES_FOLDER / daily_folder_name
        
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
        
        learning_sessions = self.vault_path / config.OBSIDIAN_DAILY_NOTES_FOLDER
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
obsidian_service = ObsidianService()
