from pathlib import Path
import sys

# Add the project root to sys.path so `source` imports work when running directly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

import tempfile
import pandas as pd
from fastapi.testclient import TestClient

# Import the FastAPI app
from source import api


# ---------- Pretty print helpers ----------
def _line(title: str = "", char: str = "-") -> str:
    return (char * 8 + f" {title} " + char * 8) if title else char * 24


def _kv(label: str, value) -> str:
    return f"  {label:<18}: {value}"

def _prepare_iv_csv(output_dir: Path, segment: str = "MTB") -> Path:
    """Create a minimal IV CSV for a segment."""
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({"IV": [0.6, 0.4, 0.1]}, index=["f1", "f2", "f3"])
    csv_path = output_dir / f"{segment}_features_IV.csv"
    df.to_csv(csv_path, header=False)
    print(_line("setup"))
    print(_kv("IV CSV", csv_path))
    print(_kv("Segment", segment))
    return csv_path


def test_query_iv_success():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Point the API to the temp output directory
        api.OUTPUT_DIR = tmp_path
        print(_line("test_success"))
        print(_kv("OUTPUT_DIR", tmp_path))
        csv_path = _prepare_iv_csv(tmp_path, segment="MTB")
        # Create a dummy report file
        report_path = tmp_path / "report.md"
        report_path.write_text("dummy report", encoding="utf-8")
        print(_kv("Report", report_path))

        client = TestClient(api.app)
        resp = client.post("/query_iv", params={"segment": "MTB", "top_n": 2})

        print(_kv("Response status", resp.status_code))
        print(_kv("Response JSON", resp.json()))
        assert resp.status_code == 200
        data = resp.json()
        assert data["segment"] == "MTB"
        assert data["top_n"] == 2
        assert data["source"] == str(csv_path)
        assert data["report"] == str(report_path)
        top_feats = data.get("top_features", [])
        print(_kv("Top features", top_feats))
        assert len(top_feats) == 2
        assert top_feats[0]["feature"] == "f1"
        assert top_feats[0]["IV"] == 0.6


def test_query_iv_missing_file():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        api.OUTPUT_DIR = tmp_path
        print(_line("test_missing"))
        print(_kv("OUTPUT_DIR", f"{tmp_path} (no IV files)"))
        client = TestClient(api.app)
        resp = client.post("/query_iv", params={"segment": "MTB", "top_n": 3})

        print(_kv("Response status", resp.status_code))
        print(_kv("Response JSON", resp.json()))
        assert resp.status_code == 404
        body = resp.json()
        assert "IV file not found" in body.get("detail", "")


def test_query_iv_invalid_top_n():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        api.OUTPUT_DIR = tmp_path
        print(_line("test_invalid_top_n"))
        print(_kv("OUTPUT_DIR", tmp_path))
        _prepare_iv_csv(tmp_path, segment="MTB")
        client = TestClient(api.app)
        resp = client.post("/query_iv", params={"segment": "MTB", "top_n": 0})

        print(_kv("Response status", resp.status_code))
        print(_kv("Response JSON", resp.json()))
        assert resp.status_code == 400
        body = resp.json()
        assert "top_n must be positive" in body.get("detail", "")


def main():
    print(_line("MAIN START", "="))
    print("[main] Running test_query_iv_success...")
    test_query_iv_success()
    print(_line())
    print("[main] Running test_query_iv_missing_file...")
    test_query_iv_missing_file()
    print(_line())
    print("[main] Running test_query_iv_invalid_top_n...")
    test_query_iv_invalid_top_n()
    print(_line("MAIN END", "="))
    print("[main] All tests completed.")


if __name__ == "__main__":
    main()
