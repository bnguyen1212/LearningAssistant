import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
import glob
import requests
from dotenv import load_dotenv

load_dotenv()

class LearningState(TypedDict):
    query: str
    obsidian_content: List[str]
    code_content: List[str]
    external_content: List[str]
    learning_notes: str
    vault_updated: bool

class LearningAssistant:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-sonnet-4-20250514")
        self.obsidian_path = os.getenv("OBSIDIAN_VAULT_PATH")
        self.code_path = os.getenv("CODE_PATH")
        
    def search_obsidian(self, state: LearningState) -> LearningState:
        """Search Obsidian vault for relevant content"""
        query = state["query"].lower()
        content = []
        
        if self.obsidian_path and os.path.exists(self.obsidian_path):
            for md_file in glob.glob(f"{self.obsidian_path}/**/*.md", recursive=True):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        if any(term in file_content.lower() for term in query.split()):
                            content.append(f"File: {os.path.basename(md_file)}\n{file_content[:1000]}...")
                except Exception:
                    continue
                    
        state["obsidian_content"] = content[:3]  # Limit to 3 most relevant
        return state
    
    def search_code(self, state: LearningState) -> LearningState:
        """Search personal code for relevant content"""
        query = state["query"].lower()
        content = []
        
        if self.code_path and os.path.exists(self.code_path):
            for ext in ["*.py", "*.js", "*.ts", "*.java"]:
                for code_file in glob.glob(f"{self.code_path}/**/{ext}", recursive=True):
                    try:
                        with open(code_file, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                            if any(term in file_content.lower() for term in query.split()):
                                content.append(f"File: {os.path.basename(code_file)}\n{file_content[:1000]}...")
                    except Exception:
                        continue
                        
        state["code_content"] = content[:3]  # Limit to 3 most relevant
        return state
    
    def search_external(self, state: LearningState) -> LearningState:
        """Search external sources (simple web search)"""
        query = state["query"]
        content = []
        
        try:
            # Simple DuckDuckGo instant answer API
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("Abstract"):
                    content.append(f"DuckDuckGo: {data['Abstract']}")
                if data.get("Definition"):
                    content.append(f"Definition: {data['Definition']}")
        except Exception:
            content.append("External search unavailable")
            
        state["external_content"] = content
        return state
    
    def generate_learning_notes(self, state: LearningState) -> LearningState:
        """Generate learning notes based on all gathered content"""
        prompt = f"""
        Based on the following sources, create comprehensive learning notes about: {state['query']}

        Obsidian Vault Content:
        {chr(10).join(state['obsidian_content']) if state['obsidian_content'] else 'No relevant content found'}

        Personal Code Content:
        {chr(10).join(state['code_content']) if state['code_content'] else 'No relevant code found'}

        External Sources:
        {chr(10).join(state['external_content']) if state['external_content'] else 'No external content found'}

        Create structured learning notes in markdown format that:
        1. Summarizes key concepts
        2. Connects information from different sources
        3. Identifies knowledge gaps
        4. Suggests next learning steps
        """
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state["learning_notes"] = response.content
        return state
    
    def update_vault(self, state: LearningState) -> LearningState:
        """Update Obsidian vault with new learning notes"""
        if not self.obsidian_path or not os.path.exists(self.obsidian_path):
            state["vault_updated"] = False
            return state
            
        try:
            # Create filename from query
            filename = state["query"].replace(" ", "_").replace("/", "_")[:50] + ".md"
            filepath = os.path.join(self.obsidian_path, "Learning", filename)
            
            # Create Learning directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write learning notes to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Learning Notes: {state['query']}\n\n")
                f.write(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write(state["learning_notes"])
                f.write(f"\n\n---\nTags: #learning #ai-generated\n")
                
            state["vault_updated"] = True
        except Exception as e:
            print(f"Failed to update vault: {e}")
            state["vault_updated"] = False
            
        return state
    
    def create_workflow(self):
        """Create the LangGraph workflow"""
        workflow = StateGraph(LearningState)
        
        # Add nodes
        workflow.add_node("search_obsidian", self.search_obsidian)
        workflow.add_node("search_code", self.search_code)
        workflow.add_node("search_external", self.search_external)
        workflow.add_node("generate_notes", self.generate_learning_notes)
        workflow.add_node("update_vault", self.update_vault)
        
        # Define flow
        workflow.set_entry_point("search_obsidian")
        workflow.add_edge("search_obsidian", "search_code")
        workflow.add_edge("search_code", "search_external")
        workflow.add_edge("search_external", "generate_notes")
        workflow.add_edge("generate_notes", "update_vault")
        workflow.add_edge("update_vault", END)
        
        return workflow.compile()
    
    def learn(self, query: str):
        """Main learning function"""
        workflow = self.create_workflow()
        
        initial_state = {
            "query": query,
            "obsidian_content": [],
            "code_content": [],
            "external_content": [],
            "learning_notes": "",
            "vault_updated": False
        }
        
        result = workflow.invoke(initial_state)
        return result

if __name__ == "__main__":
    assistant = LearningAssistant()
    
    # Example usage
    query = input("What would you like to learn about? ")
    result = assistant.learn(query)
    
    print("\n" + "="*50)
    print("LEARNING NOTES")
    print("="*50)
    print(result["learning_notes"])
    print(f"\nVault updated: {result['vault_updated']}")
