"""Locate the vmax envelope of the gas-rich starless RELHIC cell in TNG50-1 at z=0.

Why: the project's Cloud-9 anchor is M200 = 5e9 Msun with Vmax = 31.12 km/s. Counting queries
showed the mass 4-6e9 Msun / starless / gas>=1.476e5 Msun cell returns 22 objects for
vmax in [28,34) but 0 for vmax in [30,35). That is contradictory unless the boundary sits
between 28 and 30. This script walks the boundary and then reads back the three highest-vmax
members of the cell to confirm the envelope from the detail records themselves.
"""
# CG-16: every host-dependent path is resolved by scripts/paths.py (single source).
import sys as _sys, pathlib as _pathlib
_CG16_ROOT = next(a for a in _pathlib.Path(__file__).resolve().parents
                  if (a / "scripts" / "paths.py").exists())
_sys.path.insert(0, str(_CG16_ROOT / "scripts"))
from paths import SCRATCH_DIR, TNG_KEY_FILE  # noqa: E402
import gzip, json, time, urllib.request

KEY = open(TNG_KEY_FILE).read().strip()
BASE = ("primary_flag=1&len_stars__lt=1&mass__gt=2.7080e-1&mass__lt=4.0620e-1"
        "&mass_gas__gt=1e-5&len_dm__gt=100")
UNIT = 1e10 / 0.6774


def api(path, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request("https://www.tng-project.org/api/" + path,
                                         headers={"api-key": KEY})
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
            if raw[:2] == b"\x1f\x8b":
                raw = gzip.decompress(raw)
            return json.loads(raw)
        except Exception as exc:
            print(f"  retry {i+1}: {exc!r}", flush=True)
            time.sleep(15 * (i + 1))
    return None


out = {"ladder": [], "envelope": []}
for vlo, vhi in ((28, 29), (29, 30), (30, 31), (31, 34), (29.5, 30.0), (29.9, 30.1)):
    res = api(f"TNG50-1/snapshots/99/subhalos/?{BASE}&vmax__gt={vlo}&vmax__lt={vhi}&count=1")
    out["ladder"].append({"vmax": [vlo, vhi], "count": res and res.get("count")})
    print(f"vmax {vlo}-{vhi}: count={res and res.get('count')}", flush=True)
    time.sleep(8)

res = api(f"TNG50-1/snapshots/99/subhalos/?{BASE}&order=vmax&sorting=desc&count=3")
ids = [r["id"] for r in (res.get("results") or [])] if res else []
print("top-vmax members of the cell:", ids, flush=True)
for sid in ids:
    time.sleep(8)
    d = api(f"TNG50-1/snapshots/99/subhalos/{sid}/")
    if d:
        row = {"id": sid, "vmax": d.get("vmax"), "mass_msun": d.get("mass") * UNIT,
               "gas_msun": (d.get("mass_gas") or 0) * UNIT, "len_stars": d.get("len_stars"),
               "len_dm": d.get("len_dm"), "halfmassrad_dm_kpc": d.get("halfmassrad_dm")}
        out["envelope"].append(row)
        print("  ", row, flush=True)

open(str(SCRATCH_DIR / "tng_vmax_envelope.json"), "w",
     encoding="utf-8").write(json.dumps(out, indent=1))
print("DONE", flush=True)
