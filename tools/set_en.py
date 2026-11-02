"""set_en.py: replace the `en` of single script entries from a TSV (id<TAB>English), e.g. menu-fit rewordings.

    python -X utf8 tools/set_en.py FILE.tsv        # prints each change; unknown ids fail

Lines starting with # are comments. JSON is written the way batches.py merge writes it (indent 1, LF).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def main(path):
    want = {}
    for ln in Path(path).read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            i, _, en = ln.partition("\t")
            want[i.strip()] = en
    done = set()
    for p, es in batches.sources():
        changed = False
        for e in es:
            if e["id"] in want:
                done.add(e["id"])
                if e.get("en") != want[e["id"]]:
                    print(f"{e['id']}: {e.get('en', '')!r} -> {want[e['id']]!r}")
                    e["en"], e["status"] = want[e["id"]], "translated"
                    changed = True
        if changed:
            p.write_text(json.dumps(es, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    missing = set(want) - done
    if missing:
        sys.exit(f"unknown ids: {sorted(missing)}")


if __name__ == "__main__":
    main(sys.argv[1])
