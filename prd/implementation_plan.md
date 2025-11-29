# Model Validation Workflow Implementation Plan

## Goal Description
Implement a robust Model Validation Workflow using LangGraph and LangChain, as described in the PRD. The system will automate the process from data upload to validation document generation, with human-in-the-loop interactions.

## User Review Required
- **Architecture**: Confirming the use of LangGraph StateGraph for workflow management.
- **Tools**: Confirming the set of tools to be implemented (File Upload, Data Analysis, Model Validation).

## Proposed Changes

### Workflow Layer
#### [NEW] [validation_workflow.py](file:///d:/works/code/AI/incubation/source/workflow/validation_workflow.py)
- **State Definition**: Define `ValidationState` with fields for `user_input`, `file_info`, `data_fields`, `validation_results`, etc.
- **Graph Construction**:
    - Create `StateGraph(ValidationState)`.
    - Add nodes: `process_file_upload`, `analyze_data_fields`, `verify_key_elements`, `prepare_validation_data`, `confirm_analysis_requirements`, `verify_calculation_logic`, `run_code_and_display_results`, `learn_knowledge_docs`, `execute_model_validation`, `generate_validation_document`.
    - Define edges to connect these nodes sequentially as per PRD Section 2.2, with potential conditional edges for user feedback loops.
- **Compilation**: Compile the graph to a runnable app.

### Agent Layer
#### [MODIFY] [agent_manager.py](file:///d:/works/code/AI/incubation/source/agent_manager.py)
- **Refactor**: Change `initialize_agent` to return the compiled LangGraph workflow instead of a simple `AgentExecutor`.
- **Integration**: Ensure the `ChatDeepSeek` model is used within the workflow nodes where LLM processing is required.

### Data Layer
#### [MODIFY] [data_handling.py](file:///d:/works/code/AI/incubation/source/data_handling.py)
- **Enhancement**: Add functions to support `analyze_data_fields` and `prepare_validation_data` nodes.
- **Tools**: Ensure `calculate_iv_tool` and others are accessible to the workflow.

### Tools Layer
#### [MODIFY] [tools.py](file:///d:/works/code/AI/incubation/source/tools.py)
- **New Tools**: Add `FileUploadTool` (simulated or actual) if `read_file_tool` is insufficient for the workflow's specific needs (e.g., parsing specific formats automatically).


## Verification Plan
### Automated Tests
- Unit tests for each workflow node.
- Integration test for the full graph execution.

### Manual Verification
- Run the workflow with a sample dataset (CSV).
- Verify the generated validation report.
