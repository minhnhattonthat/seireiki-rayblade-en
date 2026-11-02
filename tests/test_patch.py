"""patch.py / insert.py / font_en.py: the record rewriter, the encoder and the added font cells."""
import sys
from pathlib import Path

import capstone
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
def test_subop_branch_is_rewritten():
    """`5C 14 <8 args> <s16>` (slot 45 @25BD, the S31 hang) is a 12-byte conditional branch: its operand at +10
    must follow the text growth, and no bogus op inside its arguments may be rewritten."""
    rec = records()[45]
    ins, _ = patch.decode(rec)
    by = {it.off: it for it in ins}
    assert by[0x25BD].ln == 12 and by[0x25C9].kind == "text"
    texts = [it.off for it in ins if it.kind == "text" and it.off < 0x25BD]
    new, mp = patch.rebuild(rec, {t: b"\x01" * 80 for t in texts})
    patch.verify(rec, new, mp)
    o = mp[0x25BD]
    assert new[o + 2:o + 10] == rec[0x25BF:0x25C7]                      # the args are untouched
    assert o + vm.s16(new[o + 10], new[o + 11]) + 10 == mp[0x25BD + vm.s16(rec[0x25C7], rec[0x25C8]) + 10]


@needs_disc
def test_trailing_tables_and_switch():
    """`17 a b c <s16>` is 6 bytes (slot 58: the text after it was hidden), `B9 <s16>.. FF FF` (slot 102 @49D)
    is a switch table; both kinds of entries are self-relative and follow text growth."""
    recs = records()
    ins, _ = patch.decode(recs[58])
    by = {it.off: it for it in ins}
    assert by[0x10B3].ln == 6 and by[0x10B9].kind == "text"
    rec = recs[102]
    assert vm.insn_len(rec, 0x49D) == (1 + 2 * 20 + 2, "op")
    texts = [it.off for it in patch.decode(rec)[0] if it.kind == "text"]
    new, mp = patch.rebuild(rec, {t: b"\x01" * 50 for t in texts})
    patch.verify(rec, new, mp)


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


@needs_disc
def test_bank_relocation_resolves_every_entry():
    """Every (group, index) read through the new root gives the edited string or the original target; the
    heap init calls the hook and the heap starts past the bank."""
    exe = insert.Put((TREE / insert.EXE_NAME).read_bytes())
    edits = insert.bank_edits(marker=True)
    insert.bank_patch(exe, edits, [])
    new, old = bytes(exe.buf), exe.orig
    u32 = lambda d, a: int.from_bytes(d[insert.xo(a):insert.xo(a) + 4], "little")  # noqa: E731
    rd = lambda d, a: (u32(d, a) + 0x80000000) % 2**32 - 0x80000000  # noqa: E731  (self-relative = signed)
    assert int.from_bytes(new[0x1C:0x20], "little") + 0x800 == len(new)
    r0, r1 = u32(old, insert.BANK_PTR), u32(new, insert.BANK_PTR)
    seen, top = set(), 0
    for g in range(insert.BANK_GROUPS):
        t0, t1 = r0 + 4 * g + rd(old, r0 + 4 * g), r1 + 4 * g + rd(new, r1 + 4 * g)
        if g not in insert.TEXT_GROUPS:
            assert t1 == t0, f"data group {g} moved"
            continue
        n = rd(old, t0) // 4
        assert rd(new, t1) // 4 == n, f"group {g}: entry 0 no longer gives the table length"
        for k in range(n):
            a0, a1 = t0 + 4 * k + rd(old, t0 + 4 * k), t1 + 4 * k + rd(new, t1 + 4 * k)
            if a0 in edits:
                seen.add(a0)
                assert new[insert.xo(a1):insert.xo(a1) + len(edits[a0])] == edits[a0]
                top = max(top, a1 + len(edits[a0]))
            elif k:
                assert a1 == a0, f"group {g} entry {k} moved without an edit"
    assert seen == set(edits)
    md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)
    ins = lambda a, n: [f"{i.mnemonic} {i.op_str}" for i in md.disasm(new[insert.xo(a):][:4 * n], a)]  # noqa: E731
    hook = ins(insert.BANK_AT, 17)
    assert hook.count(f"jal {insert.MEMSET:#x}") == 2 and hook[-2:] == ["jr $ra", "addiu $sp, $sp, 0x18"]
    init = ins(0x80036C84, 7)
    heap = (u32(new, 0x80036C8C) & 0xFFFF) << 16 | u32(new, 0x80036C90) & 0xFFFF
    assert init[0] == f"jal {insert.BANK_AT:#x}" and top <= heap < 0x800F0000


@needs_disc
def test_resident_relocation_calls_the_new_text():
    """Resident subs through the new table: unedited ones stay put; an edited one is the old sub byte for byte
    except each edited text op, now `03 -> stub` `01 -> past the old op`, the stub = old op head + text + FF 06."""
    import extract
    exe = insert.Put((TREE / insert.EXE_NAME).read_bytes())
    res = insert.res_edits(marker=True)
    assert res
    insert.bank_patch(exe, {}, [], res)
    new = bytes(exe.buf)
    u32 = lambda a: int.from_bytes(new[insert.xo(a):insert.xo(a) + 4], "little")  # noqa: E731
    s16 = lambda d, a: int.from_bytes(d[a:a + 2], "little", signed=True)  # noqa: E731
    t = u32(insert.RES_PTR)
    for i, addr, rec in extract.resident_records():
        a = (t + 4 * i + u32(t + 4 * i)) & 0xFFFFFFFF
        if i not in res:
            assert a == addr, f"sub {i} moved without an edit"
            continue
        sub = new[insert.xo(a):]
        rest = bytearray(sub[:len(rec)])
        for off, body in res[i].items():
            start, end = vm.text_op(rec, off)
            assert sub[off] == 0x03 and sub[off + 3] == 0x01
            stub = off + 1 + s16(sub, off + 1)
            assert off + 3 + 1 + s16(sub, off + 4) == end + 1
            head = start - off
            assert sub[stub:stub + head] == rec[off:start]
            assert sub[stub + head:stub + head + len(body) + 2] == body + b"\xff\x06"
            rest[off:off + 6] = rec[off:off + 6]
        assert bytes(rest) == rec, f"sub {i}: bytes outside the edited ops changed"


@needs_disc
def test_bmess_rebuild_identity_and_growth():
    """D_BMESS: no edits = same bytes; every unit grown keeps the walk (same units, same field targets)."""
    import bmess
    for slot, r in bmess.records():
        assert bmess.rebuild(r, {}) == r, slot
        units = bmess.texts(r)
        new = bmess.rebuild(r, {s: b"\x41" * (e - s + 7) for s, e in units}, 0x10000)
        nu = bmess.texts(new)
        assert len(nu) == len(units), slot
        assert all(e - s == ou[1] - ou[0] + 7 for (s, e), ou in zip(nu, units)), slot
        ins = bmess.walk(new)[0]
        assert sum(k == "end" for k, _ in ins.values()) == sum(k == "end" for k, _ in bmess.walk(r)[0].values())


def test_canary_needs_no_missing_glyph():
    for ch in font_en.CANARY:
        assert ch in font_en.GLYPHS.values() or ch in font_en.EXISTING or ch in font_en.LATIN, ch
