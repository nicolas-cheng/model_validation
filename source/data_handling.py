import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from sklearn.tree import DecisionTreeClassifier
from langchain.tools import tool

# ============== 1. Binning helper =====================
def bin_single_feature_tool(
    series: pd.Series,
    y: Optional[pd.Series] = None,
    method: str = "quantile",   # 'quantile' | 'width' | 'tree'
    n_bins: int = 10,
    min_leaf_frac: float = 0.05,
) -> pd.Series:
    """
    Bin a single numeric feature according to the specified method.

    Parameters
    ----------
    series : pd.Series
        Raw feature values.
    y : pd.Series, optional
        Target labels (only needed when method='tree').
    method : str
        'quantile' (equal frequency), 'width' (equal width),
        or 'tree' (decision-tree-based optimal binning).
    n_bins : int
        Number of bins or max leaf nodes (for tree).
    min_leaf_frac : float
        Minimum fraction of samples per leaf for tree binning.

    Returns
    -------
    pd.Series
        Series of bin labels (string), same index as input series.
        Missing values are grouped into 'MISSING'.
    """
    # convert to numeric, coerce invalid to NaN
    s = pd.to_numeric(series, errors="coerce")
    bins = pd.Series(index=s.index, dtype="object")

    # handle missing values as a separate bin
    missing_mask = s.isna()

    # ================== quantile / width ==================
    if method in ("quantile", "width"):
        valid_mask = ~missing_mask
        if valid_mask.sum() == 0:
            # all values are missing
            bins[missing_mask] = "MISSING"
            return bins

        s_valid = s[valid_mask]

        try:
            if method == "quantile":
                # equal frequency binning
                binned = pd.qcut(s_valid, q=n_bins, duplicates="drop")
            else:
                # equal width binning
                binned = pd.cut(s_valid, bins=n_bins, duplicates="drop")
        except ValueError:
            # e.g. all values are identical
            binned = pd.Series(["ALL"] * valid_mask.sum(), index=s_valid.index)

        bins[valid_mask] = binned.astype(str)
        bins[missing_mask] = "MISSING"
        return bins

    # ================== tree-based binning ==================
    elif method == "tree":
        if y is None:
            raise ValueError("y must be provided when method='tree'.")

        valid_mask = ~missing_mask
        if valid_mask.sum() == 0:
            bins[missing_mask] = "MISSING"
            return bins

        X = s[valid_mask].values.reshape(-1, 1)
        y_vec = np.array(y)[valid_mask]

        # ensure minimum samples per leaf
        min_samples_leaf = max(int(len(X) * min_leaf_frac), 1)

        clf = DecisionTreeClassifier(
            max_leaf_nodes=n_bins,
            min_samples_leaf=min_samples_leaf,
        )
        clf.fit(X, y_vec)
        leaf_ids = clf.apply(X)

        leaf_series = pd.Series(leaf_ids, index=s[valid_mask].index)
        bins[valid_mask] = leaf_series.map(lambda v: f"leaf_{int(v)}")
        bins[missing_mask] = "MISSING"
        return bins

    else:
        raise ValueError(f"Unsupported binning method: {method}")


