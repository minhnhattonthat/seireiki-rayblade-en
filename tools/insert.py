"""insert.py: put the repo's English (or marker) text back into the game's files.

    python -X utf8 tools/insert.py marker [--slots 1,2,5] [--width 30] [--out work/marker.json]
    python -X utf8 tools/insert.py build  [--slots ...]

    import insert
    insert.changes()          # {"D_SCE.BIN": bytes, "SLPS_026.52": bytes} for build.py

Inserted text comes from script/**: an entry is written when it has `en`, or when marker mode is on (every
entry, so the build shows where each line lands). A text block's bytes are re-encoded with tbl/en.tbl and the
record is rebuilt by patch.py (offset operands rewritten). Records that grow past the script buffer (raised to 0xFFF0, SCRIPT_BUFFER) fail
the build instead of silently overflowing.

Marker text is `[<op offset>] <filler>` trimmed to `--width` characters: at 8 px per glyph that is one full
dialogue line, so a box that is narrower than the line shows the overflow.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import arc  # noqa: E402
import bmess  # noqa: E402
import extract  # noqa: E402
import font_en  # noqa: E402
import gfx_en  # noqa: E402
import patch  # noqa: E402
import tlform  # noqa: E402
import vm  # noqa: E402
from tbl import Table  # noqa: E402

SCRIPT = ROOT / "script"
TREE = ROOT / "work/disc/tree"
EXE_NAME = "SLPS_026.52"
ARCHIVES = ["D_SCE.BIN", "D_BMESS.BIN", "D_SYSTEM.BIN"]      # text-bearing archives (docs/re/text.md)
# The scene loader (0x80058298) allocates the script buffer once (`ori a0, zero, 0x8000` at RAM 0x800582B4,
# file 0x48AB4) and never frees it; the heap keeps >= 480 KB free even mid-battle (tools/heap.py), so the
# build raises it to 0xFFF0 (the largest ori immediate) for English, which runs ~2.5x the Japanese length.
SCRIPT_BUFFER = 0xFFF0
BUFFER_ALLOC = (0x48AB4, bytes.fromhex("00800434"), bytes.fromhex("F0FF0434"))
EN = Table.load(ROOT / "tbl/en.tbl")
JP = Table.load(ROOT / "tbl/jp.tbl")

FILLER = "quick brown fox jumps over the lazy dog "


def marker_text(op, width=30):
    """`[<op offset>] ` plus filler, exactly `width` characters: at 8 px a glyph that is one full dialogue line,
    so a box narrower than the line shows the overflow at once."""
    head = f"[{op:05X}] "
    return head + (FILLER * (width // len(FILLER) + 1))[:max(0, width - len(head))]


def en_text(e):
    """the translator's English laid out into the game's lines (tools/tlform.py), or ''."""
    return tlform.layout(e) if e.get("en") else ""


def load(name, slot=None):
    p = SCRIPT / (f"sce/{slot:03d}.json" if slot is not None else name)
    return json.loads(p.read_text(encoding="utf-8"))


def overrides(path):
    """{id: text} from a TSV of `id<TAB>text` (QA probes: one line replaced to measure a box)."""
    if not path:
        return {}
    out = {}
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        eid, _, text = ln.partition("\t")
        out[eid.strip()] = text
    return out


def sce_edits(marker=False, width=30, slots=None, override=None):
    """{slot: {op: text body bytes}} for every entry that has text to insert. `override` is id->text or a TSV path."""
    override = overrides(override) if isinstance(override, str) else (override or {})
    out = {}
    for p in sorted((SCRIPT / "sce").glob("*.json")):
        slot = int(p.stem)
        if slots and slot not in slots:
            continue
        edits = {}
        for e in json.loads(p.read_text(encoding="utf-8")):
            if e["id"] in override:
                edits[e["off"]] = EN.encode(override[e["id"]])
                continue
            text = en_text(e) or (marker_text(e["off"], width) if marker else "")
            if text:
                edits[e["off"]] = EN.encode(text)
        if edits:
            out[slot] = edits
    return out


# D_BMESS (tools/bmess.py): the battle loader (0x80069980) allocates a 0x200-byte output buffer for the four
# messages the preprocessor 0x800337F0 copies back to back, then one 0xC000 block holding up to four records at
# 0x3000 strides. English needs more of both: stride 0x3FF8 (2x the stride must still fit addiu's +0x7FFF),
# block 4x that, output 0x800. Every immediate is checked against its original before it is rewritten.
BM_STRIDE = 0x3FF8
BM_OUT = (0x80069980, 0x200, 0x800)
BM_BLOCK = 0x80069984
BM_OFFSETS = [0x80069A14, 0x80069A64, 0x80069ABC, 0x80069BE4, 0x80069C50, 0x80069C88, 0x80069CEC]
# free(addr, size) takes the size: the block is freed right after preprocessing, the output after the battle.
BM_FREE_BLOCK = 0x80069D68       # ori a1, zero, 0xC000
BM_FREE_OUT = 0x8006BA78         # addiu a1, zero, 0x200


def bm_marker(e, width=30):
    """`[SSOOOO] filler` in the unit's first text run (slot, offset), control codes kept, other runs dropped."""
    out, first = [], True
    for part in RUN.split(e["jp"]):
        if part.startswith("{"):
            out.append(part)
        elif part and first:
            head = f"[{e['slot']:02X}{e['text_off']:04X}] "
            out.append((head + FILLER * (width // len(FILLER) + 1))[:max(width, len(head))])
            first = False
    return "".join(out)


def bmess_records(marker=False, width=30, override=None, report=None):
    """{slot: rebuilt D_BMESS record} for the records that have text to insert."""
    override, edits = override or {}, {}
    for e in load("bmess.json"):
        text = override.get(e["id"]) or en_text(e) or (bm_marker(e, width) if marker else "")
        if text:
            edits.setdefault(e["slot"], {})[e["text_off"]] = EN.encode(text)
    recs = dict(bmess.records())
    out = {}
    for slot, ed in edits.items():
        try:
            out[slot] = bmess.rebuild(recs[slot], ed, BM_STRIDE)
        except ValueError as ex:
            raise SystemExit(f"D_BMESS slot {slot}: {ex}")
    if report is not None and out:
        report.append(f"D_BMESS: {len(out)} records rebuilt, largest {max(map(len, out.values())):#x}")
    return out


def bmess_exe(exe):
    """Raise the battle-message buffers (see BM_STRIDE) in the EXE."""
    rd = lambda a: int.from_bytes(exe.orig[xo(a):xo(a) + 4], "little")  # noqa: E731
    put = lambda a, ins, why: exe(exe.buf, xo(a), ins.to_bytes(4, "little"), why)  # noqa: E731
    a, old, new = BM_OUT
    for addr, op, reg, was, now, why in ((a, "addiu", 4, old, new, "battle message output alloc"),
                                         (BM_FREE_OUT, "addiu", 5, old, new, "battle message output free"),
                                         (BM_BLOCK, "ori", 4, 0xC000, 4 * BM_STRIDE, "D_BMESS block alloc"),
                                         (BM_FREE_BLOCK, "ori", 5, 0xC000, 4 * BM_STRIDE, "D_BMESS block free")):
        if rd(addr) != mips(op, reg, 0, was):
            raise SystemExit(f"EXE: expected {why} ({op} {was:#x}) at {addr:#x}")
        put(addr, mips(op, reg, 0, now), f"{why} {was:#x} -> {now:#x}")
    for a in BM_OFFSETS:
        w = rd(a)
        k = (w & 0xFFFF) // 0x3000
        if w & 0xFFFF not in (0x3000, 0x6000, 0x9000) or w >> 26 not in (0x09, 0x0D):
            raise SystemExit(f"EXE: expected a D_BMESS stride immediate at {a:#x}")
        put(a, (w & 0xFFFF0000) | k * BM_STRIDE, f"D_BMESS record {k} at +{k * BM_STRIDE:#x}")


def sce_records(edits, report):
    """{slot: new record bytes}, verified; fails when a record cannot hold the text."""
    recs = dict(vm.sce_records())
    out = {}
    for slot, e in edits.items():
        rec = recs[slot]
        rep = []
        new, mp = patch.rebuild(rec, e, rep)
        patch.verify(rec, new, mp, rep)
        if len(new) > SCRIPT_BUFFER:
            raise SystemExit(f"slot {slot}: record {len(new):#x} exceeds the {SCRIPT_BUFFER:#x} script buffer")
        out[slot] = new
        if rep:
            report.append(f"slot {slot}: " + "; ".join(rep[:3]))
    return out


# EXE message bank (docs/re/text.md): `*BANK_PTR` = root of 22 self-relative u32s -> group tables of
# self-relative u32s -> FF-terminated strings. Every reader loads the root through BANK_PTR, and nothing else
# points into the bank, so the build writes a new root + the edited groups' tables and strings past the EXE's
# old end (0x800DCE00, the old heap base) and moves the heap above them (docs/re/disc.md "EXE message bank").
BANK_PTR = 0x80015348
BANK_GROUPS = 22
TEXT_GROUPS = range(12)          # groups 12-21 are struct/data tables that happen to decode
EXE_BASE, EXE_HDR = 0x80010000, 0x800
BANK_AT = 0x800DCE00
HEAP_END = 0x801D0000
MEMSET = 0x800A5194              # BIOS A(2Bh) memset stub
OT_BUF = (0x800DC000, 0xE00)     # buffers below the old heap base the heap init also cleared (0x80020xxx code)
HEAP_INIT_MEMSET = 0x80036C84    # jal memset(0x800DC000, 0, 0xF4000)
HEAP_INIT_FREE = 0x80036C8C      # lui a0 / ori a0 / lui a1 / jal free / ori a1: free(0x800DCE00, 0xF3200)
RUN = re.compile(r"(\{[^}]*\})")


def xo(addr):
    return addr - EXE_BASE + EXE_HDR


def mips(op, *a):
    """The few R3000 encodings the heap-init hook needs (registers as numbers: a0=4 a1=5 a2=6 sp=29 ra=31)."""
    if op == "lui":
        return 0x3C000000 | a[0] << 16 | a[1]
    if op == "ori":
        return 0x34000000 | a[1] << 21 | a[0] << 16 | a[2]
    if op == "addiu":
        return 0x24000000 | a[1] << 21 | a[0] << 16 | (a[2] & 0xFFFF)
    if op in ("sw", "lw"):
        return (0xAC000000 if op == "sw" else 0x8C000000) | a[2] << 21 | a[0] << 16 | (a[1] & 0xFFFF)
    if op == "jal":
        return 0x0C000000 | (a[0] & 0x0FFFFFFF) >> 2
    if op == "jr":
        return a[0] << 21 | 8
    if op == "move":
        return a[1] << 21 | a[0] << 11 | 0x21
    if op == "nop":
        return 0
    raise ValueError(op)


def heap_hook(base):
    """memset wrapper called by the heap init instead of its one big memset: clears the buffers below the old
    heap base and the heap from `base` up, skipping the bank between them."""
    a0, a1, a2, sp, ra = 4, 5, 6, 29, 31
    size = HEAP_END - base
    ins = [("addiu", sp, sp, -0x18), ("sw", ra, 0x10, sp),
           ("lui", a0, OT_BUF[0] >> 16), ("ori", a0, a0, OT_BUF[0] & 0xFFFF), ("move", a1, 0),
           ("jal", MEMSET), ("ori", a2, 0, OT_BUF[1]),
           ("lui", a0, base >> 16), ("ori", a0, a0, base & 0xFFFF), ("move", a1, 0), ("lui", a2, size >> 16),
           ("jal", MEMSET), ("ori", a2, a2, size & 0xFFFF),
           ("lw", ra, 0x10, sp), ("nop",), ("jr", ra), ("addiu", sp, sp, 0x18)]
    return b"".join(mips(*i).to_bytes(4, "little") for i in ins)


def bank_marker(e, width=None):
    """Marker for a bank string: its control codes kept, each text run replaced by filler of the run's pixel
    width, the first run headed by `GKK:` (group, index). `{fb}` toggles the small label font (Lv/Exp/HP drawn
    from other cells, until the next `{fb}` or `{nl}`): those runs are kept as they are."""
    head, out, small = f"{e['group']:X}{e['index']:02X}:", [], False
    for part in RUN.split(e["jp"]):
        if part.startswith("{") or not part or small:
            small = (not small if part == "{fb}" else False if part == "{nl}" else small)
            out.append(part if part.startswith("{") else "".join(f"[{b:02X}]" for b in JP.encode(part)))
            continue
        raw, i, w = JP.encode(part), 0, 0     # advance: one-byte code 8 px, F0-FA two-byte code 12 px
        while i < len(raw):
            two = 0xF0 <= raw[i] <= 0xFA
            w, i = w + (3 if two else 2), i + (2 if two else 1)
        w //= 2
        out.append((head + FILLER * (w // len(FILLER) + 1))[:w])
        head = ""
    return "".join(out)


def bank_edits(marker=False, override=None):
    """{original string address: English bytes incl. the FF end} for the bank entries that have text
    (`override`: id->text, e.g. `bank00:001` for a width probe)."""
    out, override = {}, override or {}
    for e in load("exe_bank.json"):
        if e["status"] == "data":
            continue
        text = override.get(e["id"]) or en_text(e) or (bank_marker(e) if marker and e["group"] in TEXT_GROUPS else "")
        if text:
            out[e["addr"]] = EN.encode(text) + b"\xFF"
    return out


# Resident system script (docs/re/flow.md): `*RES_PTR` -> 70 self-relative u32s -> sub-scripts the VM runs in
# place (op `0C n` calls sub n; all ~20 readers load the table through RES_PTR). An edited sub is copied byte for
# byte after the bank, behind a new table whose other entries point back at the old subs. In the copy each edited
# text op becomes `03 <call stub>` `01 <jump past the old op>` and the stubs (`78 .. <English> FF 06`) go at its
# end, so no offset inside the sub moves: sub 58 mixes bytecode with layout tables the decoder cannot tell apart.
RES_PTR = 0x80010370


def res_edits(marker=False, width=30, override=None):
    """{sub: {text-op offset: body bytes}} for the resident text (Yamato's affection hints, sub 58)."""
    out, override = {}, override or {}
    for e in load("resident.json"):
        if e["status"] == "data":
            continue
        text = override.get(e["id"]) or en_text(e) or (marker_text(e["off"], width) if marker else "")
        if text:
            out.setdefault(e["sub"], {})[e["off"]] = EN.encode(text)
    return out


def res_blob(edits, base, report):
    """New resident table at `base` + the rebuilt subs after it (bytes, 4-aligned)."""
    recs = extract.resident_records()
    n = len(recs)
    blob = bytearray(4 * n)
    s16 = lambda v: (v & 0xFFFF).to_bytes(2, "little")  # noqa: E731
    for i, addr, rec in recs:
        if i in edits:
            new = bytearray(rec)
            for off, body in sorted(edits[i].items()):
                start, end = vm.text_op(rec, off)
                if rec[off] != 0x78 or end + 1 - off < 6:
                    raise SystemExit(f"resident sub {i}: {off:#x} is not a text op with room for call + jump")
                new[off:off + 6] = b"\x03" + s16(len(new) - off - 1) + b"\x01" + s16(end + 1 - (off + 3) - 1)
                new += rec[off:start] + body + b"\xff\x06"
            addr = base + len(blob)
            blob += new + bytes(-len(new) % 4)
            report.append(f"resident sub {i}: {len(rec)} -> {len(new)} bytes at {addr:#x}")
        blob[4 * i:4 * i + 4] = ((addr - (base + 4 * i)) & 0xFFFFFFFF).to_bytes(4, "little")
    return blob


def bank_patch(exe, edits, report, res=None):
    """Write the relocated bank (and the resident script when `res` has edits), the heap-init hook and the
    bigger EXE size into `exe` (a Put)."""
    rd = lambda a: int.from_bytes(exe.orig[xo(a):xo(a) + 4], "little")  # noqa: E731
    root = rd(BANK_PTR)
    hook = heap_hook(0)                        # length only; re-made with the real heap base below
    new_root = BANK_AT + len(hook)
    blob = bytearray(4 * BANK_GROUPS)
    used = set()
    for g in range(BANK_GROUPS):
        t = (root + 4 * g + rd(root + 4 * g)) & 0xFFFFFFFF
        n = rd(t) // 4 if g in TEXT_GROUPS else 0      # data groups: no real count, never rebuilt
        tgts = [(t + 4 * k + rd(t + 4 * k)) & 0xFFFFFFFF for k in range(n)]
        if not any(x in edits for x in tgts):
            tt = t                             # untouched group: the new root points at the old table
        else:
            tt = new_root + len(blob)
            tab, strs, placed = bytearray(4 * n), bytearray(), {}
            for k, x in enumerate(tgts):
                if x in edits or (k == 0 and x == t + 4 * n):   # entry 0 = empty string right after the table
                    if x not in placed:
                        if x not in edits and exe.orig[xo(x)] != 0xFF:
                            raise SystemExit(f"bank group {g}: entry 0 at {x:#x} is not an empty string")
                        placed[x] = tt + 4 * n + len(strs)
                        strs += edits.get(x, b"\xFF")
                    used.add(x)
                    x = placed[x]
                tab[4 * k:4 * k + 4] = ((x - (tt + 4 * k)) & 0xFFFFFFFF).to_bytes(4, "little")
            blob += tab + strs
            blob += bytes(-len(blob) % 4)
        blob[4 * g:4 * g + 4] = ((tt - (new_root + 4 * g)) & 0xFFFFFFFF).to_bytes(4, "little")
    if set(edits) - used:
        raise SystemExit(f"bank: {len(set(edits) - used)} edited strings are not in any group table")
    if res:
        res_at = new_root + len(blob)
        blob += res_blob(res, res_at, report)
        exe(exe.buf, xo(RES_PTR), res_at.to_bytes(4, "little"), "resident script table pointer")
    vwf_at = new_root + len(blob)                  # variable-width hooks + advance table (tools/font_en.py)
    vwf, sites = font_en.vwf_blob(vwf_at)
    blob += vwf
    for addr, orig, new in sites:
        if exe.orig[xo(addr):xo(addr) + len(orig)] != orig:
            raise SystemExit(f"EXE: unexpected code at VWF hook site {addr:#x}")
        exe(exe.buf, xo(addr), new, f"VWF hook at {addr:#x}")
    end = new_root + len(blob)
    heap = (end + 0x7FF) & ~0x7FF
    size = (heap - EXE_BASE + 0x7FF) & ~0x7FF  # PS-X EXE text size is whole sectors
    exe.buf += bytes(EXE_HDR + size - len(exe.buf))
    exe(exe.buf, 0x1C, size.to_bytes(4, "little"), "EXE text size (bank past the old end)")
    exe(exe.buf, xo(BANK_AT), heap_hook(heap) + blob, f"message bank: hook + root + {len(blob)} bytes")
    exe(exe.buf, xo(BANK_PTR), new_root.to_bytes(4, "little"), "bank root pointer")
    exe(exe.buf, xo(HEAP_INIT_MEMSET), mips("jal", BANK_AT).to_bytes(4, "little"), "heap init: memset -> hook")
    lui_a0, ori_a0, lui_a1, _, ori_a1 = (xo(HEAP_INIT_FREE + 4 * i) for i in range(5))
    hs = HEAP_END - heap
    for off, ins, why in ((lui_a0, mips("lui", 4, heap >> 16), "heap base hi"),
                          (ori_a0, mips("ori", 4, 4, heap & 0xFFFF), "heap base lo"),
                          (lui_a1, mips("lui", 5, hs >> 16), "heap size hi"),
                          (ori_a1, mips("ori", 5, 5, hs & 0xFFFF), "heap size lo")):
        exe(exe.buf, off, ins.to_bytes(4, "little"), why)
    report.append(f"EXE: bank {len(edits)} strings at {new_root:#x}..{end:#x}, heap {heap:#x} ({hs // 1024} KB)")


class Put:
    """Every write to a file goes through here: builds the romdiff --writes log and keeps the clean original."""

    def __init__(self, data):
        self.orig = bytes(data)
        self.buf = bytearray(data)
        self.log = []

    def __call__(self, buf, off, data, why):
        old = self.orig[off:off + len(data)].ljust(len(data), b"\0")   # past the original end = zero padding
        self.log.append(f"{off:X} {old.hex()} {data.hex()} {why}")
        buf[off:off + len(data)] = data


def header(data):
    """Slot table of an archive: 4 bytes per slot (self-relative offsets)."""
    n = int.from_bytes(data[:4], "little") // 4
    return data[:4 * n]


def changes(marker=False, width=30, slots=None, report=None, override=None):
    """{filename: bytes} for build.py: the archives and the EXE, rebuilt with the current text."""
    report = [] if report is None else report
    files = {}
    override = overrides(override) if isinstance(override, str) else (override or {})
    edits = sce_edits(marker, width, slots, override)
    recs = sce_records(edits, report) if edits else {}
    exe = Put((TREE / EXE_NAME).read_bytes())
    bm = bmess_records(marker, width, override, report)
    for name in ARCHIVES:
        data = (TREE / name).read_bytes()
        new = arc.pack(data, {"D_SCE.BIN": recs, "D_BMESS.BIN": bm,
                              "D_SYSTEM.BIN": {} if marker else gfx_en.records()}.get(name, {}))
        if new != data:
            files[name] = new
        # The EXE holds its own copy of each archive's slot table (D_SCE at 0x9D5FC, D_BMESS at 0x9DCFC,
        # D_SYSTEM at 0x9787C), and the loader reads that copy: repacking without patching it loads every
        # record from the old offset. It is a byte copy of the file header, so write the new header there.
        old, hdr = header(data), header(new)
        if hdr != old:
            hits = [i for i in range(len(exe.orig)) if exe.orig.startswith(old, i)]
            if len(hits) != 1:
                raise SystemExit(f"{name}: {len(hits)} copies of its slot table in the EXE (expected 1)")
            exe(exe.buf, hits[0], hdr, f"{name} slot table")
            report.append(f"EXE: {name} slot table at {hits[0]:#x} repointed")
    if recs:
        off, old_ins, new_ins = BUFFER_ALLOC
        if exe.orig[off:off + 4] != old_ins:
            raise SystemExit(f"EXE: expected the script-buffer alloc at {off:#x}")
        exe(exe.buf, off, new_ins, "script buffer 0x8000 -> 0xFFF0")
    if bm:
        bmess_exe(exe)
    bank, res = bank_edits(marker, override), res_edits(marker, width, override)
    bank_patch(exe, bank, report, res)             # always: it also places the VWF hook
    font_en.patch(exe.buf, exe)
    if exe.log and bytes(exe.buf) != exe.orig:
        files[EXE_NAME] = bytes(exe.buf)
        report.append(f"EXE: {len(exe.log)} writes")
    return files, exe.log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["marker", "build"])
    ap.add_argument("--slots", default="", help="comma-separated D_SCE slots (default: all)")
    ap.add_argument("--width", type=int, default=30, help="marker line width in characters")
    ap.add_argument("--override", default="", help="TSV of id<TAB>text replacing single lines (QA probes)")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    slots = {int(x, 0) for x in a.slots.split(",") if x.strip()} if a.slots else None
    report = []
    files, log = changes(marker=(a.cmd == "marker"), width=a.width, slots=slots, report=report,
                         override=overrides(a.override))
    for name, data in files.items():
        print(f"  {name}: {len(data)} bytes")
    for line in report[:20]:
        print("  note:", line)
    if a.out:
        Path(a.out).write_text(json.dumps({k: len(v) for k, v in files.items()}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
