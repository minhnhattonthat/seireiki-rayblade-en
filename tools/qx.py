"""qx.py: the game's image containers (inside LZ records, tools/lz.py), and a static-sweep renderer.

Header: u16 magic, u16 count, count x 16-byte entries {u32 offset, u16 a, u16 b, u16 w, u16 h, i16 x, i16 y},
then u32 ncolors + ncolors x u16 BGR555 CLUT. Pixel data at each entry's offset.
  'QX' 0x5851: 8 bpp, w*h bytes (screens, faces, cut-ins).
  'qX' 0x5871: 4 bpp, w*h/2 bytes, 16-colour palette (a & 0xF) of the shared CLUT (guess: palette field).

    python -X utf8 tools/qx.py sweep D_SYSTEM [D_SCREEN ..]   -> work/gfx/<ARC>/<slot>_<img>.png + sheet_*.png
"""
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arc  # noqa: E402
import lz  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def parse(p):
    magic, count = struct.unpack_from("<HH", p, 0)
    if magic not in (0x5851, 0x5871):
        raise ValueError(f"not QX: {magic:#x}")
    ents = [struct.unpack_from("<IHHHHhh", p, 4 + 16 * i) for i in range(count)]
    cp = 4 + 16 * count
    ncol = struct.unpack_from("<I", p, cp)[0]
    clut = struct.unpack_from(f"<{ncol}H", p, cp + 4)
    return magic, ents, clut


def rgb(c):
    return ((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3)


def render(p):
    magic, ents, clut = parse(p)
    pal = [rgb(c) for c in clut]
    out = []
    for off, a, b, w, h, x, y in ents:
        if w == 0 or h == 0 or w > 1024 or h > 512:
            out.append(None)
            continue
        im = Image.new("RGB", (w, h))
        px = im.load()
        if magic == 0x5851:
            # stored as 32-px-wide column strips, each strip all rows top to bottom (verified on D_SCREEN 323)
            k = off
            for sx in range(0, w, 32):
                sw = min(32, w - sx)
                for j in range(h):
                    for i in range(sw):
                        px[sx + i, j] = pal[p[k]] if k < len(p) and p[k] < len(pal) else (255, 0, 255)
                        k += 1
        else:
            base = (a & 0xF) * 16
            for j in range(h):
                for i in range(w):
                    k = off + (j * w + i) // 2
                    if k >= len(p):
                        continue
                    v = (p[k] >> (4 * (i & 1))) & 15
                    px[i, j] = pal[base + v] if base + v < len(pal) else (v * 17,) * 3
        out.append(im)
    return out


def sweep(name):
    d = (ROOT / f"work/disc/tree/{name}.BIN").read_bytes()
    outdir = ROOT / f"work/gfx/{name}"
    outdir.mkdir(parents=True, exist_ok=True)
    skipped, tiles = [], []
    done = set()
    for slot, (s, e) in enumerate(arc.entries(d)):
        if s in done or e <= s:
            continue
        done.add(s)
        try:
            p = lz.unpack_record(d[s:e])
            ims = render(p)
        except Exception as x:  # noqa: BLE001 - every skip is reported, never dropped silently
            skipped.append(f"{slot}: {x}")
            continue
        for k, im in enumerate(ims):
            if im is None:
                skipped.append(f"{slot}.{k}: bad size")
                continue
            path = outdir / f"{slot:04d}_{k:02d}.png"
            im.save(path)
            tiles.append((f"{slot}.{k}", im))
    # contact sheets: 1024 px wide pages, labelled
    page, x, y, rowh, n = None, 0, 0, 0, 0
    pages = []
    for label, im in tiles:
        im = im if im.width <= 512 else im.resize((512, max(1, im.height * 512 // im.width)))
        if page is None or x + im.width > 1024:
            x, y, rowh = 0, y + rowh + 12, 0
        if page is None or y + im.height + 12 > 1024:
            page = Image.new("RGB", (1024, 1024), (40, 0, 40))
            pages.append(page)
            x, y, rowh = 0, 0, 0
        page.paste(im, (x, y + 10))
        ImageDraw.Draw(page).text((x, y), label, fill=(255, 255, 0))
        x += im.width + 4
        rowh = max(rowh, im.height)
    for i, pg in enumerate(pages):
        pg.save(outdir / f"sheet_{i:02d}.png")
    (outdir / "skipped.txt").write_text("\n".join(skipped) + "\n", encoding="utf-8", newline="\n")
    print(f"{name}: {len(tiles)} images, {len(pages)} sheets, {len(skipped)} skipped (see skipped.txt)")


if __name__ == "__main__":
    if sys.argv[1] == "sweep":
        for n in sys.argv[2:]:
            sweep(n)
