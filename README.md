# Model Validation System

A LangGraph-based automated model validation workflow system that streamlines data processing, analysis, and validation reporting using AI agents.

## 🎯 Overview

This project implements an intelligent model validation workflow using **LangGraph** and **LangChain**, designed to automate the entire validation process from data upload to document generation. The system leverages AI agents with specialized tools for file operations, data analysis, and statistical calculations.

## ✨ Key Features

- **🔄 LangGraph Workflow**: 10-node automated validation workflow with human-in-the-loop interactions
- **🤖 AI Agent**: ChatDeepSeek-powered agent with tool calling and structured output capabilities
- **📊 Data Analysis**: Information Value (IV) calculation and feature binning (quantile, width, tree-based)
- **📁 File Operations**: Comprehensive file handling tools for various formats (text, Parquet, etc.)
- **💬 Multi-turn Chat**: Interactive chat interface with conversation history management
- **🎨 LangGraph Studio**: Visual workflow debugging and monitoring via web UI

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   LangGraph Workflow                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. Process File Upload                             │ │
│  │ 2. Analyze Data Fields                             │ │
│  │ 3. Verify Key Elements                             │ │
│  │ 4. Prepare Validation Data                         │ │
│  │ 5. Confirm Analysis Requirements                   │ │
│  │ 6. Verify Calculation Logic                        │ │
│  │ 7. Run Code and Display Results                    │ │
│  │ 8. Learn Knowledge Docs                            │ │
│  │ 9. Execute Model Validation                        │ │
│  │ 10. Generate Validation Document                   │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    Agent Manager                         │
│  • ChatDeepSeek LLM (100K context, tool calling)        │
│  • Summarization middleware (80% trigger, 30% keep)     │
│  • 11 specialized tools                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────┬──────────────────┬──────────────────┐
│   File Tools     │   Data Tools     │   Chat Manager   │
│  • read_file     │  • calculate_iv  │  • Multi-turn    │
│  • write_file    │  • bin_feature   │  • Streaming     │
│  • list_files    │  • process_iv    │  • History       │
│  • modify_file   │                  │                  │
│  • create_file   │                  │                  │
│  • read_parquet  │                  │                  │
└──────────────────┴──────────────────┴──────────────────┘
```

## 📁 Project Structure

```
incubation/
├── source/                          # Source code directory
│   ├── workflow/                    # LangGraph workflow definitions
│   │   └── validation_workflow.py  # 10-node validation workflow
│   ├── agent_manager.py             # Agent initialization and configuration
│   ├── chat_manager.py              # Multi-turn chat interface
│   ├── flow_manager.py              # LangGraph flow initialization
│   ├── tools.py                     # File operation tools (8 tools)
│   ├── data_handling.py             # Data analysis tools (IV, binning)
│   ├── ochestration_agent.py        # Main orchestration entry point
│   ├── main.py                      # Application entry point
│   ├── test/                        # Test files
│   │   ├── test_data_handling_tools.py
│   │   └── test_file_tools.py
│   └── play_ground/                 # Experimental notebooks
├── prd/                             # Product requirements and planning
│   ├── implementation_plan.md       # Implementation plan
│   ├── task.md                      # Task tracking
│   └── AI_model_validation_report_GXS_Agent_Requirement.pdf
├── langgraph.json                   # LangGraph configuration
├── pyproject.toml                   # Project dependencies (uv)
├── start.bat                        # Quick start script (Windows)
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.12 or higher
- **uv**: Package manager (recommended) or pip
- **DeepSeek API Key**: Required for ChatDeepSeek model

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd incubation
```

2. **Install dependencies using uv**:
```bash
uv sync
```

Or using pip:
```bash
pip install .
```

3. **Set up environment variables**:
Create a `.env` file in the project root:
```env
DEEPSEEK_API_KEY=your_api_key_here
```

### Running the Application

#### Option 1: LangGraph Studio (Recommended)
Start the LangGraph development server with visual workflow debugging:

```bash
.\.venv\Scripts\langgraph.exe dev
```

Or using uv:
```bash
uv run langgraph dev
```

The LangGraph Studio UI will open at **http://127.0.0.1:2024** where you can:
- 📊 Visualize the workflow graph
- 🧪 Test the validation workflow interactively
- 🐛 Debug node execution
- 📈 Monitor workflow state

#### Option 2: Command Line Interface
Run the chat interface directly:

```bash
uv run source/main.py
```

Or on Windows:
```bash
start.bat
```

## 🛠️ Available Tools

### File Operation Tools (8)
| Tool | Description |
|------|-------------|
| `search_tool` | Search for information |
| `read_file_tool` | Read text file contents |
| `write_file_tool` | Write content to file |
| `list_files_tool` | List directory contents |
| `modify_file_tool` | Find and replace in files |
| `create_new_file` | Create new file with content |
| `read_parquet_file` | Read Parquet files |

### Data Analysis Tools (3)
| Tool | Description |
|------|-------------|
| `calculate_iv_tool` | Calculate Information Value for features |
| `bin_single_feature_tool` | Bin numeric features (quantile/width/tree) |
| `process_inputs_and_calculate_iv_tool` | End-to-end IV calculation from inputs |

## 📊 Workflow Nodes

The validation workflow consists of 10 sequential nodes:

1. **Process File Upload**: Handle data file upload and validation
2. **Analyze Data Fields**: Extract and analyze data schema
3. **Verify Key Elements**: Confirm key fields with user
4. **Prepare Validation Data**: Clean and prepare data
5. **Confirm Analysis Requirements**: Verify analysis parameters
6. **Verify Calculation Logic**: Validate calculation methods
7. **Run Code and Display Results**: Execute analysis and show results
8. **Learn Knowledge Docs**: Incorporate domain knowledge
9. **Execute Model Validation**: Perform validation calculations
10. **Generate Validation Document**: Create final report

## ⚙️ Configuration

### LangGraph Configuration (`langgraph.json`)
```json
{
    "dependencies": ["."],
    "graphs": {
        "model_validation": "./source/flow_manager.py:graph"
    },
    "env": ".env"
}
```

### Agent Configuration
- **Model**: ChatDeepSeek (`deepseek-chat`)
- **Max Input Tokens**: 100,000
- **Tool Calling**: Enabled
- **Structured Output**: Enabled
- **Max Retries**: 3
- **Middleware**: Summarization (80% trigger, 30% keep)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest source/test/

# Run specific test file
uv run pytest source/test/test_data_handling_tools.py
uv run pytest source/test/test_file_tools.py
```

