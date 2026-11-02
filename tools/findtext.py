"""findtext.py: search files for Japanese words encoded with tbl/jp.tbl (game font encoding).

    python -X utf8 tools/findtext.py WORD [WORD..] -- FILE_OR_DIR..
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main():
    i = sys.argv.index("--")
    words, paths = sys.argv[1:i], sys.argv[i + 1:]
    t = Table.load(ROOT / "tbl/jp.tbl")
    pats = {w: t.encode(w) for w in words}
    files = []
    for p in map(Path, paths):
        files += sorted(p.rglob("*")) if p.is_dir() else [p]
    for f in files:
        if not f.is_file():
            continue
        d = f.read_bytes()
        for w, pat in pats.items():
            n, pos, first = 0, d.find(pat), []
            while pos >= 0:
                n += 1
                if len(first) < 4:
                    first.append(hex(pos))
                pos = d.find(pat, pos + 1)
            if n:
                print(f"{f.relative_to(ROOT) if f.is_relative_to(ROOT) else f}\t{w}\t{n}\t{' '.join(first)}")


if __name__ == "__main__":
    main()
