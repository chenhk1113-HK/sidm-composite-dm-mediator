"""
Polls the T38c background run: read /tmp/kiss_sidm_output/ and report.
"""
import json
import time
from pathlib import Path


def main():
    output_dir = Path("/tmp/kiss_sidm_output")
    snapshots = sorted(output_dir.glob("snap_*.jld2")) if output_dir.exists() else []
    result_path = Path("/tmp/kiss_result.json")

    out = {
        "t38c_status": {
            "snapshots_so_far": len(snapshots),
            "snapshots_target": 10,
            "snapshots_list": [s.name for s in snapshots],
            "snapshot_size_bytes": [s.stat().st_size for s in snapshots],
            "result_json_present": result_path.exists(),
            "poll_unix_seconds": int(time.time()),
        }
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()