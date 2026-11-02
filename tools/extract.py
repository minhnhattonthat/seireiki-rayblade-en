"""extract.py: decode every string in the game into script/, and check the result roundtrips.

    python -X utf8 tools/extract.py dump [--force]     # write script/ from the original disc tree
    python -X utf8 tools/extract.py check              # roundtrip + coverage, exit 1 on failure

Sources (docs/re/text.md):
  sce/       D_SCE scene scripts (one JSON per slot): text after VM op 0x78.
  resident   the 70 self-relative sub-scripts of the resident system script in the EXE (same VM).
  exe_bank   the EXE message bank: 22 groups, each a table of self-relative u32 pointers to strings
             (group id << 8 | index is the id the code passes to the reader).
  exe_inline FF-terminated strings in the EXE data section that no bank entry points at.

Each entry: id, jp (decoded), en (empty until translated), off/len (source bytes), status.
The extract never clobbers work: `dump` writes only missing files unless --force, and with --force it
keeps any entry that already has `en` text.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import vm  # noqa: E402
from tbl import Table  # noqa: E402

SCRIPT = ROOT / "script"
T = Table.load(ROOT / "tbl/jp.tbl")
EXE = (ROOT / "work/disc/tree/SLPS_026.52").read_bytes()
EXE_BASE = 0x80010000
EXE_DATA = (0x80012500, 0x8001E700)     # system/battle strings live here (docs/re/text.md)
# VM bytecode embedded in the EXE: the Yamato affection hints (op 01 records with 7B speaker + 78 text).
EXE_VM_REGIONS = [(0x800124E0, 0x800126E0)]
BANK_ROOT = 0x8001534C
BANK_GROUPS = 22
CTRL = re.compile(r"\{(?:\w+)(?::[0-9A-F]*)?\}|\[[0-9A-F]{2}\]")
JP = re.compile(r"[\u3000-\u303f\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\u2025\u2026\uff00-\uffef]")


def plausible(text):
    """True when a decoded run reads as game text, not as binary that happens to decode.

    Real strings are mostly Japanese glyphs (kana/kanji/fullwidth punctuation) once the control
    tokens are removed. Short labels ("HP順", "LV順") are allowed with any Japanese at all; longer
    runs need a third of their visible characters to be Japanese."""
    core = CTRL.sub("", text)
    chars = [c for c in core if not c.isspace()]
    if not chars:
        return False
    jp = sum(1 for c in chars if JP.match(c))
    return jp >= 1 and (len(chars) <= 4 or jp / len(chars) >= 1 / 3)


def exe_off(addr):
    return addr - EXE_BASE + 0x800


def u32(addr):
    return struct.unpack_from("<I", EXE, exe_off(addr))[0]


def sweep_texts(rec):
    """(text blocks, skipped bytes) for a VM bytecode record, walking it linearly and skipping
    undecodable bytes. Each block: (op offset, text start, text end)."""
    i, texts, skips = 0, [], []
    while i < len(rec):
        r = vm.insn_len(rec, i)
        if r is None:
            skips.append(i)
            i += 1
            continue
        ln, kind = r
        if kind == "text":
            start, end = vm.text_op(rec, i)
            texts.append((i, start, end))
        i += ln
    return texts, skips


def entry(eid, rec, op, start, end, extra=None):
    e = {"id": eid, "jp": T.decode(rec, start, end - start)[0], "off": op, "len": end + 1 - op,
         "en": "", "status": "todo"}
    if extra:
        e.update(extra)
    return e


def sce_files():
    """{slot: [entries]} for D_SCE."""
    out = {}
    for slot, rec in vm.sce_records():
        texts, _ = sweep_texts(rec)
        if not texts:
            continue
        out[slot] = [entry(f"sce{slot:03d}:{op:05X}", rec, op, a, b,
                           {"style": rec[op + 1], "text_off": a, "text_len": b - a})
                     for op, a, b in texts]
    return out


def resident_records():
    """[(index, addr, rec)] for the 70 self-relative sub-scripts of the resident system script."""
    b = 0x80010374
    n = u32(b) // 4
    t = [b + 4 * i + u32(b + 4 * i) for i in range(n)]
    uniq = sorted(set(t)) + [b + 0x4A00]
    nxt = {s: uniq[i + 1] for i, s in enumerate(uniq[:-1])}
    return [(i, s, EXE[exe_off(s):exe_off(s) + (nxt[s] - s)]) for i, s in enumerate(t)]


def resident_entries():
    out = []
    for i, addr, rec in resident_records():
        texts, _ = sweep_texts(rec)
        out += [entry(f"res{i:02d}:{op:04X}", rec, op, a, b,
                      {"sub": i, "sub_addr": addr, "text_addr": addr + a, "text_len": b - a})
                for op, a, b in texts]
    return out

def bank_entries():
    """Strings of the EXE message bank. Group g's table is BANK_ROOT + u32; entry k is at
    table+4k and points at table+4k+u32, self-relative."""
    lo, hi = EXE_DATA
    out, empty, seen_addr = [], 0, set()
    for g in range(BANK_GROUPS):
        t = BANK_ROOT + 4 * g + u32(BANK_ROOT + 4 * g)
        if not lo <= t < hi:
            continue
        n = u32(t) // 4 if t + 4 <= hi else 0
        for k in range(min(n, 1024)):
            a = t + 4 * k
            if a + 4 > hi:
                break
            tgt = a + u32(a)
            if not lo <= tgt < hi or tgt in seen_addr:
                continue
            end = vm.text_end(EXE, exe_off(tgt))
            if end is None:
                continue
            text, used = T.decode(EXE, exe_off(tgt), end - exe_off(tgt))
            if used != end - exe_off(tgt):
                continue
            if not text.strip() or text == "{end}":
                empty += 1
                continue
            seen_addr.add(tgt)
            out.append({"id": f"bank{g:02d}:{k:03X}", "jp": text, "group": g, "index": k,
                        "addr": tgt, "len": end - exe_off(tgt) + 1, "en": "", "status": "todo"})
    return out, empty


def inline_entries(bank):
    """FF-terminated strings in the EXE data section that no bank entry points at (menus, debug strings).

    Only starts that read as text are taken: the run must begin with a Japanese glyph (or a
    fullwidth space before one), because starting a few bytes early turns the previous string's
    tail into an ASCII prefix and the scan tries every offset anyway."""
    lo, hi = EXE_DATA
    taken = set()
    for e in bank:
        taken.update(range(e["addr"], e["addr"] + e["len"]))
    out = []
    a = lo
    while a < hi:
        if a in taken:
            a += 1
            continue
        i = exe_off(a)
        end = vm.text_end(EXE, i)
        if end is None or not 2 <= end - i <= 300:
            a += 1
            continue
        text, used = T.decode(EXE, i, end - i)
        strong = sum(1 for c in EXE[i:end] if 0x40 <= c <= 0xEE)
        head = CTRL.sub("", text).lstrip("　 \t")
        ok_start = bool(head) and bool(JP.match(head[0]))
        after_ff = a == lo or EXE[exe_off(a) - 1] == 0xFF
        chars = [c for c in head if not c.isspace()]
        ratio = sum(1 for c in chars if JP.match(c)) / len(chars) if chars else 0
        # Quote-delimited speech is unambiguous; bare runs also match the EXE's kana and font
        # tables, so those are left for the marker build to catch.
        quoted = "「" in text or "」" in text
        if (used == end - i and strong >= 2 and ok_start and after_ff and quoted and plausible(text)
                and ratio >= 0.9 and not any(b in taken for b in range(a, a + used + 1))):
            out.append({"id": f"exe:{a:05X}", "jp": text, "addr": a, "len": used + 1,
                        "en": "", "status": "candidate",
                        "notes": "inline EXE string (no pointer table): confirm in the marker build"})
            a += used + 1
        else:
            a += 1
    return out


def exe_vm_entries():
    """Texts of the VM sub-scripts embedded in the EXE (the affection hints)."""
    out = []
    for a, b in EXE_VM_REGIONS:
        rec = EXE[exe_off(a):exe_off(b)]
        for op, s, e in sweep_texts(rec)[0]:
            text = T.decode(rec, s, e - s)[0]
            if not plausible(text):
                continue
            out.append({"id": f"exevm:{a + op:05X}", "jp": text, "addr": a + op, "text_addr": a + s,
                        "text_len": e - s, "len": e + 1 - op, "en": "", "status": "todo"})
    return out


def load(path):
    return json.loads((SCRIPT / path).read_text(encoding="utf-8"))


def keep_old(path, new):
    """Merge: keep en/status/notes of entries already in the file (never clobber translation work)."""
    if not path.exists():
        return new
    old = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))}
    for e in new:
        o = old.get(e["id"])
        if o:
            for k in ("en", "status", "notes", "max"):
                if o.get(k):
                    e[k] = o[k]
    return new


def dump(force=False):
    SCRIPT.mkdir(exist_ok=True)
    (SCRIPT / "sce").mkdir(exist_ok=True)
    n = 0
    for slot, entries in sce_files().items():
        p = SCRIPT / "sce" / f"{slot:03d}.json"
        if p.exists() and not force:
            continue
        merged = keep_old(p, entries)
        p.write_text(json.dumps(merged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        n += len(merged)
    bank, empty = bank_entries()
    for name, entries in (("resident.json", resident_entries()),
                          ("exe_bank.json", bank),
                          ("exe_inline.json", inline_entries(bank)),
                          ("exe_vm.json", exe_vm_entries())):
        p = SCRIPT / name
        if p.exists() and not force:
            continue
        merged = keep_old(p, entries)
        p.write_text(json.dumps(merged, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        n += len(merged)
    print(f"dumped {n} strings into script/")


def all_entries():
    for p in sorted((SCRIPT / "sce").glob("*.json")):
        yield p, json.loads(p.read_text(encoding="utf-8"))
    for name in ("resident.json", "exe_bank.json", "exe_inline.json", "exe_vm.json"):
        p = SCRIPT / name
        if p.exists():
            yield p, json.loads(p.read_text(encoding="utf-8"))


def source_bytes(e):
    """The original byte string for an entry (the text itself, not the terminator)."""
    if e["id"].startswith("sce"):
        slot = int(e["id"][3:6])
        rec = _sce()[slot]
        return rec[e["text_off"]:e["text_off"] + e["text_len"]]
    if "text_addr" in e:
        return EXE[exe_off(e["text_addr"]):exe_off(e["text_addr"]) + e["text_len"]]
    return EXE[exe_off(e["addr"]):exe_off(e["addr"]) + e["len"] - 1]


_SCE = {}


def _sce():
    if not _SCE:
        _SCE.update(dict(vm.sce_records()))
    return _SCE


def check():
    """Roundtrip every extracted string against the original bytes, and re-discover for coverage."""
    bad, total = [], 0
    for p, entries in all_entries():
        for e in entries:
            total += 1
            try:
                raw = T.encode(e["jp"])
            except Exception as ex:
                bad.append((p.name, e["id"], f"encode: {ex}"))
                continue
            orig = source_bytes(e)
            if raw != orig:
                bad.append((p.name, e["id"], f"roundtrip {raw.hex()[:40]} != {orig.hex()[:40]}"))
    # coverage: every text block the decoder finds is in script/
    ids = set()
    for _, entries in all_entries():
        ids.update(e["id"] for e in entries)
    missing = []
    for slot, entries in sce_files().items():
        for e in entries:
            if e["id"] not in ids:
                missing.append(e["id"])
    print(f"{total} strings, {len(bad)} roundtrip errors, {len(missing)} uncovered")
    for b in bad[:10]:
        print("  !", *b)
    for m in missing[:10]:
        print("  ! missing", m)
    return 1 if bad or missing else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["dump", "check"])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.cmd == "dump":
        dump(a.force)
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main())
