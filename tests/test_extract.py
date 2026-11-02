"""Phase 4 (extract): every extracted string re-encodes to the original bytes, and the text
ranges are fully covered.

The roundtrip runs over script/ (the committed extraction); the coverage test re-discovers every
text block from the original files and fails if one is missing from script/. Both read the pristine
disc tree in work/disc/tree (built by tools/build.py's unpack step), never build/."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import re as re_mod  # noqa: E402
import vm  # noqa: E402

HAVE_TREE = (ROOT / "work/disc/tree/D_SCE.BIN").exists() and (ROOT / "work/disc/tree/SLPS_026.52").exists()
pytestmark = pytest.mark.skipif(not HAVE_TREE, reason="no unpacked disc in work/disc/tree")


def test_script_dir_populated():
    files = list((ROOT / "script/sce").glob("*.json"))
    assert len(files) > 400, f"only {len(files)} scene files"
    for name in ("exe_bank.json", "resident.json", "exe_vm.json"):
        entries = json.loads((ROOT / "script" / name).read_text(encoding="utf-8"))
        assert entries, name


def test_roundtrip():
    """encode(decode(bytes)) == bytes for every extracted string."""
    bad, n = [], 0
    for p, entries in extract.all_entries():
        for e in entries:
            n += 1
            raw = extract.T.encode(e["jp"])
            orig = extract.source_bytes(e)
            if raw != orig:
                bad.append((p.name, e["id"]))
    assert n > 50000, n
    assert not bad, f"{len(bad)} strings do not roundtrip, e.g. {bad[:5]}"


def test_coverage_sce():
    """Every text block the decoder finds in D_SCE is in script/sce (no unexplained gaps)."""
    have = set()
    for p in (ROOT / "script/sce").glob("*.json"):
        have.update(e["id"] for e in json.loads(p.read_text(encoding="utf-8")))
    missing = []
    for slot, rec in vm.sce_records():
        texts, _ = extract.sweep_texts(rec)
        for op, a, b in texts:
            eid = f"sce{slot:03d}:{op:05X}"
            if eid not in have:
                missing.append(eid)
    assert not missing, f"{len(missing)} text blocks not extracted, e.g. {missing[:5]}"


def test_coverage_bank():
    """Every bank string the reader can reach is extracted (ids are group:index)."""
    have = {e["id"] for e in json.loads((ROOT / "script/exe_bank.json").read_text(encoding="utf-8"))}
    bank, _ = extract.bank_entries()
    missing = [e["id"] for e in bank if e["id"] not in have and extract.plausible(e["jp"])]
    assert not missing, f"{len(missing)} bank strings not extracted, e.g. {missing[:5]}"


def test_table_covers_font():
    """tbl/jp.tbl must decode every glyph cell (0x00-0xA4C): a missing code shifts the text."""
    missing = [c for c in range(0xA4D) if not any(len(k) == (1 if c < 0xF0 else 2) and
                                                 extract.T.dec.get(k) for k in
                                                 ([bytes([c])] if c < 0xF0 else [bytes([0xEF + (c >> 8), c & 0xFF])]))]
    assert not missing, f"{len(missing)} glyph codes missing from tbl/jp.tbl, e.g. {missing[:5]}"


def test_len_table_matches_exe():
    """vm.LEN is the interpreter's own length table (RAM 0x800C8480)."""
    exe = (ROOT / "work/disc/tree/SLPS_026.52").read_bytes()
    off = 0x800C8480 - 0x80010000 + 0x800
    assert vm.LEN == exe[off:off + 256], "vm.LEN differs from the EXE table"


def test_text_end_skips_glyph_low_bytes():
    """A 0xFF that is the low byte of a glyph (F0..FA xx) does not end the text."""
    raw = bytes.fromhex("F3FF") + b"\xe6\xff"          # 私 。 then the terminator
    assert vm.text_end(raw, 0) == 3
