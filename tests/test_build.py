"""Identity build (phase 3): unpack + repack with no edits gives the original disc, byte for byte.
Builds its own disc into work/test_build (never reads build/): a stale artifact can't pass."""
import hashlib
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

pytestmark = pytest.mark.skipif(not build.CUE.exists() or not build.MK.exists(),
                                reason="no dump in rom/ or no mkpsxiso in tools/")


def sha1(p):
    with open(p, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


def test_identity_build():
    out = ROOT / "work/test_build"
    shutil.rmtree(out, ignore_errors=True)
    try:
        cue, t1, t2 = build.build(out, "ident", identity=True)
        want = [ln.split()[0] for ln in (ROOT / "rom.sha1").read_text().splitlines() if ln and ln[0] != "#"]
        assert sha1(t1) == want[0], "track 1 differs from the original"
        assert sha1(t2) == want[1], "track 2 differs from the original"
        assert "TRACK 02 AUDIO" in cue.read_text()
    finally:
        shutil.rmtree(out, ignore_errors=True)
