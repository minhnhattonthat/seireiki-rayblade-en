"""ROM-level gate (phase 7): every byte the English build changes in the EXE is covered by a logged write whose
expected original bytes match the clean EXE, no two writes overlap and none was overwritten later (romdiff.py)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import insert  # noqa: E402
import romdiff  # noqa: E402

TREE = ROOT / "work/disc/tree"
needs_disc = pytest.mark.skipif(not (TREE / "D_SCE.BIN").exists(), reason="disc not unpacked")


def parse(log):
    out = []
    for line in log:
        off, old, new, by = line.split(None, 3)
        out.append((int(off, 16), bytes.fromhex(old), bytes.fromhex(new), by))
    return out


@needs_disc
def test_exe_writes_cover_every_change():
    files, log = insert.changes()
    orig = (TREE / insert.EXE_NAME).read_bytes()
    new = files[insert.EXE_NAME]
    # the EXE grows (relocated bank, VWF hook) and the growth is zero-filled, which the write log records as the
    # "original" bytes: compare against the original padded the same way
    errs, ok = romdiff.check(orig + bytes(len(new) - len(orig)), new, set(), parse(log))
    assert errs == [], errs[:10]
    assert ok > 0
