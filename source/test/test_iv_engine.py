from pathlib import Path

import pandas as pd
import pytest

from source.tools.iv_engine import run_iv_by_segments


@pytest.fixture()
def sample_df():
    return pd.DataFrame(
        {
            "feature1": [1, 2, 3, 4, 5, 6],
            "feature2": [10, 9, 8, 7, 6, 5],
            "label": [1, 0, 1, 0, 1, 0],
            "segment": ["MTB", "MTB", "YNTB", "YNTB", "MTB", "YNTB"],
        }
    )


def test_run_iv_by_segments_creates_outputs(tmp_path: Path, sample_df: pd.DataFrame):
    out_dir = tmp_path / "test_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    data_path = out_dir / "test_data.csv"
    sample_df.to_csv(data_path, index=False)
    print(f"[test] wrote test data -> {data_path}")

    written = run_iv_by_segments(
        input_path=data_path,
        label_col="label",
        segment_col="segment",
        segments=["MTB", "YNTB"],
        output_dir=out_dir,
        n_bins=3,
    )

    print(f"[test] IV files generated: {written}")
    assert len(written) == 2
    for path in written:
        assert path.exists()
        loaded = pd.read_csv(path)
        print(f"[test] preview {path.name}:\n{loaded.head()}\n")
        assert not loaded.empty
    

# run with below:
# python -m pytest source/test/test_iv_engine.py -s