# ============== 2. IV calculator (main) =================
def calculate_iv(
    df: pd.DataFrame,
    label_col: str,
    feature_cols: Optional[List[str]] = None,
    binning_method: str = "quantile",   # 'quantile' | 'width' | 'tree'
    n_bins: int = 10,
    min_leaf_frac: float = 0.05,
    positive_label: Any = 1,
    return_type: str = "both",          # 'bin' | 'feature' | 'both'
) -> Dict[str, Any]:
    """
    Calculate Information Value (IV) for multiple features.

    Parameters
    ----------
    df : pd.DataFrame
        Input data table that contains label and feature columns.
    label_col : str
        Name of the label column.
    feature_cols : list of str, optional
        Feature columns to be evaluated. If None, all columns except label_col are used.
    binning_method : str
        'quantile' (equal frequency), 'width' (equal width),
        or 'tree' (decision-tree-based optimal binning).
    n_bins : int
        Number of bins or max leaf nodes (for tree).
    min_leaf_frac : float
        Minimum fraction of samples per leaf for tree binning.
    positive_label : Any
        The value in label_col that represents the "bad" or "event" class.
    return_type : str
        'bin'      -> return only per-bin IV table;
        'feature'  -> return only per-feature IV summary;
        'both'     -> return both.

    Returns
    -------
    Dict[str, Any]
        keys (depending on return_type):
            - 'per_bin' : pd.DataFrame with index (Feature, Bin) and columns:
                ['count', 'bads', 'goods', 'pct_goods', 'pct_bads',
                 'count_pct', 'bad_rate', 'woe', 'iv']
            - 'per_feature' : pd.Series with overall IV per feature.
    """
    if feature_cols is None:
        feature_cols = [c for c in df.columns if c != label_col]

    # ensure label exists
    if label_col not in df.columns:
        raise ValueError(f"Label column '{label_col}' not found in DataFrame.")

    # binary label: 1 for positive_label, 0 for others
    y = (df[label_col] == positive_label).astype(int)

    all_summary_tables = []

    #  loop over features and bin each one
    for feature in feature_cols:
        if feature not in df.columns:
            raise ValueError(f"Feature column '{feature}' not found in DataFrame.")

        # tree method requires y, others ignore it
        if binning_method == "tree":
            bins = bin_single_feature(
                series=df[feature],
                y=y,
                method=binning_method,
                n_bins=n_bins,
                min_leaf_frac=min_leaf_frac,
            )
        else:
            bins = bin_single_feature(
                series=df[feature],
                method=binning_method,
                n_bins=n_bins,
                min_leaf_frac=min_leaf_frac,
            )

        temp_df = pd.DataFrame({
            "Feature": feature,
            "Bin": bins,
            "Bad": y,
        })

        # group by feature and bin
        summary = temp_df.groupby(["Feature", "Bin"])["Bad"].agg(["count", "sum"])
        summary.rename(columns={"sum": "bads"}, inplace=True)
        all_summary_tables.append(summary)

    if not all_summary_tables:
        raise ValueError("No features to calculate IV.")

    #  concatenate all features' bin summaries
    summary_table = pd.concat(all_summary_tables)
    # index: (Feature, Bin)

    #  calculate global totals
    total_bads = summary_table["bads"].sum()
    total_goods = summary_table["count"].sum() - total_bads

    if total_bads == 0 or total_goods == 0:
        raise ValueError(
            "Cannot compute IV because there are no bad or no good samples "
            "in the dataset."
        )

    #  add good counts
    summary_table["goods"] = summary_table["count"] - summary_table["bads"]

    #  percentage of total goods/bads per bin
    summary_table["pct_goods"] = summary_table["goods"] / total_goods
    summary_table["pct_bads"] = summary_table["bads"] / total_bads

    # avoid zero proportion for log
    eps = 1e-6
    summary_table["pct_goods"] = summary_table["pct_goods"].clip(lower=eps)
    summary_table["pct_bads"] = summary_table["pct_bads"].clip(lower=eps)

    #  within-feature statistics
    summary_table["count_pct"] = (
        summary_table["count"] /
        summary_table.groupby(level=0)["count"].transform("sum")
    )
    summary_table["bad_rate"] = summary_table["bads"] / summary_table["count"]

    # WoE & IV
    summary_table["woe"] = np.log(summary_table["pct_goods"] / summary_table["pct_bads"])
    summary_table["iv"] = (
        (summary_table["pct_goods"] - summary_table["pct_bads"])
        * summary_table["woe"]
    )

    #  per-feature IV (overall)
    iv_per_feature = (
        summary_table
        .groupby(level=0)["iv"]
        .sum()
        .sort_values(ascending=False)
    )

    result: Dict[str, Any] = {}

    if return_type in ("bin", "both"):
        result["per_bin"] = summary_table

    if return_type in ("feature", "both"):
        result["per_feature"] = iv_per_feature

    return result


# ============== 3. Glue: connect inputs -> outputs ==============

# - inputs["data"] : list[dict] 形式的表格数据（每行一个 dict）
# - inputs["label_col"] : str
# - 可选：inputs["feature_cols"] : list[str]
# - 可选：inputs["binning_method"], inputs["n_bins"], inputs["positive_label"], inputs["return_type"]

# 1) build DataFrame from inputs["data"]
data_obj = inputs.get("data")
if isinstance(data_obj, pd.DataFrame):
    df = data_obj.copy()
else:
    # assume list of dicts
    df = pd.DataFrame(data_obj)

label_col = inputs.get("label_col", "label")
feature_cols = inputs.get("feature_cols")   # can be None
binning_method = inputs.get("binning_method", "quantile")  # 'quantile' | 'width' | 'tree'
n_bins = int(inputs.get("n_bins", 10))
min_leaf_frac = float(inputs.get("min_leaf_frac", 0.05))
positive_label = inputs.get("positive_label", 1)
return_type = inputs.get("return_type", "both")  # 'bin' | 'feature' | 'both'

iv_result = calculate_iv(
    df=df,
    label_col=label_col,
    feature_cols=feature_cols,
    binning_method=binning_method,
    n_bins=n_bins,
    min_leaf_frac=min_leaf_frac,
    positive_label=positive_label,
    return_type=return_type,
)

# 将结果转成 JSON 友好的格式（list[dict]）
if "per_feature" in iv_result:
    per_feature_iv = iv_result["per_feature"].reset_index()
    per_feature_iv.columns = ["Feature", "IV"]
    outputs["per_feature_iv"] = per_feature_iv.to_dict(orient="records")

if "per_bin" in iv_result:
    per_bin_iv = iv_result["per_bin"].reset_index()
    # index (Feature, Bin) -> columns Feature, Bin
    outputs["per_bin_iv"] = per_bin_iv.to_dict(orient="records")


if __name__ == "__main__":
    print()