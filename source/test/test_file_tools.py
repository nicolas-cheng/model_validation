"""Test ochestration_agent tools"""
import os
import sys
from pathlib import Path

# Add the project root to sys.path
# This ensures that the `source` module can be imported correctly
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from source.ochestration_agent import (
    search_tool,
    read_file_tool,
    write_file_tool,
    list_files_tool,
    modify_file_tool
)

def test_ochestration_agent_tools():
    """Test all tool functions in ochestration_agent."""
    print("=" * 60)
    print("🧪 Testing ochestration_agent tools")
    print("=" * 60)

    # Test 1: Search tool
    print("\n🔍 Test 1: Search tool")
    query = "Test search functionality"
    result = search_tool.invoke({"query": query})
    print(result)

    # Test 2: Write to file
    print("\n📝 Test 2: Write to file")
    test_file = "test_demo.txt"
    test_content = "This is a test file.\nSecond line content.\nHello World!"
    result = write_file_tool.invoke({"file_path": test_file, "content": test_content})
    print(result)

    # Test 3: Read file
    print("\n📖 Test 3: Read file")
    result = read_file_tool.invoke({"file_path": test_file})
    print(result)

    # Test 4: List current directory
    print("\n📂 Test 4: List current directory")
    result = list_files_tool.invoke({"directory_path": "."})
    print(result)

    # Test 5: Modify file content
    print("\n✏️ Test 5: Modify file content")
    result = modify_file_tool.invoke({
        "file_path": test_file,
        "old_content": "test file",
        "new_content": "example file"
    })
    print(result)

    # Test 6: Read modified file
    print("\n📖 Test 6: Read modified file")
    result = read_file_tool.invoke({"file_path": test_file})
    print(result)

    # Clean up test file
    print("\n🧹 Cleaning up test file")
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"✅ Deleted test file: {test_file}")

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_ochestration_agent_tools()
