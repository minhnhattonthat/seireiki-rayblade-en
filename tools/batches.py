"""batches.py: translation batches for agents, their check, merge and review pairs.

    python -X utf8 tools/batches.py split [--chars 3500] [--max 130]   # work/tl/bNNN.tsv/.json/.terms.txt (refuses to overwrite)
    python -X utf8 tools/batches.py check bNNN [bNNN ...]             # OK or the problems, exit 1 on errors
    python -X utf8 tools/batches.py merge bNNN [...]                  # checked output -> script/**.json `en` (+ dups)
    python -X utf8 tools/batches.py pairs bNNN [...]                  # work/tl/bNNN.pairs.txt for the reviewer
    python -X utf8 tools/batches.py status                            # batches done / merged

Units are deduplicated by (form, JP): a line repeated in another scene is translated once and merged everywhere.
Input TSV: id, speaker (EN), form, limit, JP view (` / ` = a line break of the original box; {nl} kept literally in
choice/menu rows). Output: work/tl/bNNN.out.tsv, `id<TAB>English`.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import tlform  # noqa: E402

TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
KATA = "ァ-ヺー<E1>"
HONORIFICS = {"さん": "-san", "くん": "-kun", "君": "-kun", "ちゃん": "-chan", "様": "-sama", "さま": "-sama",
              "殿": "-dono"}
TERM_TABLES = ("characters", "places", "items / skills / terms", "mechs", "weapons")


def sources():
    """[(file, entries)] in story order: bank (names/menus first), scenes, resident, battle messages."""
    out = [(SCRIPT / "exe_bank.json", None)]
    out += [(p, None) for p in sorted((SCRIPT / "sce").glob("*.json"))]
    out += [(SCRIPT / "resident.json", None), (SCRIPT / "bmess.json", None)]
    return [(p, json.loads(p.read_text(encoding="utf-8"))) for p, _ in out]


def view(e):
    s = re.sub(r"#[0-9A-F]{3}", "", e["jp"]).replace("<E1>", "ヴ")
    if tlform.form(e) in ("dlg", "battle"):
        s = re.sub(r"\{nl\}　*", " / ", s)
    return s


def limit(e):
    f = tlform.form(e)
    if f == "menu":
        return "/".join(str(tlform.jp_line_px(x) // 8) for x in e["jp"].split("{nl}")) + "ch"
    return {"dlg": "30/line", "battle": "36x3", "choice": "30/item"}[f]


def glossary():
    """{table: [(jp, en, avoid)]} from glossary.md's markdown tables."""
    tables, cur = {}, None
    for ln in GLOSSARY.read_text(encoding="utf-8").splitlines():
        if ln.startswith("## "):
            cur = ln[3:].strip().lower()
            continue
        if cur and ln.startswith("|") and not re.match(r"^\|\s*(JP|---)", ln):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and cells[1]:
                avoid = cells[4] if len(cells) > 4 else ""
                tables.setdefault(cur, []).append((cells[0], cells[1], avoid))
    return tables


def speakers(g=None):
    g = g or glossary()
    out = {}
    for t in ("characters", "speaker labels"):
        for jp, en, _ in g.get(t, []):
            for j in jp.split("/"):
                out.setdefault(j.strip(), en.split("/")[0].strip())
    return out


def run_re(jp):
    """whole-run match: a katakana term not inside a longer katakana word, a kanji term not inside a compound."""
    j = re.escape(jp)
    if re.fullmatch(f"[{KATA}・＝]+", jp):
        return re.compile(f"(?<![{KATA}]){j}(?![{KATA}])")
    if re.fullmatch(r"[一-鿿々]+", jp):
        return re.compile(rf"(?<![一-鿿々]){j}(?![一-鿿々])")
    return re.compile(j)


def terms(g=None):
    g = g or glossary()
    out = []
    for t in TERM_TABLES:
        for jp, en, avoid in g.get(t, []):
            for j in jp.split("/"):
                out.append((j.strip(), en, avoid, run_re(j.strip())))
    return out


def jp_plain(e):
    return re.sub(r"#[0-9A-F]{3}", "", e["jp"]).replace("<E1>", "ヴ")


