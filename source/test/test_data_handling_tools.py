import sys
from pathlib import Path

# Correct the project root path to ensure it points to the workspace root
project_root = Path(__file__).resolve().parents[2]  # Adjusted to point two levels up
sys.path.append(str(project_root))

import pandas as pd
import numpy as np
from source.tools.data_handling import bin_single_feature_tool, calculate_iv_tool

def load_test_data():
    """From specified Parquet file load test data"""
    file_path = "data/input data/base_by_custfac_w_waterfall_bad_20250923_v4.parquet"
    try:
        df = pd.read_parquet(file_path)
        print(f"Successfully loaded test data: {file_path}")
        return df
    except Exception as e:
        print(f"Failed to load test data: {e}")
        return None

# Test the bin_single_feature_tool
def test_bin_single_feature_tool():
    """Test the bin_single_feature_tool."""
    df = load_test_data()
    if df is not None:
        series = df.iloc[:, 0]  # Use the first column as test data
        result = bin_single_feature_tool.invoke({
            "series": series,
            "method": "quantile",
            "n_bins": 4
        })
        print("Test bin_single_feature_tool:")
        print(result)

# Test the calculate_iv_tool
def test_calculate_iv_tool():
    """Test the calculate_iv_tool."""
    df = load_test_data()
    if df is not None:
        label_col = df.columns[-1]  # Use the last column as the label column
        feature_cols = df.columns[:-1]  # Use all columns except the last one as feature columns
        result = calculate_iv_tool.invoke({
            "df": df,
            "label_col": label_col,
            "feature_cols": feature_cols,
            "binning_method": "quantile",
            "n_bins": 4,
            "positive_label": 1,
            "return_type": "both"
        })
        print("Test calculate_iv_tool:")
        print("Per Bin IV:")
        print(result["per_bin"])
        print("Per Feature IV:")
        print(result["per_feature"])

if __name__ == "__main__":
    test_bin_single_feature_tool()
    test_calculate_iv_tool()