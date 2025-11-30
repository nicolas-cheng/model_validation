from agent_manager import extract_assistant_message
from langchain_core.messages import HumanMessage
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid

# Platform-specific imports for multi-line input
if os.name == 'nt':  # Windows
    import msvcrt
else:  # Unix/Linux/Mac
    import tty
    import termios


def get_temp_upload_dir():
    """Get or create the temporary upload directory."""
    # Create temp directory in project root
    project_root = Path(__file__).parent.parent
    temp_dir = project_root / "temp" / "uploads"
    
    # Create directory if it doesn't exist
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    return temp_dir


def copy_file_to_temp(original_path: Path, temp_dir: Path) -> Path:
    """
    Copy uploaded file to temp directory with unique name.
    
    Args:
        original_path: Path to the original file
        temp_dir: Temporary directory path
        
    Returns:
        Path to the copied file in temp directory
    """
    # Generate unique filename to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    original_name = original_path.name  # This is a string
    file_ext = original_path.suffix
    
    # Create unique filename: original_name_timestamp_uuid.ext
    if file_ext:
        # Use Path.stem to get name without extension
        name_without_ext = original_path.stem
        new_name = f"{name_without_ext}_{timestamp}_{unique_id}{file_ext}"
    else:
        new_name = f"{original_name}_{timestamp}_{unique_id}"
    
    temp_file_path = temp_dir / new_name
    
    # Copy file to temp directory
    try:
        shutil.copy2(original_path, temp_file_path)
        print(f"📁 File copied to: {temp_file_path}")
        return temp_file_path
    except Exception as e:
        print(f"❌ Failed to copy file to temp directory: {e}")
        return None


def list_temp_files(temp_dir: Path) -> list:
    """List all files in the temp upload directory."""
    try:
        files = []
        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    except Exception as e:
        print(f"❌ Error listing temp files: {e}")
        return []


def cleanup_old_files(temp_dir: Path, max_age_hours: int = 24):
    """Clean up files older than specified hours."""
    try:
        current_time = datetime.now()
        removed_count = 0
        
        for file_path in temp_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.total_seconds() > max_age_hours * 3600:
                    file_path.unlink()
                    removed_count += 1
        
        if removed_count > 0:
            print(f"🧹 Cleaned up {removed_count} old files from temp directory")
            
    except Exception as e:
        print(f"❌ Error cleaning up old files: {e}")


