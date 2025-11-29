from flow_manager import initialize_flow
from chat_manager import run_chat_loop


def main():
    """Main function to run the multi-turn chat with mode selection."""
    agent = initialize_flow()
    if agent is None:
        print("Agent not initialized. Unable to start conversation.")
        return

    # "stream" for streaming output mode 
    # "legacy" for invoke mode
    run_chat_loop(agent, mode="legacy")


# Run the multi-turn chat
if __name__ == "__main__":
    main()
