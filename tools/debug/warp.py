"""warp.py: reach a named scene from a cold boot (or the title state) with tools/debug/warp.lua.

    python -X utf8 tools/debug/warp.py NAME [NAME..] [--cue build/x.cue] [--title] [--out work/qa/warp]
    python -X utf8 tools/debug/warp.py --all [--jobs 3] [--title] [--match card_]   # regen states + shots
    python -X utf8 tools/debug/warp.py --list
    python -X utf8 tools/debug/warp.py --all --match story_ --deep 30 --cue build/x.cue   # flow check, 30th box

Scene list: tools/debug/scenes.tsv (name, scene, ep, flags, mash, stop_op, stop_after, stop_n, post, frames, route,
note). scene = D_SCE slot, or -1 = the intermission (resident sub-script 5). route = route-str steps after the New
Game press; mash = press circle (or N:keys, e.g. 40:circle+start) every N frames after the route (0 = off); stop_* = end the run when the VM starts
that op (warp.lua STOP_OP), post = route played from that point; frames = run length after the route (a stop ends it
early). Each run writes <out>/<name>/ (shots, log), the last frame to
<out>/<name>.png and a savestate to work/states/<name>.sstate; it passes when warp.lua logged `WARP` (the scene id
reached the VM). Cold boot = logos + intro FMV (5400 frames); --title starts from work/states/title.sstate instead
(regenerate that state after code/font/graphics changes: `--all` does it first when --title is given).
"""
import argparse
import csv
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

CUE = ROOT / "rom/Seireiki Rayblade (Japan).cue"
TITLE_STATE = ROOT / "work/states/title.sstate"
BOOT = "5400 -;6 start;240 -;6 circle"   # tools/routes/boot.txt up to the New Game press
FROM_TITLE = "6 start;240 -;6 circle"


def scenes():
    with open(ROOT / "tools/debug/scenes.tsv", encoding="utf-8") as f:
        return [r for r in csv.DictReader((ln for ln in f if not ln.startswith("#")), delimiter="\t")]


def run(row, cue, out, title):
    name = row["name"]
    d = out / name
    shutil.rmtree(d, ignore_errors=True)
    menu = row["route"].startswith("!")  # "!" = title-screen route of its own (Continue etc.): no New Game, no warp
    pre = ("" if title else "5400 -") if menu else (FROM_TITLE if title else BOOT)
    route = ";".join(x for x in (pre, row["route"].lstrip("!")) if x.strip())
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), str(cue), "--out", str(d),
           "--route-str", route, "--script", str(ROOT / "tools/debug/warp.lua"), "--var", f"SCENE={row['scene']}",
           "--state-out", str(ROOT / f"work/states/{name}.sstate"), "--shot-every", "300", "--timeout", "900"]
    if title:
        cmd += ["--state-in", str(TITLE_STATE)]
    if row["ep"].strip():
        cmd += ["--var", f"EP={row['ep']}"]
    if row["flags"].strip():
        cmd += ["--var", "FLAGS={" + row["flags"] + "}"]
    for k in ("stop_op", "stop_after", "stop_n", "title"):
        if row[k].strip():
            cmd += ["--var", f"{k.upper()}={row[k]}"]
    if row["post"].strip():
        cmd += ["--var", f"POST='{row['post']}'"]
    every, _, keys = (row["mash"] or "0").partition(":")  # "40" or "40:circle+start"
    if int(every):
        cmd += ["--mash", every, "--mash-key", keys or "circle"]
    if int(every) or row["stop_op"].strip():  # run on after the route; a STOP ends it early
        cmd += ["--frames", str(sum(int(s.split()[0]) for s in route.split(";") if s.strip()) + int(row["frames"]))]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (d / "log.txt").read_text(encoding="utf-8", errors="replace") if (d / "log.txt").exists() else ""
    ok = p.returncode == 0 and ("WARP scene=" in log or menu) and (d / "final.png").exists()
    if row["stop_op"].strip() and "STOP op" not in log:
        ok = False  # the screen the entry waits for never came
    if (d / "final.png").exists():
        shutil.copy(d / "final.png", out / f"{name}.png")
    return name, ok, p.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--match", default="")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--cue", type=Path, default=CUE)
    ap.add_argument("--title", action="store_true", help="start from work/states/title.sstate (faster)")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--deep", type=int, default=0, help="text-box scenes stop on the Nth box (flow check)")
    ap.add_argument("--out", type=Path, default=ROOT / "work/qa/warp")
    a = ap.parse_args()
    rows = scenes()
    if a.deep:   # flow check: stop on the Nth text box instead of the row's own count (VM branches still land)
        for r in rows:
            if r["stop_op"].strip() == "0x78":
                r["stop_n"] = str(a.deep)
                r["frames"] = str(max(int(r["frames"] or 0), 2000 + 300 * a.deep))
    if a.list:
        for r in rows:
            print(f"{r['name']:24s} scene={r['scene']:>4s}  {r['note']}")
        return 0
    by = {r["name"]: r for r in rows}
    pick = [r for r in rows if a.match in r["name"]] if a.all else [by[n] for n in a.names]
    if not pick:
        ap.error("name a scene (--list) or pass --all")
    a.out.mkdir(parents=True, exist_ok=True)
    if a.title and (a.all or not TITLE_STATE.exists()):
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), str(a.cue), "--out",
                        str(a.out / "_title"), "--route-str", "5500 -", "--state-out", str(TITLE_STATE)], check=True,
                       capture_output=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda r: run(r, a.cue, a.out, a.title), pick))
    bad = [r for r in res if not r[1]]
    for name, ok, rc in res:
        print(f"{'ok  ' if ok else 'FAIL'} {name} (exit {rc})")
    shots = [str(a.out / f"{r['name']}.png") for r in pick if (a.out / f"{r['name']}.png").exists()]
    if shots:
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/sheet.py"), *shots, "--cols", "6",
                        "--div", "2", "--max", "36", "--out", str(a.out / "sheet.png")])
    print(f"{len(res) - len(bad)}/{len(res)} reached")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