def handle_file_upload():
    """
    Handle file upload from user with persistence to temp folder.
    Returns file path and basic file info.
    """
    print("\n📁 File Upload Mode")
    print("💡 Enter the file path (relative or absolute)")
    print("   Examples:")
    print("   - data/myfile.csv")
    print("   - C:/Users/username/Documents/data.parquet")
    print("   - /home/user/data/file.json")
    print("   - For paths with spaces, use quotes: \"C:/My Documents/file.csv\"")
    print("   Type 'cancel' to exit file upload mode")
    print("-" * 60)
    
    # Get temp directory ready
    temp_dir = get_temp_upload_dir()
    
    # Clean up old files (older than 24 hours)
    cleanup_old_files(temp_dir)
    
    # Show existing files in temp directory
    existing_files = list_temp_files(temp_dir)
    if existing_files:
        print(f"📂 Existing files in temp directory ({len(existing_files)} files):")
        for i, file_info in enumerate(existing_files[:5], 1):  # Show last 5 files
            age_hours = (datetime.now() - file_info['modified']).total_seconds() / 3600
            print(f"  {i}. {file_info['name']} ({file_info['size']:,} bytes, {age_hours:.1f}h ago)")
        if len(existing_files) > 5:
            print(f"  ... and {len(existing_files) - 5} more files")
        print()
    
    while True:
        try:
            file_path = input("📎 Enter file path: ").strip()
            
            if file_path.lower() == 'cancel':
                return None, None
            
            if not file_path:
                print("❌ Please enter a valid file path.")
                continue
            
            # Handle quoted paths (remove surrounding quotes if present)
            if (file_path.startswith('"') and file_path.endswith('"')) or \
               (file_path.startswith("'") and file_path.endswith("'")):
                file_path = file_path[1:-1].strip()
            
            # Convert to Path object and check if file exists
            path = Path(file_path)
            
            if not path.exists():
                print(f"❌ File not found: {file_path}")
                print("💡 Tips:")
                print("   - Check if the file path is correct")
                print("   - Use absolute paths for better reliability")
                print("   - For paths with spaces, enclose in quotes")
                print(f"   - Current working directory: {Path.cwd()}")
                continue
            
            if not path.is_file():
                print(f"❌ Path is not a file: {file_path}")
                continue
            
            # Get file info
            file_size = path.stat().st_size
            file_ext = path.suffix.lower()
            
            # Check file size (limit to 100MB for now)
            max_size = 100 * 1024 * 1024  # 100MB
            if file_size > max_size:
                print(f"❌ File too large: {file_size:,} bytes (max: {max_size:,} bytes)")
                continue
            
            # Supported file types
            supported_types = {'.csv', '.json', '.parquet', '.txt', '.xlsx', '.xls'}
            if file_ext not in supported_types:
                print(f"⚠️  Warning: File type '{file_ext}' may not be supported.")
                print(f"   Supported types: {', '.join(supported_types)}")
                
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    continue
            
            print(f"✅ File selected: {path.name}")
            print(f"   Size: {file_size:,} bytes")
            print(f"   Type: {file_ext}")
            print(f"   Original path: {path.absolute()}")
            
            confirm = input("Upload this file to temp directory? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                # Copy file to temp directory
                temp_file_path = copy_file_to_temp(path, temp_dir)
                
                if temp_file_path and temp_file_path.exists():
                    print(f"✅ File successfully uploaded to temp directory!")
                    print(f"   Temp path: {temp_file_path}")
                    
                    return str(temp_file_path), {
                        'name': path.name,
                        'size': file_size,
                        'type': file_ext,
                        'original_path': str(path.absolute()),
                        'temp_path': str(temp_file_path),
                        'uploaded_at': datetime.now()
                    }
                else:
                    print("❌ Failed to copy file to temp directory")
                    return None, None
            else:
                print("❌ Upload cancelled.")
                return None, None
                
        except KeyboardInterrupt:
            print("\n❌ File upload cancelled.")
            return None, None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None, None


def get_file_upload_command():
    """
    Get file upload command from user input with persistence to temp folder.
    """
    print("\n📁 File Upload Options:")
    print("1. Type 'upload' or 'file' to upload a file")
    print("2. Type 'upload <path>' to directly specify a file path")
    print("   For paths with spaces: upload \"C:/My Documents/file.csv\"")
    print("3. Type 'cancel' to cancel")
    
    # Get temp directory ready
    temp_dir = get_temp_upload_dir()
    
    user_input = input("📎 Choose option: ").strip()
    
    if user_input.lower() in ['upload', 'file']:
        return handle_file_upload()
    elif user_input.lower().startswith('upload '):
        file_path = user_input[7:].strip()  # Remove 'upload ' prefix
        if not file_path:
            print("❌ Please provide a file path after 'upload'")
            return None, None
        
        # Handle quoted paths (remove surrounding quotes if present)
        if (file_path.startswith('"') and file_path.endswith('"')) or \
           (file_path.startswith("'") and file_path.endswith("'")):
            file_path = file_path[1:-1].strip()
        
        path = Path(file_path)
        if path.exists() and path.is_file():
            file_size = path.stat().st_size
            print(f"✅ File found: {path.name}")
            print(f"   Size: {file_size:,} bytes")
            print(f"   Original path: {path.absolute()}")
            
            confirm = input("Upload this file to temp directory? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                # Copy file to temp directory
                temp_file_path = copy_file_to_temp(path, temp_dir)
                
                if temp_file_path and temp_file_path.exists():
                    print(f"✅ File successfully uploaded to temp directory!")
                    print(f"   Temp path: {temp_file_path}")
                    
                    return str(temp_file_path), {
                        'name': path.name,
                        'size': file_size,
                        'type': path.suffix.lower(),
                        'original_path': str(path.absolute()),
                        'temp_path': str(temp_file_path),
                        'uploaded_at': datetime.now()
                    }
                else:
                    print("❌ Failed to copy file to temp directory")
                    return None, None
            else:
                print("❌ Upload cancelled.")
                return None, None
        else:
            print(f"❌ File not found: {file_path}")
            print("💡 Tips:")
            print("   - Check if the file path is correct")
            print("   - Use absolute paths for better reliability")
            print("   - For paths with spaces, enclose in quotes")
            print(f"   - Current working directory: {Path.cwd()}")
            return None, None
    elif user_input.lower() == 'cancel':
        return None, None
    else:
        print("❌ Invalid option.")
        return None, None


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
    Get input from user. Press Enter to send message.
    This works reliably across all platforms.
    """
    print(prompt)
    print("💡 Tip: Press Enter to send your message")
    print("-" * 60)
    
    try:
        line = input()
        return line.strip()
    except EOFError:
        return ""


def run_chat_loop(agent, mode="legacy"):
    """Run a multi-turn chat loop with support for streaming and legacy output modes."""
    print("\n" + "="*60)
    print("🤖 AI Assistant Multi-turn Chat System")
    print("="*60)
    print("💡 Tips:")
    print("  - Type your message and press Enter to send")
    print("  - Type 'upload' or 'file' to upload a file")
    print("  - Type 'upload <path>' to upload a specific file")
    print("  - Type 'list' to show uploaded files in temp directory")
    print("  - Type 'exit' to end the conversation")
    print("  - Type 'clear' to reset the conversation history")
    print("="*60)

    conversation_history = []
    uploaded_files = []  # Track uploaded files
    temp_dir = get_temp_upload_dir()  # Get temp directory
    turn = 0

    while True:
        try:
            user_input = get_simple_multiline_input(f"\n[Turn {turn + 1}] You:")

            if not user_input:
                continue

            # Handle exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Conversation ended. Goodbye!")
                print(f"📊 Total turns: {turn}")
                break

            # Handle clear commands
            if user_input.lower() in ['clear', 'reset']:
                conversation_history = []
                uploaded_files = []  # Clear uploaded files too
                turn = 0
                print("✅ Conversation history and uploaded files cleared")
                continue

            # Handle list temp files command
            if user_input.lower() in ['list', 'files', 'temp']:
                existing_files = list_temp_files(temp_dir)
                if existing_files:
                    print(f"\n📂 Files in temp directory ({len(existing_files)} files):")
                    print("-" * 60)
                    for i, file_info in enumerate(existing_files, 1):
                        age_hours = (datetime.now() - file_info['modified']).total_seconds() / 3600
                        print(f"  {i}. {file_info['name']}")
                        print(f"     Size: {file_info['size']:,} bytes")
                        print(f"     Age: {age_hours:.1f} hours ago")
                        print(f"     Path: {file_info['path']}")
                        if i < len(existing_files):
                            print()
                else:
                    print("\n📂 No files in temp directory")
                continue

            # Handle file upload commands
            if user_input.lower() in ['upload', 'file'] or user_input.lower().startswith('upload '):
                file_path, file_info = get_file_upload_command()
                if file_path and file_info:
                    uploaded_files.append(file_info)
                    # Create a message about the uploaded file
                    file_message = f"📁 File uploaded: {file_info['name']} ({file_info['size']:,} bytes, {file_info['type']})\nOriginal path: {file_info['original_path']}\nTemp path: {file_info['temp_path']}\n\nPlease analyze this file."
                    
                    content = ""
                    if conversation_history:
                        content = "\n\nConversation History:\n"
                        for i, (user_msg, ai_msg) in enumerate(conversation_history[-3:], 1):
                            content += f"Turn {i} - User: {user_msg}\n"
                            content += f"Turn {i} - AI: {ai_msg}\n"
                        content += f"\nCurrent Request: {file_message}"
                    else:
                        content = file_message
                    
                    print("\n" + "-" * 60)
                    print("🤔 AI is analyzing your file...")
                    print("-" * 60)
                    
                    # Process the file upload with the agent
                    if mode == "stream":
                        last_chunk_content = ""
                        for chunk in agent.stream({"messages": [{"role": "user", "content": content}]},
                                                  stream_mode="messages"):
                            print(chunk[0].content, end='', flush=True)
                            last_chunk_content = chunk[0].content

                        print("✅ Done")  # Add completion message
                        conversation_history.append((f"📁 Uploaded: {file_info['name']}", last_chunk_content))
                    else:
                        response = agent.invoke({"messages": [HumanMessage(content=content)]})
                        ai_reply = extract_assistant_message(response)
                        print(f"🤖 AI: {ai_reply}")
                        print("✅ Done")
                        conversation_history.append((f"📁 Uploaded: {file_info['name']}", ai_reply))
                    
                    turn += 1
                continue

            # Regular text message
            content = ""
            if conversation_history:
                content = "\n\nConversation History:\n"
                for i, (user_msg, ai_msg) in enumerate(conversation_history[-3:], 1):
                    content += f"Turn {i} - User: {user_msg}\n"
                    content += f"Turn {i} - AI: {ai_msg}\n"
                
                # Add uploaded files info to context
                if uploaded_files:
                    content += "\n📁 Uploaded Files:\n"
                    for i, file_info in enumerate(uploaded_files, 1):
                        content += f"  {i}. {file_info['name']} ({file_info['size']:,} bytes, {file_info['type']})\n"
                        content += f"     Temp path: {file_info['temp_path']}\n"
                
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

                print("✅ Done")  # Add completion message
                # Save to history
                conversation_history.append((user_input, last_chunk_content))
            else:
                # Use legacy output mode
                response = agent.invoke(
                    {"messages": [HumanMessage(content=content)]}
                )
                ai_reply = extract_assistant_message(response)
                print(f"🤖 AI: {ai_reply}")
                print("✅ Done")  # Add completion message

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
