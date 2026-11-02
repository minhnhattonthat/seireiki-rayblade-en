"""insert.py: put the repo's English (or marker) text back into the game's files.

    python -X utf8 tools/insert.py marker [--slots 1,2,5] [--width 30] [--out work/marker.json]
    python -X utf8 tools/insert.py build  [--slots ...]

    import insert
    insert.changes()          # {"D_SCE.BIN": bytes, "SLPS_026.52": bytes} for build.py

Inserted text comes from script/**: an entry is written when it has `en`, or when marker mode is on (every
entry, so the build shows where each line lands). A text block's bytes are re-encoded with tbl/en.tbl and the
record is rebuilt by patch.py (offset operands rewritten). Records that grow past the 0x8000 script buffer fail
the build instead of silently overflowing.

Marker text is `[<op offset>] <filler>` trimmed to `--width` characters: at 8 px per glyph that is one full
dialogue line, so a box that is narrower than the line shows the overflow.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import arc  # noqa: E402
import font_en  # noqa: E402
import patch  # noqa: E402
import vm  # noqa: E402
from tbl import Table  # noqa: E402

SCRIPT = ROOT / "script"
TREE = ROOT / "work/disc/tree"
EXE_NAME = "SLPS_026.52"
ARCHIVES = ["D_SCE.BIN", "D_BMESS.BIN", "D_SYSTEM.BIN"]      # text-bearing archives (docs/re/text.md)
SCRIPT_BUFFER = 0x8000
EN = Table.load(ROOT / "tbl/en.tbl")

FILLER = "quick brown fox jumps over the lazy dog "


def marker_text(op, width=30):
    """`[<op offset>] ` plus filler, exactly `width` characters: at 8 px a glyph that is one full dialogue line,
    so a box narrower than the line shows the overflow at once."""
    head = f"[{op:05X}] "
    return head + (FILLER * 3)[:max(0, width - len(head))]


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
            text = e["en"] if e.get("en") else (marker_text(e["off"], width) if marker else "")
            if text:
                edits[e["off"]] = EN.encode(text)
        if edits:
            out[slot] = edits
    return out


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


def exe_edits(marker=False, width=30):
    """In-place text that does not move anything: none yet (EXE bank + resident text is phase 5b)."""
    return [], []


class Put:
    """Every write to a file goes through here: builds the romdiff --writes log and keeps the clean original."""

    def __init__(self, data):
        self.orig = bytes(data)
        self.buf = bytearray(data)
        self.log = []

    def __call__(self, buf, off, data, why):
        self.log.append(f"{off:X} {self.orig[off:off + len(data)].hex()} {data.hex()} {why}")
        buf[off:off + len(data)] = data


def header(data):
    """Slot table of an archive: 4 bytes per slot (self-relative offsets)."""
    n = int.from_bytes(data[:4], "little") // 4
    return data[:4 * n]


def changes(marker=False, width=30, slots=None, report=None, override=None):
    """{filename: bytes} for build.py: the archives and the EXE, rebuilt with the current text."""
    report = [] if report is None else report
    files = {}
    edits = sce_edits(marker, width, slots, override)
    recs = sce_records(edits, report) if edits else {}
    exe = Put((TREE / EXE_NAME).read_bytes())
    for name in ARCHIVES:
        data = (TREE / name).read_bytes()
        new = arc.pack(data, recs if name == "D_SCE.BIN" else {})
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
