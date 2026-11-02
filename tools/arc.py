"""arc.py: the D_*.BIN archive format.

Header = N u32 LE self-relative offsets: slot i points at 4*i + off[i]; N*4 = off[0] (slot 0 points just past the
table). Several slots can alias one record (same target). A record runs to the next distinct target (or file end).
Verified: D_SCE slot 1 (0x192C) is the bytes the game loads at RAM 0x800DCE00 (first dialogue scene).

    python -X utf8 tools/arc.py info work/disc/tree/D_SCE.BIN [N]
    python -X utf8 tools/arc.py unpack work/disc/tree/D_SCE.BIN work/unpack/D_SCE     # one file per slot (aliases dup)
"""
import struct
import sys
from pathlib import Path


def targets(data):
    n = struct.unpack_from("<I", data, 0)[0] // 4
    return [4 * i + o for i, o in enumerate(struct.unpack_from(f"<{n}I", data, 0))]


def entries(data):
    """(start, end) per slot; end = next distinct target above start, or file end."""
    t = targets(data)
    uniq = sorted(set(t)) + [len(data)]
    nxt = {s: uniq[i + 1] for i, s in enumerate(uniq[:-1])}
    return [(s, nxt.get(s, len(data))) for s in t]


def pack(data, new_blobs):
    """Rebuild an archive: new_blobs maps slot -> bytes for changed records (aliases follow their record).
    Records keep their original order; 4-byte alignment of every record start is kept."""
    t = targets(data)
    ents = entries(data)
    order = sorted(set(t))
    blob_of = {s: data[s:e] for s, e in ents}
    for slot, b in new_blobs.items():
        blob_of[t[slot]] = b
    out = bytearray(data[:order[0]])
    newpos = {}
    for s in order:
        while len(out) % 4:
            out.append(0)
        newpos[s] = len(out)
        out += blob_of[s]
    for i, s in enumerate(t):
        struct.pack_into("<I", out, 4 * i, newpos[s] - 4 * i)
    return bytes(out)


if __name__ == "__main__":
    cmd, path = sys.argv[1], Path(sys.argv[2])
    data = path.read_bytes()
    ents = entries(data)
    if cmd == "info":
        print(f"{path.name}: {len(ents)} slots, {len(set(ents))} records, size {len(data):#x}")
        for i, (s, e) in enumerate(ents[:int(sys.argv[3]) if len(sys.argv) > 3 else 8]):
            print(f"  {i:4d} {s:#09x} {e - s:#08x} {data[s:s + 16].hex(' ')}")
    elif cmd == "unpack":
        out = Path(sys.argv[3])
        out.mkdir(parents=True, exist_ok=True)
        for i, (s, e) in enumerate(ents):
            (out / f"{i:04d}.bin").write_bytes(data[s:e])
        print(f"{len(ents)} slots -> {out}")
