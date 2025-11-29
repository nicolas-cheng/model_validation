from typing import TypedDict, Optional, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

# Import tools
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from source.tools import read_file_tool, read_parquet_file, list_files_tool
from source.data_handling import process_inputs_and_calculate_iv_tool

class ValidationState(TypedDict):
    """
    State definition for the Model Validation Workflow.
    """
    user_input: str
    messages: Annotated[List[BaseMessage], add_messages]
    file_info: Optional[Dict[str, Any]]
    data_fields: Optional[Dict[str, Any]]
    key_elements: Optional[Dict[str, Any]]
    validation_data: Optional[Any] # DataFrame or similar, might need to be a path if serializing
    analysis_requirements: Optional[Dict[str, Any]]
    calculation_logic_verified: bool
    validation_results: Optional[Dict[str, Any]]
    knowledge_docs: Optional[List[str]]
    model_performance: Optional[Dict[str, Any]]
    validation_document: Optional[str]
    current_step: str

# Node definitions

def process_file_upload(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 1: Process file upload"""
    print("--- Process File Upload ---")
    messages = state.get("messages", [])
    if not messages:
        return {"current_step": "process_file_upload", "messages": [AIMessage(content="Please provide the file path for the data you want to validate.")]}
    
    last_message = messages[-1]
    if isinstance(last_message, HumanMessage):
        # Use LLM to acknowledge and extract file information WITHOUT tool calls
        # This prevents the "tool_calls must be followed by tool messages" error
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant for model validation. The user is providing a file path or data information. Acknowledge their input and ask for confirmation or additional details if needed. Do NOT call any tools."),
            MessagesPlaceholder(variable_name="messages"),
        ])
        # IMPORTANT: Do not use bind_tools() here to avoid tool call errors
        chain = prompt | llm
        result = chain.invoke({"messages": messages})
        return {"messages": [result], "current_step": "process_file_upload"}
    
    return {"current_step": "process_file_upload"}

def analyze_data_fields(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 2: Analyze data fields"""
    print("--- Analyze Data Fields ---")
    # Placeholder for data analysis logic
    return {"current_step": "analyze_data_fields"}

def verify_key_elements(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 3: Verify key elements with user"""
    print("--- Verify Key Elements ---")
    return {"current_step": "verify_key_elements"}

def prepare_validation_data(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 4: Prepare validation data"""
    print("--- Prepare Validation Data ---")
    return {"current_step": "prepare_validation_data"}

def confirm_analysis_requirements(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 5: Confirm analysis requirements"""
    print("--- Confirm Analysis Requirements ---")
    return {"current_step": "confirm_analysis_requirements"}

def verify_calculation_logic(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 6: Verify calculation logic"""
    print("--- Verify Calculation Logic ---")
    return {"current_step": "verify_calculation_logic"}

def run_code_and_display_results(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 7: Run code and display results"""
    print("--- Run Code and Display Results ---")
    return {"current_step": "run_code_and_display_results"}

def learn_knowledge_docs(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 8: Learn from knowledge documents"""
    print("--- Learn Knowledge Docs ---")
    return {"current_step": "learn_knowledge_docs"}

def execute_model_validation(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 9: Execute model validation"""
    print("--- Execute Model Validation ---")
    return {"current_step": "execute_model_validation"}

def generate_validation_document(state: ValidationState, llm) -> Dict[str, Any]:
    """Node 10: Generate validation document"""
    print("--- Generate Validation Document ---")
    return {"current_step": "generate_validation_document"}

def build_validation_workflow(llm):
    """Builds the LangGraph workflow."""
    workflow = StateGraph(ValidationState)

    # Helper to curry llm into nodes
    def node_wrapper(node_func):
        return lambda state: node_func(state, llm)

    # Add nodes
    workflow.add_node("process_file_upload", node_wrapper(process_file_upload))
    workflow.add_node("analyze_data_fields", node_wrapper(analyze_data_fields))
    workflow.add_node("verify_key_elements", node_wrapper(verify_key_elements))
    workflow.add_node("prepare_validation_data", node_wrapper(prepare_validation_data))
    workflow.add_node("confirm_analysis_requirements", node_wrapper(confirm_analysis_requirements))
    workflow.add_node("verify_calculation_logic", node_wrapper(verify_calculation_logic))
    workflow.add_node("run_code_and_display_results", node_wrapper(run_code_and_display_results))
    workflow.add_node("learn_knowledge_docs", node_wrapper(learn_knowledge_docs))
    workflow.add_node("execute_model_validation", node_wrapper(execute_model_validation))
    workflow.add_node("generate_validation_document", node_wrapper(generate_validation_document))

    # Add edges (Linear flow for now, will add conditionals later)
    workflow.set_entry_point("process_file_upload")
    workflow.add_edge("process_file_upload", "analyze_data_fields")
    workflow.add_edge("analyze_data_fields", "verify_key_elements")
    workflow.add_edge("verify_key_elements", "prepare_validation_data")
    workflow.add_edge("prepare_validation_data", "confirm_analysis_requirements")
    workflow.add_edge("confirm_analysis_requirements", "run_code_and_display_results")
    workflow.add_edge("run_code_and_display_results", "verify_calculation_logic")
    workflow.add_edge("verify_calculation_logic", "learn_knowledge_docs")
    workflow.add_edge("learn_knowledge_docs", "execute_model_validation")
    workflow.add_edge("execute_model_validation", "generate_validation_document")
    workflow.add_edge("generate_validation_document", END)

    return workflow.compile()
