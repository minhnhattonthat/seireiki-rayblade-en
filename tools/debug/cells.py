"""cells.py: print the text windows' cell chains from a RAM dump (the room a text line really has).

    python -X utf8 tools/debug/cells.py RAM.bin
    (RAM dump: emu.py ... --state-in work/states/<scene>.sstate --frames 30 --script tools/lua/dump_at.lua
     --var DUMP_AT=20  ->  <out>/d000020.ram.bin)

Window table at 0x800CEF40: 48 entries of 60 bytes = 4 cells of 12 bytes {+4 u16 right neighbour (hi = entry,
lo = cell, FFFF none), +6 u16 below neighbour, +8 x in the 64-px buffer, +9 y, +0xA width, +0xB height} then
+0x30 x, +0x32 y (screen), +0x34 flags, +0x38 4bpp buffer pointer. The glyph routine 0x80034530 moves to the
right neighbour when x passes a cell's width; a line's room is the sum of its chain (`w64h16>0401` = a 64x16
cell whose right neighbour is entry 4 cell 1). Past the last cell, glyphs spill into the buffer's next row.
"""
import struct
import sys

BASE = 0x000CEF40


def windows(ram):
    for w in range(48):
        e = ram[BASE + w * 60:BASE + w * 60 + 60]
        x, y, _, buf = struct.unpack_from("<HHII", e, 0x30)
        if not buf:
            continue
        cells = []
        for c in range(4):
            r = e[c * 12:c * 12 + 12]
            right, below = struct.unpack_from("<HH", r, 4)
            if r[10]:
                cells.append(f"w{r[10]}h{r[11]}" + ("" if right == 0xFFFF else f">{right:04X}")
                             + ("" if below == 0xFFFF else f"v{below:04X}"))
        yield w, x, y, sum(e[c * 12 + 10] for c in range(4)), cells


if __name__ == "__main__":
    for w, x, y, total, cells in windows(open(sys.argv[1], "rb").read()):
        print(f"win{w:02d} pos {x},{y} total {total}:", " ".join(cells))
