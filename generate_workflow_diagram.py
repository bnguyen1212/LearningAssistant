import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from graph.workflow import create_learning_workflow
from dotenv import load_dotenv

load_dotenv()

def main():
    """
    Generate the workflow diagram
    """
    print("🚀 Generating Learning Workflow Diagram...")
    
    try:
        # Create workflow
        workflow = create_learning_workflow()
        
        # Generate visual diagram
        diagram_path = workflow.get_workflow_image("learning_workflow_diagram.png")
        
        if diagram_path:
            print(f"🎨 Workflow diagram created: {diagram_path}")
            print("📊 Open the image to see your conversational learning workflow!")
        
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")

if __name__ == "__main__":
    main()