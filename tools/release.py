"""release.py: build -> check -> smoke -> leftover Japanese -> QA gates -> polish -> debug off -> xdelta patch ->
re-apply to a clean original and compare -> zip (patch + README only). Stops at the first failure.

    python -X utf8 tools/release.py --version 1.0 [--force]

Writes release/Seireiki_Rayblade_EN_v<ver>.xdelta (Track 1 only: Track 2, the audio, must come out unchanged) and
release/Seireiki_Rayblade_EN_v<ver>.zip (that + README.txt from docs/release-readme.md). The playable image stays in
build/. Refuses to overwrite an existing version without --force. Publishing is the user's call (never here).
"""
import argparse
import hashlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

REL = ROOT / "release"
ORIG1 = ROOT / "rom/Seireiki Rayblade (Japan) (Track 1).bin"
ORIG2 = ROOT / "rom/Seireiki Rayblade (Japan) (Track 2).bin"
NAME = "Seireiki Rayblade (English)"
BUILT1 = ROOT / f"build/{NAME} (Track 1).bin"
BUILT2 = ROOT / f"build/{NAME} (Track 2).bin"
GATES = [("work/qa/manifest.tsv", "work/qa/verdicts"), ("work/qa/story/manifest.tsv", "work/qa/story/verdicts")]
NEW_GAME = (0xE20, b"\x0b\x01\x00")   # resident script's New Game `0B 01 00` (warp.lua patches it in RAM only)
KEEP_JP_SLOTS = {239}                  # D11: dev scenario lists stay Japanese


def step(msg):
    print(f"== {msg}", flush=True)


def run(cmd, what):
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT)
    if r.returncode:
        sys.exit(f"release: {what} failed (exit {r.returncode})")


def sha1(p):
    with open(p, "rb") as f:
        return hashlib.file_digest(f, "sha1").hexdigest()


def crc32(p):
    import zlib
    c = 0
    with open(p, "rb") as f:
        while b := f.read(1 << 20):
            c = zlib.crc32(b, c)
    return f"{c:08X}"


def text_bodies():
    """Every decoded text body of the built D_SCE (slot 239 excluded), FF-separated: what the game can show."""
    import arc
    import patch
    import vm
    d = (ROOT / "build/files/D_SCE.BIN").read_bytes()
    out = bytearray()
    for slot, (s, e) in enumerate(arc.entries(d)):
        if slot in KEEP_JP_SLOTS:
            continue
        rec = d[s:e]
        for it in patch.decode(rec)[0]:
            if it.kind == "text":
                start, end = vm.text_op(rec, it.off)
                out += rec[start:end] + b"\xff"
    return bytes(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", required=True)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    stem = f"Seireiki_Rayblade_EN_v{a.version}"
    patch_out, zip_out = REL / f"{stem}.xdelta", REL / f"{stem}.zip"
    if (patch_out.exists() or zip_out.exists()) and not a.force:
        sys.exit(f"release: {stem} exists; pass --force to overwrite")
    py = [sys.executable, "-X", "utf8"]

    step("build")
    run(py + ["tools/build.py"], "build")
    step("tests + extraction + lint")
    run(py + ["tools/check.py"], "check")
    step("smoke (cold boot of the built image)")
    with tempfile.TemporaryDirectory() as t:
        run(py + [Path(SKILL) / "scripts/emu.py", ROOT / f"build/{NAME}.cue", "--out", t,
                  "--route", "tools/routes/boot.txt", "--smoke"], "smoke")
    step("leftover Japanese in the dialogue the game can show")
    with tempfile.TemporaryDirectory() as t:
        f = Path(t) / "sce_text.bin"
        f.write_bytes(text_bodies())
        run(py + [Path(SKILL) / "scripts/jp_left.py", f, "--tbl", "tbl/jp.tbl", "--min", "8"], "jp_left (D_SCE text)")
    run(py + [Path(SKILL) / "scripts/jp_left.py", "build/files/D_BMESS.BIN", "--tbl", "tbl/jp.tbl", "--min", "8"],
        "jp_left (D_BMESS)")
    step("QA gates")
    for man, ver in GATES:
        run(py + [Path(SKILL) / "scripts/qa_gate.py", "check", man, ver], f"qa_gate {man}")
    step("polish list")
    open_ = [ln for ln in (ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines()
             if ln.startswith("- [ ]")]
    if open_:
        sys.exit(f"release: docs/polish.md has {len(open_)} unticked lines, e.g. {open_[0][:100]}")
    step("debug tool off")
    exe = (ROOT / "build/files/SLPS_026.52").read_bytes()
    off, want = NEW_GAME
    if exe[off:off + len(want)] != want:
        sys.exit("release: the New Game op is patched in the built EXE (debug warp baked in?)")
    if sha1(BUILT2) != sha1(ORIG2):
        sys.exit("release: Track 2 changed; the patch covers Track 1 only")

    step("patch + re-apply check")
    REL.mkdir(exist_ok=True)
    run(["xdelta3", "-e", "-9", "-f", "-s", ORIG1, BUILT1, patch_out], "xdelta3 encode")
    with tempfile.TemporaryDirectory() as t:
        back = Path(t) / "track1.bin"
        run(["xdelta3", "-d", "-f", "-s", ORIG1, patch_out, back], "xdelta3 decode")
        if sha1(back) != sha1(BUILT1):
            sys.exit("release: the re-applied patch does not reproduce the built Track 1")
    step("README + zip")
    readme = (ROOT / "docs/release-readme.md").read_text(encoding="utf-8").format(
        version=a.version, patch=patch_out.name,
        orig_size=ORIG1.stat().st_size, orig_crc=crc32(ORIG1), orig_sha1=sha1(ORIG1),
        new_size=BUILT1.stat().st_size, new_crc=crc32(BUILT1), new_sha1=sha1(BUILT1),
        track2_sha1=sha1(ORIG2))
    with zipfile.ZipFile(zip_out, "w", zipfile.ZIP_STORED) as z:
        z.write(patch_out, patch_out.name)
        z.writestr("README.txt", readme)
    print(f"release: {zip_out} ({zip_out.stat().st_size:,} bytes): {patch_out.name} + README.txt")


if __name__ == "__main__":
    main()
