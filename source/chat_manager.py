from agent_manager import UserContext, extract_assistant_message


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
