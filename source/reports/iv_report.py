"""Lightweight IV report generator.

Reads per-segment IV CSVs and produces a markdown summary report.
Designed as a placeholder until chart rendering is added.
"""
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
from langchain.tools import tool


DEFAULT_SEGMENTS = ("MTB", "YNTB")


def _load_iv_table(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path, index_col=0, header=None, names=["IV"])
    except Exception:
        return None


def generate_iv_markdown(
    output_dir: Path = Path("output"),
    segments: Iterable[str] = DEFAULT_SEGMENTS,
    report_name: str = "report.md",
) -> Path:
    """Build a markdown summary referencing per-segment IV CSVs."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: List[str] = ["# Information Value Report", ""]

    for seg in segments:
        csv_path = output_dir / f"{seg}_features_IV.csv"
        df = _load_iv_table(csv_path)
        rows.append(f"## Segment: {seg}")
        if df is None or df.empty:
            rows.append(f"- No IV data found at `{csv_path}`")
            rows.append("")
            continue
        rows.append(f"Source: `{csv_path}`")
        rows.append("")
        # Top features preview
        preview = df.sort_values("IV", ascending=False).head(10)
        rows.append("Top IV features (up to 10):")
        for feature, iv in preview["IV"].items():
            rows.append(f"- {feature}: {iv:.4f}")
        rows.append("")

    report_path = output_dir / report_name
    report_path.write_text("\n".join(rows), encoding="utf-8")
    return report_path


@tool
def generate_iv_report_tool(
    output_dir: str = "output",
    segments: Optional[Iterable[str]] = None,
    report_name: str = "report.md",
) -> str:
    """Generate a markdown IV report summarizing per-segment IV CSVs."""
    segs = tuple(segments) if segments else DEFAULT_SEGMENTS
    path = generate_iv_markdown(output_dir=Path(output_dir), segments=segs, report_name=report_name)
    return str(path)
