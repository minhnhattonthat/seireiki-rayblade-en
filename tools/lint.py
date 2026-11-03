"""lint.py: the text lint over everything merged into script/ (check.py runs it; exit 1 on any error).

Per entry with a translatable form (tools/tlform.py form()):
- `en` present, unless the id is in script/keep_jp.txt (id<TAB>reason);
- tlform.check + glossary terms + honorifics (batches.check_entry): ASCII, codes match the JP, {page} counts,
  speaker tags, dialogue/choice/battle widths;
- no stub last line (a wrapped paragraph whose last line is under 6 characters);
- menu rows: pixel width at the VWF advances (font_en.text_px) <= the room: the distance to the next pen move
  ({ctl:XXYY}, YY >= 80: x = XX & 3F columns of 8 px) when the row has one, else the measured room in
  tools/menu_room.tsv (id or bankGG prefix), else the Japanese row's own width.
Prints errors, then one summary line.

    python -X utf8 tools/lint.py [--all-warnings]
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402
import font_en  # noqa: E402
import tlform  # noqa: E402

KEEP = ROOT / "script/keep_jp.txt"
ROOMS = ROOT / "tools/menu_room.tsv"
KNOWN = ROOT / "tools/lint_known.txt"
PEN = re.compile(r"\{ctl:(?!FF)([0-9A-F]{2})([89A-F][0-9A-F])\}")   # FFFF = runtime value, not a pen move
STUB = 6


def keep_list():
    if not KEEP.exists():
        return {}
    out = {}
    for ln in KEEP.read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            i, _, why = ln.partition("\t")
            out[i.strip()] = why
    return out


def rooms():
    """{id or id prefix: px} measured rooms for menu rows without a pen move to bound them."""
    out = {}
    if ROOMS.exists():
        for ln in ROOMS.read_text(encoding="utf-8").splitlines():
            if ln.strip() and not ln.startswith("#"):
                k, px = ln.split("\t")[:2]
                out[k.strip()] = int(px)
    return out


def room_for(eid, rm):
    best = None
    for k, px in rm.items():
        if eid.startswith(k) and (best is None or len(k) > len(best[0])):
            best = (k, px)
    return best[1] if best else None


def segments(row):
    """[(pen column or None, text)] split at pen moves."""
    out, col, last = [], None, 0
    for m in PEN.finditer(row):
        out.append((col, row[last:m.start()]))
        col, last = int(m.group(1), 16) & 0x3F, m.end()
    out.append((col, row[last:]))
    return out


def en_px(s):
    return font_en.text_px(tlform.CODE.sub("", s))


def group_rooms():
    """{bank group: widest JP row} for the list groups 1-11 (one field per group: names, weapons, places...):
    the field fits its longest Japanese entry, so that is a floor for every entry's room. Group 0 is mixed UI."""
    out = {}
    for e in batches.sources()[0][1]:
        if e["id"].startswith("bank") and e["group"] and tlform.form(e) == "menu":
            for j in e["jp"].split("{nl}"):
                out[e["group"]] = max(out.get(e["group"], 0), tlform.jp_line_px(j))
    return out


GROUP_ROOM = {}


def menu_errors(e, en, rm):
    errs = []
    jl, el = e["jp"].split("{nl}"), en.split("{nl}")
    if len(jl) > len(el):
        return errs                     # tlform.check reports the row count
    jl += [jl[-1]] * (len(el) - len(jl))   # help text may take an extra row (tlform.HELP_ROWS)
    if not GROUP_ROOM:
        GROUP_ROOM.update(group_rooms())
    measured = room_for(e["id"], rm)
    if measured is None and GROUP_ROOM.get(e.get("group")):
        measured = GROUP_ROOM[e["group"]]
    for j, x in zip(jl, el):
        # English may add pen moves (aligning a value column), so the rooms come from the English row's own pens:
        # a segment ends at the next pen to its right; a pen to column 0 or leftwards starts a new line instead.
        xs = segments(x)
        for k, (col, xt) in enumerate(xs):
            nxt = xs[k + 1][0] if k + 1 < len(xs) else None
            start = col or 0
            if nxt is not None and nxt > start:
                room = (nxt - start) * 8
            elif measured is not None:
                room = measured - start * 8      # measured = the whole line's room (cell chain)
            else:
                room = tlform.jp_line_px(j) if len(xs) == 1 else tlform.jp_line_px(segments(j)[min(k, len(segments(j)) - 1)][1])
            if en_px(xt) > room:
                errs.append(f"menu text {en_px(xt)} px > room {room} px: {xt!r}")
    return errs


def stubs(e, en):
    f = tlform.form(e)
    if f not in ("dlg", "battle"):
        return []
    out = []
    for s in tlform.layout(e, en).split("{page}"):
        lines = s.split("{nl}")
        chars = [len(tlform.CODE.sub("", x)) for x in lines[-2:]]
        new_page = f == "dlg" and (len(lines) - 1) % 3 == 0     # a short last sentence alone on its page is a beat
        if len(lines) > 1 and 0 < chars[1] < STUB and chars[0] > STUB and not new_page:
            out.append(f"stub last line {lines[-1]!r}")
    return out


def main():
    g = batches.glossary()
    sp, tm = batches.speakers(g), batches.terms(g)
    gl_jp = {j for j, *_ in tm}
    keep, rm = keep_list(), rooms()
    errs, n, seen = [], 0, set()
    for _, es in batches.sources():
        for e in es:
            f = tlform.form(e)
            if f == "junk":
                continue
            n += 1
            seen.add(e["id"])
            en = e.get("en", "")
            if not en:
                if e["id"] not in keep:
                    errs.append(f"{e['id']}: no English ({f})")
                continue
            ce, cen = e, en
            if f in ("menu", "special"):             # pen moves are layout: the English may add or move them
                ce, cen = dict(e, jp=PEN.sub("", e["jp"])), PEN.sub("", en)
            er, _ = batches.check_entry(ce, cen, sp, tm, gl_jp)
            # special = hand-laid rows ({fb} small-font runs kept as [XX] bytes, padding sized to the JP pixel
            # positions, pens that jump back over the text): checked in-game (work/qa/p7spec), not measured here
            if f == "special":
                er = [x for x in er if not x.startswith(("glossary:", "[XX]", "menu row"))]
            er += stubs(e, en)
            if f == "menu":
                er = [x for x in er if not x.startswith("menu row")]
                er += menu_errors(e, en, rm)
            errs += [f"{e['id']}: {x}" for x in er]
    for i in set(keep) - seen:
        errs.append(f"{i}: in keep_jp.txt but not a translatable entry")
    # shortcut: KNOWN lists open errors being worked on (phase 7); it must be empty when the phase closes
    known = set(KNOWN.read_text(encoding="utf-8").splitlines()) if KNOWN.exists() else set()
    new = [x for x in errs if x not in known]
    for x in new:
        print(x)
    stale = known - set(errs) - {""}
    for x in sorted(stale):
        print(f"fixed, remove from {KNOWN.name}: {x}")
    print(f"lint: {n} entries, {len(new)} errors" + (f", {len(errs) - len(new)} known open (tools/{KNOWN.name})"
                                                       if len(errs) > len(new) else ""))
    sys.exit(1 if new or stale else 0)


if __name__ == "__main__":
    main()
