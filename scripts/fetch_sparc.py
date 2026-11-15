"""Download SPARC database from astroweb.cwru.edu/SPARC.

Downloads:
  - Table1.mrt (galaxy sample with Vflat)
  - Rotmod_LTG.zip (175 rotation curve files)
  - MassModels.mrt (baryonic mass models)

These files are gitignored by design — external data should be re-fetched
by users rather than committed to the repo.

After download, run:
  python code/phase33d_real_sparc_probe.py
"""
import urllib.request
import zipfile
import os
import sys
from pathlib import Path

SPARC_URLS = {
    "Table1.mrt":     "https://astroweb.cwru.edu/SPARC/SPARC_Lelli2016c.mrt",
    "Rotmod_LTG.zip": "https://astroweb.cwru.edu/SPARC/Rotmod_LTG.zip",
    "MassModels.mrt": "https://astroweb.cwru.edu/SPARC/MassModels_Lelli2016c.mrt",
}

# Target depends on where this fetcher is invoked from. The copy under
# v0.3-prelim/data/external/sparc/ keeps the historical relative target; the TRACKED copy in
# scripts/ (F39: a fetcher inside a gitignored directory is invisible to a fresh clone) must
# write into v0.3-prelim/data/external/sparc, not into a new data/ at the repository root.
_HERE = Path(__file__).resolve().parent
if _HERE.name == "scripts":
    TARGET_DIR = _HERE.parent / "v0.3-prelim" / "data" / "external" / "sparc"
else:
    TARGET_DIR = _HERE.parent / "data" / "external" / "sparc"
if len(sys.argv) > 1:
    TARGET_DIR = Path(sys.argv[1])


def main():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    for filename, url in SPARC_URLS.items():
        target_path = TARGET_DIR / filename
        if target_path.exists():
            print(f"Already exists: {filename}")
            continue
        print(f"Downloading {filename} from {url}...")
        urllib.request.urlretrieve(url, target_path)
        size_kb = target_path.stat().st_size / 1024
        print(f"  Downloaded: {size_kb:.1f} KB")

    # Extract Rotmod_LTG.zip
    zip_path = TARGET_DIR / "Rotmod_LTG.zip"
    extract_dir = TARGET_DIR / "Rotmod_LTG"
    if not extract_dir.exists():
        print(f"\nExtracting {zip_path} to {extract_dir}...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_dir)
        n_files = len(list(extract_dir.glob("*")))
        print(f"  Extracted {n_files} files")

    print("\nSPARC data ready.")
    print("Run: python code/phase33d_real_sparc_probe.py")


if __name__ == "__main__":
    main()