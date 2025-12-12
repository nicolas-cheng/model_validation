# Test cases for generate_iv_report_tool in iv_report.py
# These tests verify the markdown IV report generation logic for different scenarios.

import os
import shutil
import pandas as pd
from pathlib import Path
from iv_report import MATPLOTLIB_AVAILABLE, generate_iv_markdown


# Helper function to create dummy IV CSV files for each segment
def setup_test_data(output_dir, segments):
    os.makedirs(output_dir, exist_ok=True)
    for seg in segments:
        # Create a simple IV table with three features
        df = pd.DataFrame({"IV": [0.5, 0.3, 0.1]}, index=[f"feature_{i+1}" for i in range(3)])
        df.to_csv(Path(output_dir) / f"{seg}_features_IV.csv", header=False)


# Helper function to remove test output directory after test
def cleanup_test_data(output_dir):
    shutil.rmtree(output_dir, ignore_errors=True)


# Test: Basic case with two segments, both have IV CSVs
def test_generate_iv_report_tool_basic():
    output_dir = Path("data") / "test_output"
    print(output_dir)

    # 
    segments = ["MTB", "YNTB"]
    setup_test_data(output_dir, segments)
    # Generate the markdown report using the underlying function
    report_path = generate_iv_markdown(output_dir=output_dir, segments=segments, report_name="test_report.md")
    report_path = str(report_path)
    assert os.path.exists(report_path), f"Report file not found: {report_path}"
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Check report header and segment sections
        assert "# Information Value Report" in content
        for seg in segments:
            assert f"## Segment: {seg}" in content
            assert "feature_1" in content  # At least one feature should appear
    cleanup_test_data(output_dir)


# Test: One segment is missing its IV CSV, should report missing data
def test_generate_iv_report_tool_missing_segment():
    output_dir = Path("data") / "test_output_missing"
    print(output_dir)
    
    segments = ["MTB", "MISSING_SEG"]
    setup_test_data(output_dir, ["MTB"])  # Only create MTB
    report_path = generate_iv_markdown(output_dir=output_dir, segments=segments, report_name="test_report_missing.md")

    # 
    report_path = str(report_path)
    print(report_path)

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        # Should mention missing data for the missing segment
        assert "No IV data found" in content
    cleanup_test_data(output_dir)


# Test: Chart generation when matplotlib is available
def test_generate_iv_report_tool_charts():
    output_dir = "test_output_charts"
    segments = ["MTB"]
    setup_test_data(output_dir, segments)
    report_path = generate_iv_markdown(output_dir=output_dir, segments=segments, report_name="test_report_charts.md")
    report_path = str(report_path)
    chart_path = Path(output_dir) / f"{segments[0]}_iv_top.png"
    if MATPLOTLIB_AVAILABLE:
        assert chart_path.exists(), "Chart PNG should be generated when matplotlib is available"
    else:
        # If matplotlib is absent, the report should still be generated
        assert os.path.exists(report_path)
    cleanup_test_data(output_dir)


# Run tests if this script is executed directly
if __name__ == "__main__":
    test_generate_iv_report_tool_basic()
    test_generate_iv_report_tool_missing_segment()
    print("All tests passed.")