"""polish.py: the polish pass over docs/polish.md (Minor findings; the release refuses unticked lines).

    python -X utf8 tools/polish.py split [--size 60]   # unticked lines not yet in a chunk -> work/polish/pNN.txt
    python -X utf8 tools/polish.py show ID [ID..]      # jp + en of script entries (for the agents)
    python -X utf8 tools/polish.py apply pNN           # pNN.en.tsv -> script (set_en), pNN.ticks.tsv -> ticks

A chunk lists `N| <polish line>`. The agent writes work/polish/pNN.en.tsv (`id<TAB>full new English`, only for
lines it fixes) and work/polish/pNN.ticks.tsv (`N<TAB>fixed` or `N<TAB>waived: reason`, one per chunk line).
apply runs set_en, then ticks each line in docs/polish.md (`- [x] ... -- fixed|waived: ...`). Run lint after.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import set_en  # noqa: E402

POLISH = ROOT / "docs/polish.md"
DIR = ROOT / "work/polish"


def chunk_lines(p):
    return {int(n): ln for n, _, ln in (x.partition("| ") for x in p.read_text(encoding="utf-8").splitlines())}


def split(size):
    DIR.mkdir(parents=True, exist_ok=True)
    taken = {ln for p in DIR.glob("p[0-9]*.txt") for ln in chunk_lines(p).values()}
    todo = [ln for ln in POLISH.read_text(encoding="utf-8").splitlines() if ln.startswith("- [ ]") and ln not in taken]
    k = len(list(DIR.glob("p[0-9]*.txt")))
    for i in range(0, len(todo), size):
        p = DIR / f"p{k:02d}.txt"
        p.write_text("".join(f"{n}| {ln}\n" for n, ln in enumerate(todo[i:i + size])), encoding="utf-8")
        print(p, len(todo[i:i + size]))
        k += 1


def show(ids):
    want = set(ids)
    for _, es in batches.sources():
        for e in es:
            if e["id"] in want:
                print(json.dumps({k: e.get(k) for k in ("id", "jp", "en")}, ensure_ascii=False))


def apply(name):
    lines = chunk_lines(DIR / f"{name}.txt")
    en = DIR / f"{name}.en.tsv"
    if en.exists() and en.read_text(encoding="utf-8").strip():
        set_en.main(en)
    ticks = {}
    for x in (DIR / f"{name}.ticks.tsv").read_text(encoding="utf-8").splitlines():
        if x.strip():
            n, _, how = x.partition("\t")
            ticks[int(n)] = how.strip()
    missing = set(lines) - set(ticks)
    if missing:
        sys.exit(f"{name}: no tick for lines {sorted(missing)}")
    text = POLISH.read_text(encoding="utf-8").splitlines()
    pos = {ln: i for i, ln in enumerate(text)}
    for n, ln in lines.items():
        if ln not in pos:
            continue  # already ticked (re-run)
        assert ticks[n].startswith(("fixed", "waived")), f"{name} line {n}: tick must be fixed|waived: {ticks[n]!r}"
        text[pos[ln]] = ln.replace("- [ ]", "- [x]", 1) + f" -- {ticks[n]}"
    POLISH.write_text("\n".join(text) + "\n", encoding="utf-8", newline="\n")
    print(f"{name}: {len(lines)} lines ticked")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "split":
        split(int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--size" else 60)
    elif cmd == "show":
        show(sys.argv[2:])
    elif cmd == "apply":
        apply(sys.argv[2])
    else:
        sys.exit(__doc__)
