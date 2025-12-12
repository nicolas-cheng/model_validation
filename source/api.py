"""FastAPI service exposing IV calculation, report generation, and IV query.

Endpoints:
- POST /calculate_iv : upload dataset, compute per-segment IV, return output paths
- POST /generate_report : build markdown report from existing IV CSVs
- POST /query_iv : return top-N IV features for a segment from generated CSVs

Run locally:
    uvicorn source.api:app --reload
"""
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
import pandas as pd

from source.tools.iv_engine import run_iv_by_segments
from source.iv.iv_report import generate_iv_markdown

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


def _load_iv_for_segment(segment: str) -> pd.DataFrame:
    csv_path = OUTPUT_DIR / f"{segment}_features_IV.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail=f"IV file not found for segment {segment}: {csv_path}")
    try:
        return pd.read_csv(csv_path, index_col=0, header=None, names=["IV"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to read IV file for {segment}: {exc}") from exc


@app.post("/query_iv")
async def query_iv_endpoint(segment: str = "MTB", top_n: int = 5):
    """Return top-N IV features for a given segment.

    Requires that per-segment IV CSVs have been generated in OUTPUT_DIR.
    """
    if top_n <= 0:
        raise HTTPException(status_code=400, detail="top_n must be positive")

    df = _load_iv_for_segment(segment)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"IV table for segment {segment} is empty")

    top = df.sort_values("IV", ascending=False).head(top_n)
    report_path = OUTPUT_DIR / "report.md"
    return {
        "segment": segment,
        "top_n": top_n,
        "source": str(OUTPUT_DIR / f"{segment}_features_IV.csv"),
        "top_features": top.reset_index().rename(columns={"index": "feature"}).to_dict(orient="records"),
        "report": str(report_path) if report_path.exists() else None,
    }
