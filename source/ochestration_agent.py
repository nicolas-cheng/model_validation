from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain.tools import tool
from pathlib import Path
from source.data_handling import bin_single_feature_tool
from dataclasses import dataclass

# 初始化 LLM
model = ChatDeepSeek(
    model="deepseek-chat",
    #temperature=0,
    #max_tokens=None,
    #timeout=None,
    max_retries=2,
    # api_key="...",
    # other params...
)

print(f"已初始化模型: {model.model_name}")

# 定义工具
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

@dataclass
class UserContext:
    user_id: str

# 初始化 agent
tools = [
    search_tool,
    read_file_tool,
    write_file_tool,
    list_files_tool,
    modify_file_tool
]
try:
    agent = create_agent(
        model=model,
        tools=tools,
        context_schema=UserContext,
        system_prompt="you are a helpful assistant."
    )
    print("Agent 初始化成功")
    print(f"已加载 {len(tools)} 个工具: {', '.join([tool.name for tool in tools])}")
except Exception as e:
    print(f"Agent 初始化失败: {e}")
    agent = None

def extract_assistant_message(response):
    """从响应中提取助手的消息"""
    try:
        if isinstance(response, dict) and 'messages' in response:
            # 获取最后一条助手消息
            for msg in reversed(response['messages']):
                if hasattr(msg, 'content') and hasattr(msg, 'type'):
                    if msg.type == 'ai' or msg.type == 'assistant':
                        return msg.content
        elif hasattr(response, 'content'):
            return response.content
        return str(response)
    except Exception:
        return str(response)

def run_chat_loop():
    """运行多轮对话循环"""
    if agent is None:
        print("Agent 未初始化，无法启动对话")
        return
    
    print("\n" + "="*60)
    print("🤖 AI 助手多轮对话系统")
    print("="*60)
    print("💡 提示：")
    print("  - 输入您的问题开始对话")
    print("  - 输入 'exit' 或 '退出' 结束对话")
    print("  - 输入 'clear' 或 '清空' 清除对话历史")
    print("="*60)
    
    conversation_history = []
    turn = 0
    
    while True:
        try:
            # 获取用户输入
            user_input = input(f"\n[第 {turn + 1} 轮] 你: ").strip()
            
            if not user_input:
                continue
            
            # 检查退出命令
            if user_input.lower() in ['exit', '退出', 'quit', 'q']:
                print("\n👋 对话已结束，再见！")
                print(f"📊 本次对话共 {turn} 轮")
                break
            
            # 检查清空历史命令
            if user_input.lower() in ['clear', '清空', 'reset']:
                conversation_history = []
                turn = 0
                print("✅ 对话历史已清空")
                continue
            
            # 构建包含历史的输入
            content = ""
            if conversation_history:
                content = "\n\n对话历史:\n"
                for i, (user_msg, ai_msg) in enumerate(conversation_history[-3:], 1):  # 只保留最近3轮
                    content += f"第{i}轮 - 用户: {user_msg}\n"
                    content += f"第{i}轮 - AI: {ai_msg}\n"
                content += f"\n当前问题: {user_input}"
            else:
                content = user_input
            
            # 调用 agent
            print("AI is thinking...", end='', flush=True)
            
            input_message = {
                
            }

            response = agent.invoke(
            {"messages": [{"role": "user", "content": content}]},
            context=UserContext(user_id="user123"))

            print("\r" + " " * 30 + "\r", end='')  # 清除"思考中"提示
            
            # 提取回复
            if isinstance(response, dict) and 'output' in response:
                ai_reply = response['output']
            else:
                ai_reply = extract_assistant_message(response)
            
            # 显示回复
            print(f"AI: {ai_reply}")
            
            # 保存到历史
            conversation_history.append((user_input, ai_reply))
            turn += 1
            
        except KeyboardInterrupt:
            print("\n\n⚠️  检测到中断信号")
            confirm = input("确认退出对话？(y/n): ").strip().lower()
            if confirm in ['y', 'yes', '是']:
                print(f"\n👋 对话已结束！共进行了 {turn} 轮对话")
                break
        except Exception as e:
            print(f"\n❌ 处理请求时出错: {str(e)}")
            print("💡 请重试或输入新的问题")

# 运行多轮对话
if __name__ == "__main__":
    run_chat_loop()
