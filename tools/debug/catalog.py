"""catalog.py: one line per D_SCE scene (slot): size, flag guards, goto-scene candidates, first text lines.

    python -X utf8 tools/debug/catalog.py [--lines 3] > work/debug/catalog.tsv

Text = FF-terminated runs after a `78 xx` text op (see docs/re/text.md). Guards = the developer message
"<hex>のフラグが立っていません" some scripts print when a required story flag is unset. Gotos = `0B lo hi` byte
patterns (VM op 0B = goto scene; byte scan, so a guess until the phase-4 disassembler exists).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import arc  # noqa: E402
from tbl import Table  # noqa: E402

T = Table.load(ROOT / "tbl/jp.tbl")


def texts(rec):
    out, i = [], 0
    while True:
        i = rec.find(b"\x78", i)
        if i < 0 or i + 2 >= len(rec):
            return out
        j = rec.find(b"\xff", i + 2)
        if j < 0:
            return out
        try:
            s = T.decode(rec, i + 2, j - i - 2)[0]
        except Exception:
            i += 1
            continue
        if len(s) >= 4 and "[" not in s:
            out.append(s)
            i = j + 1
        else:
            i += 1


def main():
    n = int(sys.argv[sys.argv.index("--lines") + 1]) if "--lines" in sys.argv else 3
    data = (ROOT / "work/disc/tree/D_SCE.BIN").read_bytes()
    print("slot\tsize\tguards\tgotos\ttext")
    for slot, (s, e) in enumerate(arc.entries(data)):
        rec = data[s:e]
        t = texts(rec)
        guards = sorted({m.group(1) for x in t for m in re.finditer(r"([0-9A-F]+)のフラグが立って", x)})
        gotos = sorted({rec[k + 1] | rec[k + 2] << 8 for k in range(len(rec) - 2)
                        if rec[k] == 0x0B and (rec[k + 1] | rec[k + 2] << 8) < 448 and rec[k + 2] < 2})
        first = " / ".join(x[:40] for x in t if "フラグ" not in x)[:200] if t else ""
        print(f"{slot}\t{e - s}\t{','.join(guards)}\t{len(gotos)}\t{first}")


if __name__ == "__main__":
    main()
