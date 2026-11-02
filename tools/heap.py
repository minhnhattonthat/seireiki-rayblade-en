"""heap.py: the game's heap free list in a RAM dump (or dump one from savestates first).

    python -X utf8 tools/heap.py RAM.bin [RAM.bin..]          # free blocks, total free, largest block
    python -X utf8 tools/heap.py --states story_S01 battle_map # emu.py: load work/states/<name>.sstate, dump RAM

Facts (docs/re/disc.md "Free space / limits"): allocator 0x80036860 (best fit), free 0x800365E8 (addr, size;
coalescing); free list at 0x800D4E58 = 64 x {u32 addr, u32 size}, u16 count at +0x200. Boot seeds it with
free(0x800DCE00, 0xF3200): the heap is 0x800DCE00..0x801D0000, and the scene script buffer (0x8000) is its
first block.
"""
import argparse
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

LIST, HEAP = 0x800D4E58, (0x800DCE00, 0x801D0000)


def free_list(ram):
    base = LIST - 0x80000000
    n = struct.unpack_from("<H", ram, base + 0x200)[0]
    return [struct.unpack_from("<II", ram, base + 8 * i) for i in range(min(n, 64))]


def report(name, ram):
    fl = free_list(ram)
    tot = sum(s for _, s in fl)
    big = max((s for _, s in fl), default=0)
    print(f"{name}: {len(fl)} free blocks, {tot:#x} ({tot // 1024} KB) free, largest {big:#x} ({big // 1024} KB)")
    for a, s in sorted(fl):
        print(f"   {a:08X} {s:#8x}")
    return big


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dumps", nargs="*", type=Path)
    ap.add_argument("--states", nargs="*", default=[])
    ap.add_argument("--cue", default=str(ROOT / "build/Seireiki Rayblade (English).cue"))
    a = ap.parse_args()
    for name in a.states:
        out = ROOT / "work/qa/heap" / name
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), a.cue, "--out", str(out),
                        "--state-in", str(ROOT / f"work/states/{name}.sstate"), "--frames", "30",
                        "--script", str(Path(SKILL) / "scripts/lua/probes/ramdump.lua"), "--var", "RAM_EVERY=20"],
                       check=True, capture_output=True)
        dumps = sorted(out.glob("ram_*.bin"))
        report(name, dumps[-1].read_bytes())
    for d in a.dumps:
        report(d.name, d.read_bytes())


if __name__ == "__main__":
    main()
