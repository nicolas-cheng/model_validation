from agent_manager import UserContext, extract_assistant_message
from langchain_core.messages import HumanMessage
import sys
import os

# Platform-specific imports for multi-line input
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix/Linux/Mac
    import tty
    import termios


def get_multiline_input(prompt=""):
    """
    Get multi-line input from user. Press Ctrl+Enter to send.
    Works on both Windows and Unix-like systems.
    """
    print(prompt, end='', flush=True)
    lines = []
    current_line = ""
    
    if os.name == 'nt':  # Windows
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getwche()
                
                # Check for Ctrl+Enter (Ctrl+J or Ctrl+M)
                if char == '\n' or char == '\r':
                    # Check if Ctrl is pressed
                    # In Windows, we need to check the previous character
                    # Simple approach: use Enter for newline, Ctrl+Enter to send
                    # We'll use a different approach: Enter adds newline, empty line sends
                    print()  # Move to next line
                    if current_line.strip() == "" and lines:
                        # Empty line after content - send message
                        break
                    lines.append(current_line)
                    current_line = ""
                    print("     ", end='', flush=True)  # Indent continuation
                elif char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                elif char == '\x08' or char == '\x7f':  # Backspace
                    if current_line:
                        current_line = current_line[:-1]
                        print('\b \b', end='', flush=True)
                else:
                    current_line += char
    else:  # Unix/Linux/Mac
        # For Unix systems, use a simpler approach with readline
        print("(Press Ctrl+D on empty line to send, or type message and press Enter twice)")
        import readline
        while True:
            try:
                line = input("     " if lines else "")
                if line.strip() == "" and lines:
                    break
                lines.append(line)
            except EOFError:  # Ctrl+D
                break
    
    # Combine all lines
    result = '\n'.join(lines) if lines else current_line
    return result.strip()


def get_simple_multiline_input(prompt=""):
    """
    Simpler multi-line input: Press Enter twice (empty line) to send message.
    This works reliably across all platforms.
    """
    print(prompt)
    print("💡 Tip: Press Enter twice (empty line) to send, or type 'SEND' on a new line")
    print("-" * 60)
    
    lines = []
    while True:
        try:
            line = input()
            
            # Check for send command
            if line.strip().upper() == 'SEND':
                break
            
            # Empty line - check if we should send
            if line.strip() == "":
                if lines:  # If we have content, send it
                    break
                else:  # If no content yet, just continue
                    continue
            
            lines.append(line)
        except EOFError:
            break
    
    return '\n'.join(lines).strip()


def run_chat_loop(agent, mode="legacy"):
    """Run a multi-turn chat loop with support for streaming and legacy output modes."""
    print("\n" + "="*60)
    print("🤖 AI Assistant Multi-turn Chat System")
    print("="*60)
    print("💡 Tips:")
    print("  - Type your message (multi-line supported)")
    print("  - Press Enter twice (empty line) to send message")
    print("  - Type 'exit' to end the conversation")
    print("  - Type 'clear' to reset the conversation history")
    print("="*60)

    conversation_history = []
    turn = 0

    while True:
        try:
            user_input = get_simple_multiline_input(f"\n[Turn {turn + 1}] You:")

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

            print("\n" + "-" * 60)
            print("🤔 AI is thinking...")
            print("-" * 60)

            if mode == "stream":
                # Use streaming output
                last_chunk_content = ""
                for chunk in agent.stream({"messages": [{"role": "user", "content": content}]},
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
                    {"messages": [HumanMessage(content=content)]}
                )
                ai_reply = extract_assistant_message(response)
                print(f"🤖 AI: {ai_reply}")

                # Save to history
                conversation_history.append((user_input, ai_reply))

            turn += 1

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupt signal detected")
            try:
                confirm = input("Confirm exit? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    print(f"\n👋 Conversation ended! Total turns: {turn}")
                    break
            except:
                print(f"\n👋 Conversation ended! Total turns: {turn}")
                break
        except Exception as e:
            print(f"\n❌ Error processing request: {str(e)}")
            print("💡 Please try again or ask a new question")
