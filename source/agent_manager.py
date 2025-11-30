from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_deepseek import ChatDeepSeek
from pathlib import Path

import sys
from tools.tools import search_tool, read_file_tool, write_file_tool, list_files_tool, modify_file_tool, create_new_file, read_parquet_file
from tools.data_handling import calculate_iv_tool, bin_single_feature_tool, process_inputs_and_calculate_iv_tool

# Add the project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def extract_assistant_message(response):
    """Extract the assistant's message from the response."""
    try:
        if isinstance(response, dict) and 'messages' in response:
            # Get the last assistant message
            for msg in reversed(response['messages']):
                if hasattr(msg, 'content') and hasattr(msg, 'type'):
                    if msg.type == 'ai' or msg.type == 'assistant':
                        return msg.content
        elif hasattr(response, 'content'):
            return response.get("content", str(response))
        return str(response)
    except Exception:
        return str(response)


def initialize_agent():
    """Initialize the LLM and Agent."""
    try:
        custom_profile = {
            "max_input_tokens": 100_000,
            "tool_calling": True,
            "structured_output": True,
            "max_retries": 3
            # ...
        }
        model = ChatDeepSeek(
            model="deepseek-chat",
            profile=custom_profile # pyright: ignore[reportArgumentType]
        )
        print(f"Model initialized OK✅: {model.model_name}")

        # Initialize tools configuration
        tools = [
            search_tool,
            read_file_tool,
            write_file_tool,
            list_files_tool,
            modify_file_tool,
            create_new_file,
            read_parquet_file,
            calculate_iv_tool,
            bin_single_feature_tool,
            process_inputs_and_calculate_iv_tool
        ]

        agent = create_agent(
            model=model,
            tools=tools,
            middleware=[
                SummarizationMiddleware(
                  model=model,
                  trigger=("fraction", 0.8),
                  keep=("fraction", 0.3)
                ) # pyright: ignore[reportArgumentType]
            ],
            system_prompt="you are a helpful assistant."
        )
        print("Agent initialized successfully✅")
        print(f"Loaded {len(tools)} tools: {', '.join([getattr(tool, 'name', 'Unnamed Tool') for tool in tools])}")

        return agent

    except Exception as e:
        print(f"Agent initialization failed: {e}")
        return None
