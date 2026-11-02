import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "work/disc/tree/SLPS_026.52"


def test_scene_list_well_formed():
    with open(ROOT / "tools/debug/scenes.tsv", encoding="utf-8") as f:
        rows = list(csv.DictReader((ln for ln in f if not ln.startswith("#")), delimiter="\t"))
    assert len(rows) > 50
    assert len({r["name"] for r in rows}) == len(rows)
    for r in rows:
        assert None not in r and None not in r.values(), r["name"]
        if r["scene"].startswith("c"):  # cNN[+HEX]: New Game calls resident sub NN (warp.py)
            sub, _, entry = r["scene"][1:].partition("+")
            entry, _, delay = entry.partition("@")
            assert 0 <= int(sub) < 70 and (not entry or int(entry, 16) >= 0) and (not delay or int(delay) >= 0)
        else:
            assert -1 <= int(r["scene"]) < 448
        if r["stop_op"]:
            op, _, arg = r["stop_op"].partition("/")
            assert 0 <= int(op, 16) < 256 and (not arg or 0 <= int(arg, 16) < 256)
        for step in r["route"].lstrip("!").split(";"):
            if step.strip():
                n, keys = step.split()
                assert int(n) > 0 and keys


@pytest.mark.skipif(not EXE.exists(), reason="unpacked disc not present (work/disc/tree)")
def test_warp_patch_site():
    # warp.lua rewrites the New Game `0B 01 00` (goto scene 1) at RAM 0x80010620; EXE file = RAM - 0x80010000 + 0x800
    assert EXE.read_bytes()[0x10620 - 0x10000 + 0x800:][:3] == b"\x0b\x01\x00"
