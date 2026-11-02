"""tlform.py: how an English line is laid out and checked, shared by tools/batches.py (check) and tools/insert.py.

Translators write paragraphs; the layout here makes the game's lines (docs/widths.md):
- dlg     dialogue box, 30 chars/line, the engine pages every 3 lines (keep the 3rd line of a page to 28: the page
          arrow takes the last column). Lines are word-wrapped here and joined with {nl}.
- battle  D_BMESS band, 36 chars/line, no engine wrap, <= 3 lines per {page} segment.
- choice  one item per {nl}; JP items indented with a full-width space get one ASCII space; <= 30 incl. the space.
- menu    EXE bank strings: kept as written, one line per {nl}; budget = the JP line's pixel width (warning only:
          over-budget menu rows go to the phase-7 engine fit list, docs/widths.md).

`en` in script/*.json holds the translator's text; layout() makes the bytes' source text at insert time.
"""
import re

CODE = re.compile(r"\{[^{}]*\}")
FREE_CODES = {"{nl}", "{page}", "{end}"}        # layout codes: the English may place them differently
# speaker tag at the start of a segment: optional portrait code (battle), a short name, then 「 『 or （
TAG = re.compile(r"^((?:\{ctl:[0-9A-F]{4}\})*)(？+|[^「『（{}　、。！？‥“”]{1,14}?)([「『（])")
EN_TAG = re.compile(r"^((?:\{ctl:[0-9A-F]{4}\})*)([^:{}]{1,24}): ")
OPEN_EN = {"「": "", "『": "'", "（": "("}
JUNK_STYLES = {88, 92, 130}
CHOICE_STYLES = {128, 129, 160, 192}
DLG_W, PAGE_LAST_W, BATTLE_W, BATTLE_LINES, CHOICE_W = 30, 28, 36, 3, 30


def form(e):
    """dlg | battle | choice | menu | junk for a script entry."""
    i = e["id"]
    if i.startswith("bm"):
        return "battle"
    if i.startswith("bank"):
        if e.get("status") == "data" or not re.sub(r"\{[^{}]*\}|　|\s", "", e["jp"]):
            return "junk"
        # small-font runs ({fb}, kept byte for byte) and raw <XXX> cells: done by hand in phase 7, not in batches
        return "special" if "{fb}" in e["jp"] or re.search(r"<[0-9A-F]{3}>", e["jp"]) else "menu"
    if i.startswith("res"):
        return "dlg" if TAG.match(e["jp"]) else "junk"
    if i.startswith("sce"):
        if not CODE.sub("", e["jp"]).strip("　 ") or e.get("style") in JUNK_STYLES or junk_text(e["jp"]):
            return "junk"
        return "choice" if e.get("style") in CHOICE_STYLES else "dlg"
    return "junk"                                   # exe_vm / exe_inline: copies of res58 lines


def junk_text(jp):
    """bytecode decoded as text: Latin letters scattered between kana with no bracket or sentence end."""
    body = CODE.sub("", jp)
    latin = sum(c.isascii() and c.isalnum() for c in body)
    return len(body) >= 4 and latin * 4 >= len(body) and not re.search(r"[「」。！？]", body) and "S0" not in body


def segments(text):
    return text.split("{page}")


def width(s):
    return len(CODE.sub("", s))


def wrap(text, w, last_w=None, lines_per_page=3):
    """Word-wrap one segment into lines (explicit {nl} kept). The last line of every page gets last_w."""
    out = []
    for para in text.split("{nl}"):
        line = ""
        for word in para.split(" "):
            if word == "" and line == "":
                continue
            lim = last_w if last_w and len(out) % lines_per_page == lines_per_page - 1 else w
            cand = f"{line} {word}" if line else word
            if width(cand) <= lim or not line:
                line = cand
            else:
                out.append(line)
                line = word
        out.append(line)
    return out


def jp_line_px(line):
    """pixel width of a JP bank line: one-byte codes 8 px, two-byte (kanji, symbols) 12 px; codes 0."""
    px = 0
    for c in CODE.sub("", line):
        px += 8 if (c.isascii() or "぀" <= c <= "ヿ" or c in "　、。．（）「」『』・々ヵヴ") else 12
    return px


