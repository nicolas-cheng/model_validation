from langchain_deepseek import ChatDeepSeek
from pathlib import Path
from dataclasses import dataclass
import sys

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from source.workflow.validation_workflow import build_validation_workflow

@dataclass
class UserContext:
    user_id: str

def initialize_flow():
    """Initialize the LangGraph Workflow."""
    try:
        custom_profile = {
            "max_input_tokens": 100_000,
            "tool_calling": True,
            "structured_output": True,
            "max_retries": 3
        }
        model = ChatDeepSeek(
            model="deepseek-chat",
            profile=custom_profile # pyright: ignore[reportArgumentType]
        )
        print(f"Model initialized OK✅: {model.model_name}")

        # Build and return the workflow
        workflow = build_validation_workflow(model)
        print("Workflow initialized successfully✅")
        
        return workflow

    except Exception as e:
        print(f"Workflow initialization failed: {e}")
        return None

# Expose the graph for LangGraph Studio
graph = initialize_flow()
