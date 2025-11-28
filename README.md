# 模型验证系统

这是一个用于数据处理和模型验证的模块化系统，包含后端服务和工具函数。系统旨在通过模块化设计简化数据处理和验证流程。

## 系统架构

- **后端**：基于Python的模块化设计，包含数据处理、工具函数和流程管理代理
- **前端**：目前未包含前端界面，未来可扩展为基于HTML或其他框架的交互界面

## 文件结构

```
model_validation/
├── LICENSE
├── main.py                # 主程序入口
├── pyproject.toml         # 项目配置文件
├── README.md              # 使用说明文档
├── data/                  # 数据目录
│   └── input data/        # 输入数据目录
├── source/                # 源代码目录
│   ├── __init__.py        # 包初始化文件
│   ├── data_handling.py   # 数据处理工具
│   ├── ochestration_agent.py # 流程管理代理
│   ├── tools.py           # 工具函数
│   └── play_ground/       # 测试和实验目录
│       └── agent.demo_flow.ipynb # 示例Jupyter Notebook
└── test/                  # 测试目录
    ├── test_data_handling_tools.py # 数据处理工具测试
    └── test_file_tools.py # 文件工具测试
```

## 快速开始

### 1. 安装依赖

确保您已安装Python 3.12及以上版本和pip。然后安装所需的Python包：

```bash
pip install .
```

### 2. 启动主程序

在命令行中运行以下命令启动主程序：

```bash
python main.py
```

程序将输出：
```
Hello from incubation!
```

## 依赖列表

以下是项目的主要依赖：

- `flask>=3.1.2`
- `langchain>=1.0.8`
- `langchain-community>=0.4.1`
- `langchain-deepseek>=1.0.1`
- `langchain-ollama>=1.0.0`
- `pandas>=2.3.3`
- `scikit-learn>=1.7.2`
- `streamlit>=1.51.0`

## 注意事项

1. 确保Python环境满足最低版本要求。
2. 项目目前为基础版本，后续可扩展更多功能。

## 许可证

本项目采用MIT许可证.