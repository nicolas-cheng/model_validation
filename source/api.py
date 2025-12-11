"""FastAPI service exposing IV calculation, report generation, and IV Q&A placeholders.

Endpoints:
- POST /calculate_iv : upload dataset, compute per-segment IV, return output paths
- POST /generate_report : build markdown report from existing IV CSVs
- POST /query_iv : placeholder for IV Q&A over indexed artifacts

Run locally:
    uvicorn source.api:app --reload
"""
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException

from source.tools.iv_engine import run_iv_by_segments
from source.reports.iv_report import generate_iv_markdown

UPLOAD_DIR = Path("temp/uploads")
OUTPUT_DIR = Path("output")

app = FastAPI(title="IV POC API", version="0.1.0")


def _save_upload(file: UploadFile, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / file.filename
    try:
        with dest_path.open("wb") as f:
            f.write(file.file.read())
    finally:
        file.file.close()
    return dest_path


@app.post("/calculate_iv")
async def calculate_iv_endpoint(
    file: UploadFile = File(...),
    label_col: str = "label",
    segment_col: str = "segment",
    segments: Optional[List[str]] = None,
    n_bins: int = 10,
):
    segs = segments or ["MTB", "YNTB"]
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    saved_path = _save_upload(file, UPLOAD_DIR)

    try:
        written = run_iv_by_segments(
            input_path=saved_path,
            label_col=label_col,
            segment_col=segment_col,
            segments=segs,
            output_dir=OUTPUT_DIR,
            n_bins=n_bins,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"input": str(saved_path), "written_files": [str(p) for p in written]}


@app.post("/generate_report")
async def generate_report_endpoint(
    segments: Optional[List[str]] = None,
    report_name: str = "report.md",
):
    segs = segments or ("MTB", "YNTB")
    try:
        report_path = generate_iv_markdown(output_dir=OUTPUT_DIR, segments=segs, report_name=report_name)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"report_path": str(report_path)}


@app.post("/query_iv")
async def query_iv_endpoint(question: str):
    # Placeholder: RAG/index-backed Q&A to be implemented.
    return {"answer": "IV Q&A not implemented yet", "question": question}