def layout(e, en=None):
    """the text to encode for entry e (English with the game's line breaks)."""
    en = e.get("en", "") if en is None else en
    f = form(e)
    if f == "dlg":
        return "{page}".join("{nl}".join(wrap(s, DLG_W, PAGE_LAST_W)) for s in segments(en))
    if f == "battle":
        return "{page}".join("{nl}".join(wrap(s, BATTLE_W)) if s else s for s in segments(en))
    if f == "choice":
        jl = e["jp"].split("{nl}")
        el = en.split("{nl}")
        return "{nl}".join((" " + x if j.startswith("　") and not x.startswith(" ") else x)
                           for j, x in zip(jl, el)) if len(jl) == len(el) else en
    return en


def tags(text):
    """[(segment index, tag, bracket)] for every segment that opens with a speaker tag."""
    out = []
    for i, s in enumerate(segments(text)):
        m = TAG.match(s)
        if m:
            out.append((i, m.group(2), m.group(3)))
    return out


def check(e, en, speakers):
    """(errors, warnings) for one entry's English. speakers: {jp tag: en name}."""
    errs, warns = [], []
    jp, f = e["jp"], form(e)
    if not en.strip():
        return ["empty English"], []
    bad = sorted({c for c in CODE.sub("", en) if not (32 <= ord(c) < 127 or c == "♥") or c in "{}"})
    if bad:
        errs.append("non-ASCII or brace characters: " + "".join(bad))
    if "\\u" in en or "\t" in en:
        errs.append("escape or tab in text")
    if re.search(r"\[[0-9A-Fa-f]{2}\]", en):
        errs.append("[XX] hex pattern (the encoder reads it as a byte)")
    if re.search(r"\{[^{}]*\}(st|nd|rd|th)\b", en):
        errs.append("ordinal suffix glued to a code")
    jc = sorted(c for c in CODE.findall(jp) if c not in FREE_CODES)
    ec = sorted(c for c in CODE.findall(en) if c not in FREE_CODES)
    if jc != ec:
        errs.append(f"control codes differ: jp {jc} en {ec}")
    unknown = [c for c in CODE.findall(en) if not re.fullmatch(r"\{(nl|page|end|fb|ctl:[0-9A-F]{4}|face:[0-9A-F]{6})\}", c)]
    if unknown:
        errs.append(f"unknown codes {unknown}")
    if f in ("dlg", "battle") and jp.count("{page}") != en.count("{page}"):
        errs.append(f"{{page}} count {en.count('{page}')} != jp {jp.count('{page}')}")
    if f in ("dlg", "battle") and jp.count("{page}") == en.count("{page}"):
        es = segments(en)
        for i, tag, br in tags(jp):
            want = speakers.get(tag)
            if want is None:
                errs.append(f"speaker tag {tag} not in glossary")
                continue
            m = EN_TAG.match(es[i])
            if not m or m.group(2) != want:
                errs.append(f"segment {i + 1} must start with '{want}: ' (speaker {tag})")
            elif OPEN_EN[br] and not es[i][m.end():].startswith(OPEN_EN[br]):
                errs.append(f"segment {i + 1}: {tag}{br} opens with {OPEN_EN[br]!r} after the name")
    if f == "battle":
        for i, s in enumerate(segments(en)):
            n = len(wrap(s, BATTLE_W))
            if n > BATTLE_LINES:
                errs.append(f"battle segment {i + 1} wraps to {n} lines (max {BATTLE_LINES} x {BATTLE_W})")
    if f == "choice":
        jl, el = jp.split("{nl}"), en.split("{nl}")
        if len(jl) != len(el):
            errs.append(f"{len(el)} lines/items, jp has {len(jl)}")
        else:
            for x in layout(e, en).split("{nl}"):
                if width(x) > CHOICE_W:
                    errs.append(f"item over {CHOICE_W}: {x!r}")
    if f == "dlg":
        for ln in "{nl}".join(layout(e, en).split("{page}")).split("{nl}"):
            if width(ln) > DLG_W:
                errs.append(f"word run over {DLG_W}: {ln!r}")
    if f == "menu":
        jl, el = jp.split("{nl}"), en.split("{nl}")
        if len(jl) != len(el):
            errs.append(f"{len(el)} lines, jp has {len(jl)} (menu rows are fixed)")
        else:
            for j, x in zip(jl, el):
                lim = jp_line_px(j) // 8
                if width(x) > lim:
                    warns.append(f"menu row {width(x)} > {lim} chars (JP width): {x!r}")
    return errs, warns
