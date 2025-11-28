from langchain.tools import tool
from pathlib import Path
import pandas as pd

@tool
def search_tool(query: str) -> str:
    """用于搜索信息的工具。输入搜索查询，返回相关信息。"""
    return f"这是关于 '{query}' 的搜索结果：已找到相关信息。"

@tool
def read_file_tool(file_path: str) -> str:
    """读取文件内容。输入文件路径，返回文件的文本内容。
    
    Args:
        file_path: 要读取的文件路径（相对路径或绝对路径）
    
    Returns:
        文件内容的字符串，如果出错则返回错误信息
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"错误：文件 '{file_path}' 不存在"
        
        if not path.is_file():
            return f"错误：'{file_path}' 不是一个文件"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"文件 '{file_path}' 的内容：\n{content}"
    except UnicodeDecodeError:
        return f"错误：无法读取文件 '{file_path}'，可能是二进制文件"
    except Exception as e:
        return f"读取文件 '{file_path}' 时出错: {str(e)}"

@tool
def write_file_tool(file_path: str, content: str) -> str:
    """写入内容到文件。如果文件已存在则覆盖，不存在则创建新文件。
    
    Args:
        file_path: 要写入的文件路径
        content: 要写入的内容
    
    Returns:
        操作结果信息
    """
    try:
        path = Path(file_path)
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"成功：已将内容写入文件 '{file_path}'"
    except Exception as e:
        return f"写入文件 '{file_path}' 时出错: {str(e)}"

@tool
def list_files_tool(directory_path: str = ".") -> str:
    """列出指定目录中的所有文件和子目录。
    
    Args:
        directory_path: 要列出的目录路径，默认为当前目录
    
    Returns:
        目录中的文件和子目录列表
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return f"错误：目录 '{directory_path}' 不存在"
        
        if not path.is_dir():
            return f"错误：'{directory_path}' 不是一个目录"
        
        items = []
        for item in sorted(path.iterdir()):
            item_type = "📁" if item.is_dir() else "📄"
            items.append(f"{item_type} {item.name}")
        
        if not items:
            return f"目录 '{directory_path}' 是空的"
        
        return f"目录 '{directory_path}' 的内容：\n" + "\n".join(items)
    except Exception as e:
        return f"列出目录 '{directory_path}' 时出错: {str(e)}"

@tool
def modify_file_tool(file_path: str, old_content: str, new_content: str) -> str:
    """修改文件中的内容。查找old_content并替换为new_content。
    
    Args:
        file_path: 要修改的文件路径
        old_content: 要被替换的原内容
        new_content: 新的内容
    
    Returns:
        操作结果信息
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"错误：文件 '{file_path}' 不存在"
        
        if not path.is_file():
            return f"错误：'{file_path}' 不是一个文件"
        
        # 读取文件内容
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否存在要替换的内容
        if old_content not in content:
            return f"错误：在文件 '{file_path}' 中未找到要替换的内容"
        
        # 替换内容
        modified_content = content.replace(old_content, new_content)
        count = content.count(old_content)
        
        # 写回文件
        with open(path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        return f"成功：已在文件 '{file_path}' 中替换了 {count} 处内容"
    except Exception as e:
        return f"修改文件 '{file_path}' 时出错: {str(e)}"

@tool
def create_new_file(file_path: str, content: str = "") -> str:
    """创建一个新文件并写入内容。

    Args:
        file_path: 要创建的文件路径。
        content: 文件的初始内容，默认为空字符串。

    Returns:
        操作结果信息。
    """
    try:
        path = Path(file_path)
        # 确保父目录存在
        path.parent.mkdir(parents=True, exist_ok=True)

        # 创建文件并写入内容
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        return f"成功：已创建文件 '{file_path}'"
    except Exception as e:
        return f"创建文件 '{file_path}' 时出错: {str(e)}"

@tool
def read_parquet_file(file_path: str) -> str:
    """读取 Parquet 文件内容并返回前几行数据。

    Args:
        file_path: 要读取的 Parquet 文件路径。

    Returns:
        文件的前几行数据（字符串形式），如果出错则返回错误信息。
    """
    try:
        # 检查文件是否存在
        path = Path(file_path)
        if not path.exists():
            return f"错误：文件 '{file_path}' 不存在"

        # 读取 Parquet 文件
        df = pd.read_parquet(file_path)

        # 返回前几行数据
        return f"文件 '{file_path}' 的内容：\n{df.head().to_string()}"
    except Exception as e:
        return f"读取 Parquet 文件 '{file_path}' 时出错: {str(e)}"