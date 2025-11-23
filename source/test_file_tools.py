"""测试文件操作工具的独立脚本"""
from source.ochestration_agent import (
    read_file_tool,
    write_file_tool,
    list_files_tool,
    modify_file_tool
)
import os

def test_file_operations():
    """测试所有文件操作工具"""
    print("=" * 60)
    print("🧪 测试文件操作工具")
    print("=" * 60)
    
    # 测试1: 写入文件
    print("\n📝 测试1: 写入文件")
    test_file = "test_demo.txt"
    test_content = "这是一个测试文件。\n第二行内容。\nHello World!"
    result = write_file_tool.invoke({"file_path": test_file, "content": test_content})
    print(result)
    
    # 测试2: 读取文件
    print("\n📖 测试2: 读取文件")
    result = read_file_tool.invoke({"file_path": test_file})
    print(result)
    
    # 测试3: 列出当前目录
    print("\n📂 测试3: 列出当前目录")
    result = list_files_tool.invoke({"directory_path": "."})
    print(result)
    
    # 测试4: 修改文件内容
    print("\n✏️ 测试4: 修改文件内容")
    result = modify_file_tool.invoke({
        "file_path": test_file,
        "old_content": "测试文件",
        "new_content": "示例文件"
    })
    print(result)
    
    # 测试5: 读取修改后的文件
    print("\n📖 测试5: 读取修改后的文件")
    result = read_file_tool.invoke({"file_path": test_file})
    print(result)
    
    # 清理测试文件
    print("\n🧹 清理测试文件")
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"✅ 已删除测试文件: {test_file}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_file_operations()
