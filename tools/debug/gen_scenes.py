"""gen_scenes.py: (re)write tools/debug/scenes.tsv from D_SCE (scene-2 dispatcher -> story_*, battle scenes ->
card_NN) plus the hand-written menu/battle/ending entries below. Run from the repo root:
    python -X utf8 tools/debug/gen_scenes.py
Edit the hand entries here, not in the .tsv. Facts behind it: docs/re/flow.md.
"""
import re
import sys
sys.path.insert(0, "tools")
import arc

d = open("work/disc/tree/D_SCE.BIN", "rb").read()
E = arc.entries(d)
rec = lambda n: d[E[n][0]:E[n][1]]
COLS = "name scene ep title flags mash stop_op stop_after stop_n post frames route note".split()
rows = []


def add(name, scene, note, ep="", title="", flags="", mash="", stop_op="", stop_after="", stop_n="", post="",
        frames="", route=""):
    rows.append(dict(name=name, scene=scene, ep=ep, title=title, flags=flags, mash=mash, stop_op=stop_op,
                     stop_after=stop_after, stop_n=stop_n, post=post, frames=frames, route=route, note=note))


labels = ["S01", "S03", "S04", "S06", "S09", "S09.5", "S10", "S11", "S11.5", "S13", "S15", "S16", "S17", "S20",
          "S21", "S22", "S23", "S24", "S25", "S26", "S27", "S28", "S29", "S30", "S31", "S32"]
r2 = rec(2)
targets = [r2[0x17 + 13 * i + 11] | r2[0x17 + 13 * i + 12] << 8 for i in range(26)]
for lab, sc in zip(labels, targets):
    add(f"story_{lab.replace('.', '_')}", sc, f"chapter start {lab} (scene 2 dispatcher), third text box",
        mash="40", stop_op="0x78", stop_after="20", stop_n="3", frames="4000")

first = {}
for sl in range(len(E)):
    r = rec(sl)
    for m in re.finditer(rb"\x40\xff", r):
        t = r.find(b"\x16\x03", m.start(), m.start() + 12)
        if t >= 0 and r[t + 3] == 0 and r[t + 2] not in first:
            first[r[t + 2]] = (sl, m.start())
first.pop(53)  # its scene 77 stops on a pre-battle sortie screen first: shown below via scene 128 + TITLE
for t in range(69):  # 80 banner slots (4 sheets x 20); 69 titles in the DC port
    if t in first:
        sl, at = first[t]
        bump = rec(sl)[:2] == b"\x16\x01"
        late = at > 0x100  # dialogue before the map load: mash through it (the card's own waits ignore circle)
        add(f"card_{t:02d}", sl, f"chapter card title {t} (D_SYSTEM banner), battle scene {sl}",
            ep=str(t if bump else t + 1), mash="40" if late else "", stop_op="0x8C", stop_after="530",
            frames="12000" if late else "3000")
    else:  # no script sets this title (53: see above): poke it into scene 128's card
        add(f"card_{t:02d}", 128, f"chapter card title {t} poked over battle scene 128 ({'scene 77' if t == 53 else 'no script uses it'})",
            ep=str(t + 1), title=str(t), stop_op="0x8C", stop_after="530", frames="3000")
add("sortie_select", 77, "pre-battle sortie (unit selection) screen, scene 77", mash="40", frames="9000")

add("intermission", -1, "intermission menu (resident sub-script 5)", route="400 -")
add("int_save", -1, "intermission > Save: memory card slot select", route="400 -;6 circle;300 -")
add("int_system", -1, "intermission > System: options list", route="400 -;8 down;45 -;6 circle;200 -")
add("int_next", -1, "intermission > Next: end-intermission confirm", route="400 -;8 down;45 -;8 down;45 -;6 circle;200 -")
# sound test (5 downs) and memory album (8 downs) stop the emulator from this state: docs/status.md open items
for n, (name, note) in [(6, ("sys_character", "System > Character settings")), (7, ("sys_unit", "System > Unit settings"))]:
    add(name, -1, note + " (list empty at New Game state)",
        route="400 -;8 down;45 -;6 circle;150 -" + ";6 down;45 -" * n + ";6 circle;400 -")
add("continue", 1, "title > Continue: memory card load screen", route="!300 -;8 down;45 -;6 circle;600 -")
add("credits", 0, "staff roll (scene 0; endings 347-352 end here too)", route="2400 -")
B = dict(ep="1", mash="40", stop_op="0x43", stop_after="30", frames="5000")
add("battle_map", 128, "first battle (map 6), player phase, move range", **B)
add("battle_unit_menu", 128, "battle: unit command menu + status panel", post="6 cross;90 -", **B)
add("battle_trust", 128, "battle: unit menu > Trust", post="6 cross;60 -;6 down;45 -;6 circle;150 -", **B)
add("battle_ability", 128, "battle: unit menu > Ability", post="6 cross;60 -;6 down;45 -;6 down;45 -;6 circle;150 -",
    **B)
add("event_103_guard", 103, "private event dev guard (flag 0x1B0 unset); with the flag it stays black: needs "
    "the intermission free-roam context (TODO)", stop_op="0x78", stop_after="30", frames="3000")
for sl in range(347, 353):
    add(f"ending_{sl}", sl, "ending (route variant), third text box", mash="40", stop_op="0x78", stop_after="20",
        stop_n="3", frames="4000")

with open("tools/debug/scenes.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("# Debug-tool scene list: python -X utf8 tools/debug/warp.py --list | NAME | --all. Columns: warp.py --help.\n")
    f.write("\t".join(COLS) + "\n")
    for r in rows:
        f.write("\t".join(str(r[c]) for c in COLS) + "\n")
print(len(rows))
