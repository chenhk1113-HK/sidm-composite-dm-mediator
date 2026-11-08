"""CG-16 helper for test_paths_module_honours_env_override (not a test itself).

Prints the repository root that scripts/paths.py resolves under the current environment, so the
test can prove that DM_SIDM_PROJECT_ROOT redirects every derived path without editing any file.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import paths  # noqa: E402

print(paths.REPO)
