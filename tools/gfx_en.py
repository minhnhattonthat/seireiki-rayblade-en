"""gfx_en.py: English redraws of Japanese drawn as graphics (docs/re/graphics.md), for insert.changes().

Images are qX (4 bpp) entries inside LZ records of D_SYSTEM (tools/qx.py). A redraw keeps each image's size,
palette and VRAM placement and only rewrites its pixels, so nothing about the layout changes.

Chapter cards (G8/G9): `第 N 話` is three images (第, digits, 話) and the title 「…」 one image per title with a furigana
strip after it (D_SYSTEM 17-20: title t = slot 17 + t // 20, images 2 (t % 20) and +1). The English title is
bank10's (the same text the save/intermission screens show), drawn in Liberation Sans Bold without antialiasing:
black core (index 15) and a 1-px light ring (index 2), the card's own look. 第 -> "Ep.", 話 and the strips blank.
Titles 17 and 47 are set by no scene and 61-67 are "シナリオ" placeholders: left as they are.

    python -X utf8 tools/gfx_en.py preview OUT_DIR     # every redrawn image as PNG (x3) beside the original
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import arc  # noqa: E402
import lz  # noqa: E402
import qx  # noqa: E402

TREE = ROOT / "work/disc/tree"
FONT = ROOT / "fonts/LiberationSans-Bold.ttf"
CORE, RING = 15, 2
CARD_SLOTS = range(17, 21)
UNUSED_TITLES = {17, 47} | set(range(61, 68))
EP_SLOT, EP_IMG, WA_IMG = 16, 6, 7          # 第 and 話 (24x24); digits 0-9 are images 8-17, already Arabic


def text_mask(text, w, h, max_size=17, min_size=10):
    """rows of 0/1: `text` centred in w x h, the largest size whose ink (plus the 1-px ring) fits."""
    for size in range(max_size, min_size - 1, -1):
        f = ImageFont.truetype(str(FONT), size)
        x0, y0, x1, y1 = f.getbbox(text)
        if x1 - x0 + 2 <= w and f.getbbox("Hg")[3] - f.getbbox("H")[1] + 2 <= h:
            break
    else:
        raise ValueError(f"{text!r} does not fit {w}x{h}")
    im = Image.new("1", (w, h), 0)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    cap_top, desc = f.getbbox("H")[1], f.getbbox("Hg")[3]
    y = (h - (desc - cap_top)) // 2 - cap_top
    d.text(((w - (x1 - x0)) // 2 - x0, y), text, font=f, fill=1)
    return [[im.getpixel((i, j)) for i in range(w)] for j in range(h)]


def outlined(mask):
    """index rows: CORE on the mask, RING on its 8-neighbourhood, 0 elsewhere."""
    h, w = len(mask), len(mask[0])
    out = [[0] * w for _ in range(h)]
    for j in range(h):
        for i in range(w):
            if mask[j][i]:
                out[j][i] = CORE
            elif any(mask[y][x] for y in range(max(0, j - 1), min(h, j + 2)) for x in range(max(0, i - 1), min(w, i + 2))):
                out[j][i] = RING
    return out


def put4(rec, ent, rows):
    """write index rows into a qX entry's 4-bpp pixels (low nibble = left pixel)."""
    off, _, _, w, h, _, _ = ent
    assert len(rows) == h and all(len(r) == w for r in rows) and w % 2 == 0
    for j in range(h):
        for i in range(0, w, 2):
            rec[off + (j * w + i) // 2] = rows[j][i] | rows[j][i + 1] << 4


def card_titles():
    """{title index: English} from bank10 (id bank10:XXX = title XXX)."""
    bank = json.loads((ROOT / "script/exe_bank.json").read_text(encoding="utf-8"))
    return {int(e["id"][7:], 16): e["en"] for e in bank if e["id"].startswith("bank10:") and e.get("en")}


def images():
    """{(slot, image): index rows} for every redrawn image."""
    out = {(EP_SLOT, EP_IMG): outlined(text_mask("Ep.", 24, 24)), (EP_SLOT, WA_IMG): [[0] * 24 for _ in range(24)]}
    data = (TREE / "D_SYSTEM.BIN").read_bytes()
    ents = arc.entries(data)
    for t, en in card_titles().items():
        if t in UNUSED_TITLES:
            continue
        slot, k = CARD_SLOTS[0] + t // 20, 2 * (t % 20)
        s, e = ents[slot]
        _, qents, _ = qx.parse(lz.unpack_record(data[s:e]))
        _, _, _, w, h, x, _ = qents[k]
        _, _, _, rw, rh, rx, _ = qents[k + 1]
        if rh == h and rx == x - w:
            # a long title runs on into the second image, drawn right after the first (left = anchor - x)
            rows = outlined(text_mask(en, w + rw, h))
            out[(slot, k)], out[(slot, k + 1)] = [r[:w] for r in rows], [r[w:] for r in rows]
        else:                                          # furigana strip or a blank piece
            out[(slot, k)] = outlined(text_mask(en, w, h))
            out[(slot, k + 1)] = [[0] * rw for _ in range(rh)]
    return out


def records():
    """{D_SYSTEM slot: new LZ record} for build (insert.changes)."""
    data = (TREE / "D_SYSTEM.BIN").read_bytes()
    ents = arc.entries(data)
    by_slot = {}
    for (slot, k), rows in images().items():
        by_slot.setdefault(slot, {})[k] = rows
    out = {}
    for slot, ims in by_slot.items():
        s, e = ents[slot]
        rec = bytearray(lz.unpack_record(data[s:e]))
        magic, qents, _ = qx.parse(rec)
        assert magic == 0x5871, slot
        for k, rows in ims.items():
            put4(rec, qents[k], rows)
        out[slot] = lz.pack_record(bytes(rec))
        assert lz.unpack_record(out[slot]) == rec, slot
    return out


def preview(outdir):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    data = (TREE / "D_SYSTEM.BIN").read_bytes()
    new = arc.pack(data, records())
    tiles = []
    for (slot, k) in sorted(images()):
        for src in (data, new):
            s, e = arc.entries(src)[slot]
            im = qx.render(lz.unpack_record(src[s:e]))[k]
            tiles.append(im.resize((im.width * 3, im.height * 3), Image.NEAREST))
    W = max(t.width for t in tiles)
    sheet = Image.new("RGB", (W * 2 + 8, sum(t.height + 4 for t in tiles[::2])), (255, 0, 255))
    y = 0
    for a, b in zip(tiles[::2], tiles[1::2]):
        sheet.paste(a, (0, y))
        sheet.paste(b, (W + 8, y))
        y += a.height + 4
    sheet.save(outdir / "cards.png")
    print(f"{len(tiles) // 2} images -> {outdir / 'cards.png'}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["preview"]:
        preview(sys.argv[2])
    else:
        print(__doc__)
