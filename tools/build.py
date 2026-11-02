"""build.py: rebuild the disc from the original dump, with this repo's changes, into build/.

    python -X utf8 tools/build.py [--out DIR] [--name NAME]

Steps: check the dump (rom.sha1) -> unpack the disc once (dumpsxiso -> work/disc/tree + layout.xml) -> repack the
text-bearing files (arc.pack per archive; no edits yet, so they come out byte-identical) -> mkpsxiso with a layout
that points changed files at build/files -> split the single .bin back into Track 1 / Track 2 + a 2-file .cue
(same shape as the Redump dump, so the release patch is per-track).
Identity (phase 3): with no edits both tracks equal the original (tests/test_build.py).
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import arc  # noqa: E402
import check_rom  # noqa: E402

MK = ROOT / "tools/mkpsxiso/mkpsxiso-2.30-win64"
CUE = ROOT / "rom/Seireiki Rayblade (Japan).cue"
DISC = ROOT / "work/disc"
TREE = DISC / "tree"
ARCHIVES = ["D_SCE.BIN", "D_BMESS.BIN", "D_SYSTEM.BIN"]  # text lives here (docs/re/text.md); repacked every build


def unpack():
    """dumpsxiso once; the tree is the pristine source every build reads (never written by the build)."""
    if (DISC / "layout.xml").exists() and (TREE / "SLPS_026.52").exists():
        return
    DISC.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(MK / "dumpsxiso.exe"), "-x", str(TREE), "-s", str(DISC / "layout.xml"), str(CUE)],
                   cwd=DISC, check=True, capture_output=True)


def changed_files():
    """name -> bytes for every file the build rewrites. Phase 3: archives repacked with no edits."""
    out = {}
    for name in ARCHIVES:
        out[name] = arc.pack((TREE / name).read_bytes(), {})
    return out


def layout(files_dir, changed):
    """The dumpsxiso layout with source paths absolute (cwd-free) and changed files pointed at files_dir."""
    xml = (DISC / "layout.xml").read_text(encoding="utf-8")
    xml = re.sub(r'(source|file)="tree/', lambda m: f'{m[1]}="{TREE.as_posix()}/', xml)
    xml = xml.replace('source="tree"', f'source="{TREE.as_posix()}"')
    for name in changed:
        pat = f'<file name="{name}" '
        assert xml.count(pat) == 1, name
        xml = xml.replace(pat, f'{pat}source="{(files_dir / name).as_posix()}" ')
    return xml


def split(img, cue_text, out, name):
    """mkpsxiso writes one .bin; cut it at track 2's INDEX 00 into the Redump 2-file shape."""
    mm, ss, ff = map(int, re.search(r"TRACK 02 AUDIO\s+INDEX 00 (\d+):(\d+):(\d+)", cue_text).groups())
    cut = ((mm * 60 + ss) * 75 + ff) * 2352
    t1, t2 = out / f"{name} (Track 1).bin", out / f"{name} (Track 2).bin"
    with open(img, "rb") as f, open(t2, "wb") as g:
        f.seek(cut)
        shutil.copyfileobj(f, g, 1 << 22)
    with open(img, "r+b") as f:
        f.truncate(cut)
    img.replace(t1)
    cue = out / f"{name}.cue"
    cue.write_text(f'FILE "{t1.name}" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n'
                   f'FILE "{t2.name}" BINARY\n  TRACK 02 AUDIO\n    INDEX 00 00:00:00\n    INDEX 01 00:02:00\n',
                   encoding="utf-8", newline="\n")
    return cue, t1, t2


def build(out=ROOT / "build", name="Seireiki Rayblade (English)", changed=None):
    check_rom.check()
    unpack()
    out = Path(out)
    files_dir = out / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    changed = changed_files() if changed is None else changed
    for fn, data in changed.items():
        (files_dir / fn).write_bytes(data)
    (out / "layout.xml").write_text(layout(files_dir, changed), encoding="utf-8", newline="\n")
    img, tmpcue = out / "_disc.bin", out / "_disc.cue"
    r = subprocess.run([str(MK / "mkpsxiso.exe"), "-y", "-q", "-o", str(img), "-c", str(tmpcue),
                        "-lba", str(out / "lba.txt"), str(out / "layout.xml")], cwd=out, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"mkpsxiso failed:\n{r.stdout}{r.stderr}")
    cue_text = tmpcue.read_text()
    tmpcue.unlink()
    return split(img, cue_text, out, name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT / "build"))
    ap.add_argument("--name", default="Seireiki Rayblade (English)")
    a = ap.parse_args()
    cue, t1, t2 = build(a.out, a.name)
    print(f"built {cue}")