def split(a):
    TL.mkdir(parents=True, exist_ok=True)
    if list(TL.glob("b[0-9][0-9][0-9].tsv")):
        raise SystemExit("work/tl already has batches; refusing to overwrite (move them away first)")
    seen, groups = set(), []          # groups: (name, [entries]) by scene / bank group / bmess slot
    for p, es in sources():
        cur = {}
        for e in es:
            f = tlform.form(e)
            if f in ("junk", "special"):
                continue
            key = (f, e["jp"])
            if key in seen:
                continue
            seen.add(key)
            unit = (p.stem + ":" + str(e.get("group", e.get("slot", ""))))
            cur.setdefault(unit, []).append(e)
        groups += list(cur.items())
    g = glossary()
    tm = terms(g)
    sp = speakers(g)
    batches, cur, size = [], [], 0
    for _, es in groups:
        if cur and cur[-1]["id"][:3] != es[0]["id"][:3]:   # never mix bank / scenes / resident / battle
            batches.append(cur)
            cur, size = [], 0
        for e in es:
            n = len(view(e))
            if cur and (size + n > a.chars or len(cur) >= a.max):
                batches.append(cur)
                cur, size = [], 0
            cur.append(e)
            size += n
        if size > a.chars * 0.6:      # close at a scene boundary once the batch is well filled
            batches.append(cur)
            cur, size = [], 0
    if cur:
        batches.append(cur)
    for k, es in enumerate(batches, 1):
        name = f"b{k:03d}"
        rows, raw = [], []
        for e in es:
            tg = tlform.tags(jp_plain(e))
            spk = sp.get(tg[0][1], tg[0][1]) if tg else ""
            rows.append("\t".join([e["id"], spk, tlform.form(e), limit(e), view(e)]))
            raw.append({k2: e[k2] for k2 in ("id", "jp", "style", "status") if k2 in e})
        (TL / f"{name}.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
        (TL / f"{name}.json").write_text(json.dumps(raw, ensure_ascii=False, indent=0), encoding="utf-8")
        write_terms(name, raw, tm, sp)
    print(f"{len(batches)} batches, {sum(map(len, batches))} units, {len(seen)} unique")


def write_terms(name, raw, tm, sp):
    """work/tl/<batch>.terms.txt: the glossary rows (and speaker tags) whose JP occurs in the batch."""
    used = {}
    for e in raw:
        jp = jp_plain(e)
        for j, en, avoid, rx in tm:
            if rx.search(jp):
                used[j] = (en, avoid)
        for _, t, _ in tlform.tags(jp):
            used.setdefault(t, (sp.get(t, "?? (not in glossary)"), ""))
    (TL / f"{name}.terms.txt").write_text(
        "".join(f"{j}\t{en}" + (f"\tavoid: {av}" if av else "") + "\n" for j, (en, av) in sorted(used.items())),
        encoding="utf-8")


def refresh_terms(a):
    """rewrite every batch's terms file from the current glossary (between waves, after merging NEW TERMs)."""
    g = glossary()
    tm, sp = terms(g), speakers(g)
    names = sorted(p.stem for p in TL.glob("b[0-9][0-9][0-9].json"))
    for name in names:
        write_terms(name, json.loads((TL / f"{name}.json").read_text(encoding="utf-8")), tm, sp)
    print(f"terms refreshed for {len(names)} batches")


def read_out(name):
    p = TL / f"{name}.out.tsv"
    if not p.exists():
        return None, [f"{p.name} missing"]
    out, errs = {}, []
    for n, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if not ln.strip():
            continue
        if "\t" not in ln:
            errs.append(f"line {n}: no TAB")
            continue
        i, en = ln.split("\t", 1)
        if i in out:
            errs.append(f"{i}: duplicate id")
        out[i] = en
    return out, errs


def check_batch(name, g=None, quiet=False):
    g = g or glossary()
    sp, tm = speakers(g), terms(g)
    gl_jp = {j for j, *_ in tm}
    raw = json.loads((TL / f"{name}.json").read_text(encoding="utf-8"))
    out, errs = read_out(name)
    warns = []
    if out is None:
        return errs, warns
    ids = [e["id"] for e in raw]
    for i in set(out) - set(ids):
        errs.append(f"{i}: not in the batch")
    for e in raw:
        en = out.get(e["id"])
        if en is None:
            errs.append(f"{e['id']}: missing")
            continue
        er, wa = check_entry(e, en, sp, tm, gl_jp)
        errs += [f"{e['id']}: {x}" for x in er]
        warns += [f"{e['id']}: {x}" for x in wa]
    return errs, warns


def check_entry(e, en, sp, tm, gl_jp):
    """(errors, warnings) for one entry's English: tlform's layout checks + glossary terms + honorifics."""
    jp = jp_plain(e)
    er, wa = tlform.check(dict(e, jp=jp), en, sp)
    low = en.lower()
    for j, t_en, avoid, rx in tm:
        if j in jp and rx.search(jp) and t_en.lower() not in low and t_en.split(" ")[0].lower() not in low:
            er.append(f"glossary: {j} -> {t_en} missing")
        if not avoid:
            continue
        for av in filter(None, (x.strip() for x in avoid.split(","))):
            if re.search(rf"\b{re.escape(av)}\b", en):
                er.append(f"glossary: avoid {av!r} (use {t_en})")
    for m in re.finditer(f"([{KATA}]+)(さん|くん|君|ちゃん|様|さま|殿)(?!下)", jp):
        if m.group(0) in gl_jp or m.group(1) in ("ムコ", "ジイ", "バア"):  # glossary row decides (バルちゃん); common nouns: groom, old man/woman
            continue
        if len(m.group(1).replace("ー", "")) >= 2 and HONORIFICS[m.group(2)] not in en:  # not ばーさん
            er.append(f"honorific {m.group(1)}{m.group(2)} needs {HONORIFICS[m.group(2)]}")
    return er, wa


def check(a):
    g, bad = glossary(), 0
    for name in a.batches:
        errs, warns = check_batch(name, g)
        for w in warns:
            print("warn", w)
        for x in errs:
            print(x)
        print(f"{name}: " + ("OK" if not errs else f"{len(errs)} errors") + (f", {len(warns)} warnings" if warns else ""))
        bad += bool(errs)
    sys.exit(1 if bad else 0)


def merge(a):
    g = glossary()
    tr = {}
    cur = {x["id"]: x for _, es in sources() for x in es}  # the batch's jp predates later tbl fixes: key on today's
    for name in a.batches:
        errs, _ = check_batch(name, g)
        if errs:
            raise SystemExit(f"{name}: {len(errs)} errors, not merged (run check)")
        raw = json.loads((TL / f"{name}.json").read_text(encoding="utf-8"))
        out, _ = read_out(name)
        for e in raw:
            c = cur.get(e["id"], e)
            tr[(tlform.form(c), c["jp"])] = out[e["id"]]
    n = 0
    for p, es in sources():
        changed = False
        for e in es:
            t = tr.get((tlform.form(e), e["jp"]))
            if t is not None and e.get("en") != t:
                e["en"], e["status"] = t, "translated"
                changed, n = True, n + 1
        if changed:
            p.write_text(json.dumps(es, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged {len(tr)} units into {n} entries")


def pairs(a):
    for name in a.batches:
        raw = json.loads((TL / f"{name}.json").read_text(encoding="utf-8"))
        out, _ = read_out(name)
        lines = []
        for e in raw:
            lines.append(f">> {e['id']} | {view(e)}\n   {out.get(e['id'], '(missing)')}")
        p = TL / f"{name}.pairs.txt"
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(p)


def status(a):
    names = sorted(p.stem for p in TL.glob("b[0-9][0-9][0-9].tsv"))
    done = [n for n in names if (TL / f"{n}.out.tsv").exists()]
    print(f"{len(done)}/{len(names)} batches have output")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("split")
    s.add_argument("--chars", type=int, default=3500)
    s.add_argument("--max", type=int, default=130)
    for c in ("check", "merge", "pairs"):
        sub.add_parser(c).add_argument("batches", nargs="+")
    sub.add_parser("status")
    sub.add_parser("terms")
    a = ap.parse_args()
    {"split": split, "check": check, "merge": merge, "pairs": pairs, "status": status, "terms": refresh_terms}[a.cmd](a)


if __name__ == "__main__":
    main()
