"""patch.py / insert.py / font_en.py: the record rewriter, the encoder and the added font cells."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font_en  # noqa: E402
import insert  # noqa: E402
import patch  # noqa: E402
import vm  # noqa: E402
from tbl import Table  # noqa: E402

TREE = ROOT / "work/disc/tree"
needs_disc = pytest.mark.skipif(not (TREE / "D_SCE.BIN").exists(), reason="disc not unpacked")


def records():
    return dict(vm.sce_records())


@needs_disc
def test_identity_rebuild():
    """Rebuilding a record with no edits gives back the original bytes: the partition loses nothing."""
    recs = records()
    for slot in sorted(recs)[:40] + [208, 347, 447]:
        rec = recs[slot]
        new, mp = patch.rebuild(rec, {})
        assert new == rec, f"slot {slot} rebuilt with changes"
        assert mp[0] == 0 and mp[len(rec)] == len(rec)


@needs_disc
def test_grow_preserves_control_flow():
    """A longer text block shifts everything after it; every branch still lands on the same instruction."""
    rec = records()[1]
    ins, _ = patch.decode(rec)
    texts = [it for it in ins if it.kind == "text"]
    grows = {it.off: b"X" * 60 for it in texts}
    new, mp = patch.rebuild(rec, grows)
    patch.verify(rec, new, mp)
    assert len(new) > len(rec)
    assert b"X" * 60 in new


@needs_disc
def test_text_block_is_where_the_script_says():
    """Every script entry's `off` is a text op in the record (or the build must refuse to edit it)."""
    import json
    recs = records()
    for p in sorted((ROOT / "script/sce").glob("*.json"))[:8]:
        slot = int(p.stem)
        ins, _ = patch.decode(recs[slot])
        by = {it.off: it for it in ins}
        for e in json.loads(p.read_text(encoding="utf-8")):
            assert by.get(e["off"]) is not None and by[e["off"]].kind == "text", (slot, e["id"])


def test_marker_text_fills_one_line():
    for off in (0x0F8, 0x12345):
        t = insert.marker_text(off, 30)
        assert len(t) == 30
        assert t.startswith(f"[{off:05X}]")


def test_en_table_roundtrip():
    t = Table.load(ROOT / "tbl/en.tbl")
    line = "The quick brown fox jumps!?,.:;'\"-()[]&*<>#$@_`{}|\\^ 0123456789"
    raw = t.encode(line)
    assert t.decode(raw, 0, len(raw))[0] == line
    assert all(len(c.strip()) == 0 or len(t.encode(c)) >= 1 for c in line)


@needs_disc
def test_font_cells_are_blank_in_the_original():
    """Added glyphs go into cells the Japanese font leaves empty; a non-blank cell means a clash."""
    font_en.check()
    exe = (TREE / "SLPS_026.52").read_bytes()
    for code in font_en.GLYPHS:
        cell = exe[0xA03CC + code * 16:0xA03CC + code * 16 + 16]
        assert not any(cell), f"cell {code:03X} is not blank in the original font"


def test_canary_needs_no_missing_glyph():
    for ch in font_en.CANARY:
        assert ch in font_en.GLYPHS.values() or ch in font_en.EXISTING or ch in font_en.LATIN, ch
