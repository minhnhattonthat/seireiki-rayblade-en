"""vramview.py: render a PCSX-Redux VRAM dump (1024x512 x 16-bit) as PNGs: 15-bit colour, 4bpp and 8bpp index views.

    python -X utf8 tools/vramview.py work/qa/dlg1/d007000.vram.bin [--crop x,y,w,h in 16-bit units]
"""
import sys
from PIL import Image


def main():
    path = sys.argv[1]
    v = open(path, "rb").read()
    x0, y0, w, h = (0, 0, 1024, 512)
    if "--crop" in sys.argv:
        x0, y0, w, h = map(int, sys.argv[sys.argv.index("--crop") + 1].split(","))
    rgb = Image.new("RGB", (w, h))
    i4 = Image.new("L", (w * 4, h))
    i8 = Image.new("L", (w * 2, h))
    for y in range(h):
        row = v[((y0 + y) * 1024 + x0) * 2:((y0 + y) * 1024 + x0 + w) * 2]
        for x in range(w):
            p = row[2 * x] | row[2 * x + 1] << 8
            rgb.putpixel((x, y), ((p & 31) << 3, (p >> 5 & 31) << 3, (p >> 10 & 31) << 3))
            for k in range(4):
                i4.putpixel((4 * x + k, y), ((p >> (4 * k)) & 15) * 17)
            i8.putpixel((2 * x, y), row[2 * x]); i8.putpixel((2 * x + 1, y), row[2 * x + 1])
    base = path.rsplit(".vram.bin", 1)[0]
    rgb.save(base + ".rgb.png"); i4.save(base + ".4bpp.png"); i8.save(base + ".8bpp.png")
    print(base + ".{rgb,4bpp,8bpp}.png")


if __name__ == "__main__":
    main()
