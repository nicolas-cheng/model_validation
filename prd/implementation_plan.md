# IV POC Project Implementation Plan

## Current Progress (as of 2025-12-11)
- ✅ Per-segment IV auto-calculation engine implemented (`source/tools/iv_engine.py`), generates `output/MTB_features_IV.csv` and `output/YNTB_features_IV.csv`
- ✅ IV markdown report generator implemented (`source/reports/iv_report.py`), outputs `output/report.md`
- ✅ Agent registered IV calculation and report tools (`agent_manager.py`)
- ✅ Basic test case available (`source/test/test_iv_engine.py`)
- ✅ FastAPI backend with IV endpoints (`source/api.py`): `/calculate_iv`, `/generate_report`, `/query_iv` placeholder; deps added (`fastapi`, `uvicorn`, `python-multipart`)
- ⏳ RAG index, frontend UI, LangGraph workflow, and other advanced features are pending

---

## Step-by-Step Implementation Plan

### 1. IV Auto-Calculation Engine (Dec 9–16)
- Status: ✅ done
- Feature binning and IV calculation
  - API: `run_iv_by_segments(input_path, label_col, segment_col, segments, ...) -> List[Path]`
  - Function: Load CSV/Parquet, group by segment, calculate IV for each feature, output per-segment CSV
- Result export
  - API: `export_iv_report(iv_results, output_path)`

### 2. Report Generation Module (Dec 16–22)
- Status: ✅ markdown summary done; charts/stability TBD
- IV tables and markdown report
  - API: `generate_iv_markdown(output_dir, segments, report_name) -> Path`
  - Function: Summarize per-segment IV results, generate markdown report
- Feature stability analysis (if required)
  - API: `analyze_feature_stability(train_df, test_df) -> pd.DataFrame`

### 3. RAG Index & Multimodal Processing (Dec 11–20)
- Status: ⏳ not started (placeholder)
- Multimodal data processing
  - API: `process_multimodal_data(artifacts) -> List[Document]`
- Build vector index
  - API: `build_vector_index(documents) -> VectorStoreIndex`
  - Function: Convert reports, tables, etc. into a searchable knowledge base

### 4. Chatbot & API Development (Dec 11–23)
- Status: ⚠️ backend live; frontend not started; `/query_iv` is placeholder
- Backend API
  - API: `POST /calculate_iv`, function: `calculate_iv_endpoint(file: UploadFile)`
  - API: `POST /generate_report`, function: `generate_report_endpoint()`
  - API: `POST /query_iv`, function: `query_iv_endpoint(question: str)` (stub)
- Frontend UI
  - Use Streamlit/React to build interactive interface for file upload, result display, and Q&A (TBD)

### 5. Testing & Evaluation (Dec 24–Jan 6)
- Status: 🟡 basic test in place; coverage TBD
- Test datasets and cases
  - Example: `test_data.csv`
- Evaluation metrics
  - API: `evaluate_iv_results(predicted, expected) -> dict`
  - Function: Accuracy, coverage, etc.

---

## Key Dependencies

- Data Processing: Pandas, NumPy, scikit-learn
- AI/ML: LangChain, LlamaIndex, DeepSeek API
- Backend: FastAPI, SQLAlchemy (if database needed)
- Frontend: Streamlit/React, Plotly/Dash (visualization)
