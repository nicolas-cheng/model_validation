from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_deepseek import ChatDeepSeek
from pathlib import Path
from data_handling import *
from dataclasses import dataclass

import sys
from pathlib import Path
from tools import search_tool, read_file_tool, write_file_tool, list_files_tool, modify_file_tool, create_new_file,read_parquet_file
from data_handling import calculate_iv_tool, bin_single_feature_tool, process_inputs_and_calculate_iv_tool

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
            return response.content
        return str(response)
    except Exception:
        return str(response)

@dataclass
class UserContext:
    user_id: str

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
            profile=custom_profile 
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
            context_schema=UserContext,
            middleware=[
                SummarizationMiddleware(
                  model=model,
                  trigger=("fraction", 0.8),
                  keep=("fraction", 0.3)
                )
            ],
            system_prompt="you are a helpful assistant."
        )
        print("Agent initialized successfully✅")
        print(f"Loaded {len(tools)} tools: {', '.join([getattr(tool, 'name', 'Unnamed Tool') for tool in tools])}")

        return agent

    except Exception as e:
        print(f"Agent initialization failed: {e}")
        return None

def run_chat_loop(agent, mode="legacy"):
    """Run a multi-turn chat loop with support for streaming and legacy output modes."""
    print("\n" + "="*60)
    print("🤖 AI Assistant Multi-turn Chat System")
    print("="*60)
    print("💡 Tips:")
    print("  - Enter your question to start the conversation")
    print("  - Type 'exit' to end the conversation")
    print("  - Type 'clear' to reset the conversation history")
    print("="*60)

    conversation_history = []
    turn = 0

    while True:
        try:
            user_input = input(f"\n[Turn {turn + 1}] You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Conversation ended. Goodbye!")
                print(f"📊 Total turns: {turn}")
                break

            if user_input.lower() in ['clear', 'reset']:
                conversation_history = []
                turn = 0
                print("✅ Conversation history cleared")
                continue

            content = ""
            if conversation_history:
                content = "\n\nConversation History:\n"
                for i, (user_msg, ai_msg) in enumerate(conversation_history[-3:], 1):
                    content += f"Turn {i} - User: {user_msg}\n"
                    content += f"Turn {i} - AI: {ai_msg}\n"
                content += f"\nCurrent Question: {user_input}"
            else:
                content = user_input

            print("AI is thinking...")

            if mode == "stream":
                # Use streaming output
                last_chunk_content = ""
                for chunk in agent.stream({"messages": [{"role": "user", "content": content}]},
                                          context=UserContext(user_id="user123"),
                                          stream_mode="messages"):
                    print(chunk[0].content, end='', flush=True)
                    last_chunk_content = chunk[0].content

                # Ensure the last chunk ends with a newline
                if not last_chunk_content.endswith("\n"):
                    print()  # Ensure a newline after streaming output

                # Save to history
                conversation_history.append((user_input, last_chunk_content))
            else:
                # Use legacy output mode
                response = agent.invoke(
                    {"messages": [{"role": "user", "content": content}]},
                    context=UserContext(user_id="user123")
                )
                ai_reply = extract_assistant_message(response)
                print(f"AI: {ai_reply}")

                # Save to history
                conversation_history.append((user_input, ai_reply))

            turn += 1

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupt signal detected")
            confirm = input("Confirm exit? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                print(f"\n👋 Conversation ended! Total turns: {turn}")
                break
        except Exception as e:
            print(f"\n❌ Error processing request: {str(e)}")
            print("💡 Please try again or ask a new question")

def main():
    """Main function to run the multi-turn chat with mode selection."""
    agent = initialize_agent()
    if agent is None:
        print("Agent not initialized. Unable to start conversation.")
        return

    # "stream" for streaming output mode 
    # "legacy" for invoke mode
    run_chat_loop(agent, mode="stream")

# Run the multi-turn chat
if __name__ == "__main__":
    main()
