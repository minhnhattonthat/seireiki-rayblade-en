"""story.py: chapter files for the story pass (skill references/translation.md §Review).

    python -X utf8 tools/story.py   # -> work/qa/story/chapters/chNN_sAAA-BBB.txt

D_SCE scenes in slot order, cut at the scene groups of docs/synopsis.md and at ~MAX lines (one reviewer's read).
Each line: `>> id | speaker | JP` then `   EN`; control codes dropped, {nl} shown as " / "."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work/qa/story/chapters"
GROUPS = [0, 1, 3, 10, 26, 48, 80, 128, 130, 186, 191, 192, 219, 231, 256, 299, 336, 347, 362, 368, 384]
MAX = 900
CODE = re.compile(r"\{(?!nl\})[^}]*\}")


def clean(s):
    return CODE.sub("", s).replace("{nl}", " / ").strip()


def speaker(jp):
    m = re.match(r"([^「（\s]{1,12})[「（]", clean(jp))
    return m.group(1) if m else "-"


def scenes():
    for f in sorted((ROOT / "script/sce").glob("*.json")):
        rows = [e for e in json.loads(f.read_text(encoding="utf-8")) if e.get("en") and e.get("form") != "junk"]
        if rows:
            yield int(f.stem), rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()
    chunks, cur = [], []
    for slot, rows in scenes():
        if cur and (slot in GROUPS or sum(len(r) for _, r in cur) + len(rows) > MAX):
            chunks.append(cur)
            cur = []
        cur.append((slot, rows))
    chunks.append(cur)
    for n, ch in enumerate(chunks):
        name = f"ch{n:02d}_s{ch[0][0]:03d}-{ch[-1][0]:03d}.txt"
        lines = []
        for slot, rows in ch:
            lines.append(f"## scene {slot:03d}")
            lines += [f">> {e['id']} | {speaker(e['jp'])} | {clean(e['jp'])}\n   {clean(e['en'])}" for e in rows]
        (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(chunks)} chapters -> {OUT}")


if __name__ == "__main__":
    main()
