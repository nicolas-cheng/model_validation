from langchain.tools import tool
from pathlib import Path
import pandas as pd

@tool
def search_tool(query: str) -> str:
    """Tool for searching information. Enter search query and return related information."""
    return f"Search results for '{query}': Related information found."

@tool
def read_file_tool(file_path: str) -> str:
    """Read file content. Enter file path and return the text content of the file.
    
    Args:
        file_path: File path to read (relative or absolute path)
    
    Returns:
        String of file content, returns error message if an error occurs
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"
        
        if not path.is_file():
            return f"Error: '{file_path}' is not a file"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"Content of file '{file_path}':\n{content}"
    except UnicodeDecodeError:
        return f"Error: Unable to read file '{file_path}', it may be a binary file"
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"

@tool
def write_file_tool(file_path: str, content: str) -> str:
    """Write content to file. Overwrites if file exists, creates new file if it doesn't exist.
    
    Args:
        file_path: File path to write
        content: Content to write
    
    Returns:
        Operation result information
    """
    try:
        path = Path(file_path)
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Success: Content has been written to file '{file_path}'"
    except Exception as e:
        return f"Error writing to file '{file_path}': {str(e)}"

@tool
def list_files_tool(directory_path: str = ".") -> str:
    """List all files and subdirectories in the specified directory.
    
    Args:
        directory_path: Directory path to list, defaults to current directory
    
    Returns:
        List of files and subdirectories in the directory
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"Error: Directory '{directory_path}' does not exist"
        
        if not path.is_dir():
            return f"Error: '{directory_path}' is not a directory"
        
        items = []
        for item in sorted(path.iterdir()):
            item_type = "📁" if item.is_dir() else "📄"
            items.append(f"{item_type} {item.name}")
        
        if not items:
            return f"Directory '{directory_path}' is empty"
        
        return f"Contents of directory '{directory_path}':\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing directory '{directory_path}': {str(e)}"

@tool
def modify_file_tool(file_path: str, old_content: str, new_content: str) -> str:
    """Modify content in file. Find old_content and replace it with new_content.
    
    Args:
        file_path: File path to modify
        old_content: Original content to be replaced
        new_content: New content
    
    Returns:
        Operation result information
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"
        
        if not path.is_file():
            return f"Error: '{file_path}' is not a file"
        
        # Read file content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if content to replace exists
        if old_content not in content:
            return f"Error: Content to replace not found in file '{file_path}'"
        
        # Replace content
        modified_content = content.replace(old_content, new_content)
        count = content.count(old_content)
        
        # Write back to file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        return f"Success: Replaced {count} occurrences in file '{file_path}'"
    except Exception as e:
        return f"Error modifying file '{file_path}': {str(e)}"

@tool
def create_new_file(file_path: str, content: str = "") -> str:
    """Create a new file and write content.

    Args:
        file_path: File path to create.
        content: Initial content of the file, defaults to empty string.

    Returns:
        Operation result information.
    """
    try:
        path = Path(file_path)
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Create file and write content
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"Success: Created file '{file_path}'"
    except Exception as e:
        return f"Error creating file '{file_path}': {str(e)}"

@tool
def read_parquet_file(file_path: str) -> str:
    """Read Parquet file content and return first few rows of data.

    Args:
        file_path: Path to the Parquet file to read.

    Returns:
        First few rows of data as string, returns error message if an error occurs.
    """
    try:
        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        # Read Parquet file
        df = pd.read_parquet(file_path)

        # Return first few rows of data
        return f"Content of file '{file_path}':\n{df.head().to_string()}"
    except Exception as e:
        return f"Error reading Parquet file '{file_path}': {str(e)}"