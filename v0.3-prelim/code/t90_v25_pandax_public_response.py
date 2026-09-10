"""T90.25 public PandaX response extraction and validated efficiency fold."""
from __future__ import annotations

import json
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = _PROJECT_ROOT / "data" / "external_data" / "pandax_4t" / "response"
OUTPUT_DIR = _PROJECT_ROOT / "outputs" / "t90"
EFF_URL = "https://static.pandax.sjtu.edu.cn/download/data-share/p4-first-analysis/eff_RDQ_graph.root"
XLSX_URL = "https://static.pandax.sjtu.edu.cn/download/data-share/p4-first-analysis/PandaX4T_Data_ne.xlsx"


def _download(url: str, path: Path) -> None:
    if path.exists() and path.stat().st_size > 0:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "sidm-t90/0.4"})
    with urllib.request.urlopen(req, timeout=60) as response:
        path.write_bytes(response.read())


def ensure_public_files() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = {"efficiency_root": DATA_DIR / "eff_RDQ_graph.root", "data_xlsx": DATA_DIR / "PandaX4T_Data_ne.xlsx"}
    for key, url in (("efficiency_root", EFF_URL), ("data_xlsx", XLSX_URL)):
        _download(url, files[key])
    return files


def extract_xlsx_data() -> dict:
    files = ensure_public_files()
    with zipfile.ZipFile(files["data_xlsx"]) as archive:
        ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        shared = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        strings = ["".join(t.text or "" for t in si.findall(".//m:t", ns)) for si in shared.findall("m:si", ns)]
        sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.findall(".//m:sheetData/m:row", ns):
            vals = []
            for cell in row.findall("m:c", ns):
                value = cell.find("m:v", ns)
                if value is None:
                    vals.append("")
                elif cell.get("t") == "s":
                    vals.append(strings[int(value.text)])
                else:
                    vals.append(value.text)
            rows.append(vals)
    return {"source": str(files["data_xlsx"]), "headers": rows[0], "n_rows": len(rows) - 1, "first_row": rows[1], "last_row": rows[-1]}


def extract_root_keys() -> dict:
    files = ensure_public_files()
    raw = files["efficiency_root"].read_bytes()
    tokens = sorted({x.decode("ascii", "ignore") for x in __import__("re").findall(rb"[A-Za-z_][A-Za-z0-9_]{3,}", raw)})
    keys = [x for x in tokens if any(k in x.lower() for k in ("eff", "graph", "rdq"))]
    return {"source": str(files["efficiency_root"]), "file_size_bytes": len(raw), "root_header": raw[:4] == b"root", "keys": keys}


def load_efficiency_graph() -> dict:
    """Read the public ROOT TGraphs through uproot and return all points."""
    files = ensure_public_files()
    try:
        import uproot
    except ImportError as exc:
        raise RuntimeError("uproot is required to read the public ROOT efficiency graph") from exc
    with uproot.open(files["efficiency_root"]) as root_file:
        graph = root_file["eff_nr"]
        x, y = graph.values()
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) == 0 or len(x) != len(y) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Invalid public PandaX efficiency graph")
    if np.any(y < 0.0) or np.any(y > 1.0):
        raise ValueError("Public PandaX efficiency is outside [0,1]")
    return {
        "source": str(files["efficiency_root"]),
        "source_url": EFF_URL,
        "graph_name": "eff_nr",
        "n_points": int(len(x)),
        "x_units": "keVnr",
        "x_values": x.tolist(),
        "y_values": y.tolist(),
        "x_min": float(x.min()), "x_max": float(x.max()),
        "y_min": float(y.min()), "y_max": float(y.max()),
    }


def build_efficiency_proxy() -> dict:
    """Build a compact interpolation from the extracted public graph."""
    graph = load_efficiency_graph()
    x = np.asarray(graph["x_values"], dtype=float)
    y = np.asarray(graph["y_values"], dtype=float)
    # Pointwise min/max envelopes use the public graph's actual values.
    sample_x = np.array([3.0, 5.0, 10.0, 20.0, 50.0, 100.0])
    sample_y = np.interp(sample_x, x, y)
    return {
        "source": "PandaX public eff_RDQ_graph.root: eff_nr",
        "source_url": EFF_URL,
        "exact_graph_points_loaded": True,
        "x_units": "keVnr",
        "x_values": sample_x.tolist(),
        "y_values": sample_y.tolist(),
        "full_graph": graph,
    }


def main() -> dict:
    files = ensure_public_files()
    output = {
        "analysis": "T90.25 PandaX public response acquisition",
        "files": {k: {"path": str(v), "bytes": v.stat().st_size} for k, v in files.items()},
        "xlsx": extract_xlsx_data(),
        "root": extract_root_keys(),
        "efficiency_graph": load_efficiency_graph(),
        "limitations": [
            "This is the public first-analysis total NR efficiency graph, not the full Run0+Run1 multidimensional S1/S2 response.",
            "The public candidate CSV contains selected events; it cannot independently reconstruct rejected-event efficiency.",
        ],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "t90_v25_pandax_public_response.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"output": str(path), "root_bytes": files["efficiency_root"].stat().st_size, "xlsx_bytes": files["data_xlsx"].stat().st_size, "xlsx_rows": output["xlsx"]["n_rows"], "graph": output["efficiency_graph"]["graph_name"], "graph_points": output["efficiency_graph"]["n_points"]}, indent=2))
    return output


if __name__ == "__main__":
    main()
