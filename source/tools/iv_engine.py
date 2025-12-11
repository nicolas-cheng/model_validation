"""Information Value (IV) runner utilities.

Provides helpers to:
- load CSV/Parquet
- compute IV per segment using existing calculate_iv
- write per-feature IV tables to output directory
- expose LangChain tools for agent use
"""
import json
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import pandas as pd
from langchain.tools import tool

from .data_handling import calculate_iv


def _load_dataframe(input_path: Path) -> pd.DataFrame:
    """Load CSV or Parquet into DataFrame."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if input_path.suffix.lower() == ".csv":
        return pd.read_csv(input_path)
    if input_path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(input_path)
    raise ValueError(f"Unsupported file type: {input_path.suffix}")


def _ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)


def run_iv_by_segments(
    input_path: Path,
    label_col: str,
    segment_col: str,
    segments: Sequence[str],
    feature_cols: Optional[List[str]] = None,
    binning_method: str = "quantile",
    n_bins: int = 10,
    min_leaf_frac: float = 0.05,
    positive_label=1,
    output_dir: Path = Path("output"),
) -> List[Path]:
    """Compute IV per segment and write per-feature IV CSVs.

    Returns list of written file paths (one per segment).
    """
    df = _load_dataframe(Path(input_path))
    if segment_col not in df.columns:
        raise ValueError(f"Segment column '{segment_col}' not found in input data")

    _ensure_output_dir(output_dir)
    written_paths: List[Path] = []

    for seg in segments:
        seg_df = df[df[segment_col] == seg]
        if seg_df.empty:
            # skip empty segment but continue others
            continue
        iv_result = calculate_iv(
            df=seg_df,
            label_col=label_col,
            feature_cols=feature_cols,
            binning_method=binning_method,
            n_bins=n_bins,
            min_leaf_frac=min_leaf_frac,
            positive_label=positive_label,
            return_type="feature",
        )
        per_feature = iv_result.get("per_feature")
        if per_feature is None:
            continue
        out_path = output_dir / f"{seg}_features_IV.csv"
        per_feature.to_csv(out_path, header=["IV"])
        written_paths.append(out_path)

    return written_paths


@tool
def run_iv_from_file_tool(
    input_path: str,
    label_col: str,
    segment_col: str = "segment",
    segments: Optional[Iterable[str]] = None,
    feature_cols: Optional[List[str]] = None,
    binning_method: str = "quantile",
    n_bins: int = 10,
    min_leaf_frac: float = 0.05,
    positive_label=1,
    output_dir: str = "output",
) -> str:
    """Calculate IV per segment from a CSV/Parquet and write per-feature IV CSVs.

    Returns a JSON string with written file paths.
    """
    segs: Sequence[str]
    if segments is None:
        segs = ["MTB", "YNTB"]
    else:
        segs = list(segments)

    paths = run_iv_by_segments(
        input_path=Path(input_path),
        label_col=label_col,
        segment_col=segment_col,
        segments=segs,
        feature_cols=feature_cols,
        binning_method=binning_method,
        n_bins=n_bins,
        min_leaf_frac=min_leaf_frac,
        positive_label=positive_label,
        output_dir=Path(output_dir),
    )
    return json.dumps({"written_files": [str(p) for p in paths]})
