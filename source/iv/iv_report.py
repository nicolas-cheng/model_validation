import sys
from pathlib import Path

# Add project root to sys.path for relative imports if needed
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

"""Lightweight IV report generator.

Reads per-segment IV CSVs and produces a markdown summary report.
Designed as a placeholder until chart rendering is added.
"""
from typing import Iterable, List, Optional

import pandas as pd
from langchain.tools import tool

# Optional dependency for chart generation
try:  # pragma: no cover - environment may lack matplotlib
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover
    plt = None

MATPLOTLIB_AVAILABLE = plt is not None


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
    generate_charts: bool = True,
    top_n: int = 10,
) -> Path:
    """Build a markdown summary referencing per-segment IV CSVs.

    If matplotlib is available and generate_charts is True, a per-segment bar chart
    of the top-N IV features is saved alongside the report and referenced in the
    markdown.
    """
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
        preview = df.sort_values("IV", ascending=False).head(top_n)
        rows.append(f"Top IV features (up to {top_n}):")
        for feature, iv in preview["IV"].items():
            rows.append(f"- {feature}: {iv:.4f}")
        rows.append("")

        # Optional chart generation
        if generate_charts and plt is not None:
            chart_path = output_dir / f"{seg}_iv_top.png"
            try:
                fig, ax = plt.subplots(figsize=(6, 3))
                preview["IV"].plot(kind="bar", ax=ax, color="#4B8BBE")
                ax.set_title(f"Top IV Features - {seg}")
                ax.set_ylabel("IV")
                ax.set_xlabel("Feature")
                fig.tight_layout()
                fig.savefig(chart_path, dpi=150)
                plt.close(fig)
                rows.append(f"![Top IV chart for {seg}]({chart_path.name})")
                rows.append("")
            except Exception:  # pragma: no cover - avoid failing report if plotting fails
                rows.append("- Chart generation failed (skipped).")
                rows.append("")
        elif generate_charts:
            rows.append("- Chart generation skipped (matplotlib not available).")
            rows.append("")

    report_path = output_dir / report_name
    report_path.write_text("\n".join(rows), encoding="utf-8")
    return report_path


@tool
def generate_iv_report_tool(
    output_dir: str = "output",
    segments: Optional[Iterable[str]] = None,
    report_name: str = "report.md",
    generate_charts: bool = True,
    top_n: int = 10,
) -> str:
    """Generate a markdown IV report summarizing per-segment IV CSVs."""
    segs = tuple(segments) if segments else DEFAULT_SEGMENTS
    path = generate_iv_markdown(
        output_dir=Path(output_dir),
        segments=segs,
        report_name=report_name,
        generate_charts=generate_charts,
        top_n=top_n,
    )
    return str(path)