## 📦 Dependencies

Key dependencies (see `pyproject.toml` for complete list):

- `langgraph-cli>=0.1.0` - LangGraph CLI and API
- `langchain>=1.1.0` - LangChain framework
- `langchain-deepseek>=1.0.1` - DeepSeek LLM integration
- `pandas>=2.3.3` - Data manipulation
- `scikit-learn>=1.7.2` - Machine learning utilities
- `streamlit>=1.51.0` - Web UI (optional)
- `flask>=3.1.2` - Web framework (optional)

## 🐛 Troubleshooting

### LangGraph Dev Server Fails to Start

**Issue**: `ModuleNotFoundError: No module named 'workflow'`

**Solution**: Ensure import paths are correct. The import should be:
```python
from source.workflow.validation_workflow import build_validation_workflow
```

**Issue**: `Required package 'langgraph-api' is not installed`

**Solution**: Install the complete LangGraph CLI package:
```bash
uv pip install "langgraph-cli[inmem]"
```

### Agent Initialization Fails

**Issue**: Missing DeepSeek API key

**Solution**: Set the `DEEPSEEK_API_KEY` environment variable in `.env` file

## 📝 Development

### Adding New Tools

1. Define the tool in `source/tools.py` using the `@tool` decorator
2. Add the tool to the tools list in `source/agent_manager.py`
3. Update the agent initialization to include the new tool

### Modifying the Workflow

1. Edit `source/workflow/validation_workflow.py`
2. Add/modify nodes and edges in the `build_validation_workflow` function
3. Test using LangGraph Studio at http://127.0.0.1:2024

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using LangGraph and LangChain**