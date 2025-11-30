import sys
from pathlib import Path

# Add the project root to sys.path to ensure imports work correctly
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agent_manager import initialize_agent
from chat_manager import run_chat_loop


def main():
    """Main function to run the multi-turn chat with mode selection."""

    
    agent = initialize_agent()
    if agent is None:
        print("agent not initialized. Unable to start conversation.")
        return

    # "stream" for streaming output mode 
    # "legacy" for invoke mode
    run_chat_loop(agent, mode="legacy")

if __name__ == "__main__":
    main()
