"""fontsheet.py: render the game's 1bpp dialogue font from the EXE as a labelled sheet.

Font base RAM 0x800AFBCC (EXE file 0xA03CC). Code < 0x200: 16 bytes (8x16, 1 byte/row);
code >= 0x200: 32 bytes (16x16, 2 bytes/row, big-endian bits), at base + code*32 - 0x2000.

    python -X utf8 tools/fontsheet.py OUT.png [first_code] [count] [--zoom N]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "work/disc/tree/SLPS_026.52"
BASE = 0xA03CC  # file offset of RAM 0x800AFBCC


ORDER = [6, 7, 4, 5, 2, 3, 0, 1]  # bit for pixel x: the renderer's nibble tables put bit 2k on the left of bit 2k+1


def glyph(exe, code):
    """Return list of rows (list of 0/1), 16 rows, 8 or 16 wide (verified against the drawn VRAM strip)."""
    if code < 0x200:
        off, n = BASE + code * 16, 1
    else:
        off, n = BASE + code * 32 - 0x2000, 2
    return [[(exe[off + n * r + x // 8] >> ORDER[x % 8]) & 1 for x in range(8 * n)] for r in range(16)]


def sheet(first, count, cols=16, zoom=2):
    exe = EXE.read_bytes()
    cw, ch = 16 * zoom + 2, 16 * zoom + 12
    rows = (count + cols - 1) // cols
    im = Image.new("L", (cols * cw, rows * ch), 255)
    d = ImageDraw.Draw(im)
    for i in range(count):
        code = first + i
        g = glyph(exe, code)
        x0, y0 = (i % cols) * cw, (i // cols) * ch
        d.text((x0, y0), f"{code:03X}", fill=128)
        for y, row in enumerate(g):
            for x, b in enumerate(row):
                if b:
                    d.rectangle([x0 + x * zoom, y0 + 10 + y * zoom, x0 + x * zoom + zoom - 1, y0 + 10 + y * zoom + zoom - 1], fill=0)
    return im


if __name__ == "__main__":
    out = sys.argv[1]
    first = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0
    count = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x100
    zoom = int(sys.argv[sys.argv.index("--zoom") + 1]) if "--zoom" in sys.argv else 2
    sheet(first, count, zoom=zoom).save(out)
    print(out)
