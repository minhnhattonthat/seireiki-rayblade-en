import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import arc  # noqa: E402
import lz  # noqa: E402

TREE = ROOT / "work/disc/tree"


def test_lz_roundtrip_synthetic():
    data = bytes(range(256)) * 3 + b"\x00" * 700 + b"abcabcabcabd" * 50 + bytes([7, 7, 7, 1, 2]) * 33
    assert lz.unpack_record(lz.pack_record(data)) == data
    assert lz.unpack_record(lz.pack_record(b"")) == b""


def test_arc_pack_synthetic_with_alias():
    recs = [b"AAAA", b"BBBBBB", b"CC"]
    n = 4
    hdr, body, pos = bytearray(4 * n), bytearray(), 4 * n
    starts = []
    for r in recs:
        starts.append(pos)
        body += r + b"\0" * (-len(r) % 4)
        pos += len(r) + (-len(r) % 4)
    tgt = [starts[0], starts[0], starts[1], starts[2]]  # slot 1 aliases slot 0
    for i, t in enumerate(tgt):
        struct.pack_into("<I", hdr, 4 * i, t - 4 * i)
    data = bytes(hdr + body)
    assert arc.pack(data, {}) == data
    new = arc.pack(data, {2: b"XXXXXXXXXX"})
    s, e = arc.entries(new)[2]
    assert new[s:s + 10] == b"XXXXXXXXXX" and arc.entries(new)[1] == arc.entries(new)[0]


@pytest.mark.skipif(not (TREE / "D_SCE.BIN").exists(), reason="disc not unpacked (dumpsxiso)")
def test_real_archives_pack_identity():
    for name in ("D_SCE", "D_BMESS", "D_SYSTEM"):
        d = (TREE / f"{name}.BIN").read_bytes()
        assert arc.pack(d, {}) == d
