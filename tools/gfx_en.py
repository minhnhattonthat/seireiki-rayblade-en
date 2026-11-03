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


# World-map place labels (G5, D_SYSTEM 8.17-8.26): 16 px tall, light fill (index 1) with a dark drop shadow
# (index 3). The images sit packed in VRAM, so their widths are fixed: drawn with the game's own English pixel font
# (font_en art, 1-px gaps), or, when that is too wide, a 3x5 capital font on one or two lines.
MAP_SLOT, FILL, SHADOW = 8, 1, 3
MAP_LABELS = {17: "Flamuelk Castle", 18: "Shangria", 19: "Brandenkrois", 20: "Berta", 21: "Glascher Valley",
              22: "Alterias Valley", 23: "Muur Forest", 24: "Ze=Ode Lab Ruins", 25: "Cornel Village",
              26: "Holy Land"}
TINY = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ=-", (
    ".#./#.#/###/#.#/#.#", "##./#.#/##./#.#/##.", ".##/#../#../#../.##", "##./#.#/#.#/#.#/##.", "###/#../##./#../###",
    "###/#../##./#../#..", ".##/#../#.#/#.#/.##", "#.#/#.#/###/#.#/#.#", "###/.#./.#./.#./###", "..#/..#/..#/#.#/.#.",
    "#.#/#.#/##./#.#/#.#", "#../#../#../#../###", "#.#/###/###/#.#/#.#", "##./#.#/#.#/#.#/#.#", ".#./#.#/#.#/#.#/.#.",
    "##./#.#/##./#../#..", ".#./#.#/#.#/##./.##", "##./#.#/##./#.#/#.#", ".##/#../.#./..#/##.", "###/.#./.#./.#./.#.",
    "#.#/#.#/#.#/#.#/###", "#.#/#.#/#.#/#.#/.#.", "#.#/#.#/###/###/#.#", "#.#/#.#/.#./#.#/#.#", "#.#/#.#/.#./.#./.#.",
    "###/..#/.#./#../###", ".../###/.../###/...", ".../.../###/.../...")))
TINY["I"] = "#/#/#/#/#"


def tiny_mask(text, w, h, top):
    """rows of 0/1: text in the 3x5 capitals, centred across w, cap top at row `top`."""
    placed, lw = _glyph_run(text.upper(), lambda c: TINY[c].split("/"), 2)
    if lw > w:
        raise ValueError(f"{text!r} is {lw} px, room {w}")
    mask = [[0] * w for _ in range(h)]
    x0 = (w - lw) // 2
    for x, rows in placed:
        for j, r in enumerate(rows):
            for i, c in enumerate(r):
                if c == "#":
                    mask[top + j][x0 + x + i] = 1
    return mask


def read4(rec, ent):
    off, _, _, w, h, _, _ = ent
    return [[(rec[off + (j * w + i) // 2] >> (4 * (i & 1))) & 15 for i in range(w)] for j in range(h)]


# Character name plates (G4, D_SYSTEM 2.35-68, 32x16): white (1) with a dark 8-neighbour outline (2), rows 7-14.
PLATE_SLOT = 2
PLATES = dict(zip(range(35, 69), (
    "Lodis", "Roa", "Ymir", "Ai", "Kasumi", "Clovis", "Xiujian", "Fain", "Arthur", "Melissa", "Celica", "Gen",
    "Kururu", "Melvi", "Gabon", "Miyasco", "Bart", "Baren", "Derock", "Sisk", "Rosalie", "Maki", "Leone", "Rayfon",
    "Rishuna", "Yamato", "Aurelie", "Alforina", "Garyud", "Reduce", "Ciel", "Valga", "Cain", "Grad")))
# Trust gauge (G7, D_SYSTEM 13): header 信頼度ゲージ (13.0) and the heroines' plates (13.2-16): white (2) with a dark
# shadow (1) one row down on the plate colour (7); the old letters are painted over with each row's plate colour.
GAUGE_SLOT = 13
GAUGE = {0: "Trust Gauge", **dict(zip(range(2, 17), (
    "Ai", "Ymir", "Kasumi", "Xiujian", "Clovis", "Fain", "Rosalie", "Gen", "Aurelie", "Arthur", "Melvi", "Leone",
    "Kururu", "Melissa", "Celica")))}


def plate_rows(text, w, h):
    mask = tiny_mask(text, w - 2, h, 8)
    mask = [[0] + r + [0] for r in mask]
    out = [[0] * w for _ in range(h)]
    for j in range(h):
        for i in range(w):
            if mask[j][i]:
                out[j][i] = 1
            elif any(mask[y][x] for y in range(max(0, j - 1), min(h, j + 2)) for x in range(max(0, i - 1), min(w, i + 2))):
                out[j][i] = 2
    return out


def gauge_rows(orig, text, k):
    """repaint the letter box with the plate colour of a clean column, then the text with its shadow."""
    rows = [r[:] for r in orig]
    if k == 0:      # header: an inner box with 9/5 rules the letters overlap: each row gets its own commonest colour
        x0, x1, y0, y1, top = 10, 72, 4, 14, 6
        for j in range(y0, y1):
            vals = [v for v in orig[j][x0:x1] if v not in (1, 2)]
            fill = max(set(vals), key=vals.count)
            for i in range(x0, x1):
                rows[j][i] = fill
    else:           # plate: letters (1, 2) sit on plain plate colour 7; the slanted edge stays
        x0, x1, y0, y1, top = 9, 43, 2, 11, 3
        for j in range(y0, y1):
            for i in range(x0, x1):
                if rows[j][i] in (1, 2):
                    rows[j][i] = 7
    mask = tiny_mask(text, x1 - x0, len(rows), top)
    for j in range(len(rows)):
        for i in range(x1 - x0):
            if mask[j][i]:
                rows[j][x0 + i] = 2
                if j + 1 < len(rows) and not mask[j + 1][i]:
                    rows[j + 1][x0 + i] = 1
    return rows


# Battle (G2/G3, D_SYSTEM 0/1): popup labels (1.89-95, 1.107) are metal lettering, each row one colour from light
# (7) down to dark (4), checkered between bands, with a dark (8) edge right and below. AI-order icons (x.58-62)
# carry one light (7) letter in their box; the Prana label (x.57) is white (1) with a black (8) edge.
BATTLE = {89: "Critical", 90: "Evade", 91: "Defend", 92: "Plasma Coating", 93: "Plasma Barrier",
          94: "Ballistic Barrier", 95: "Special Field", 107: "Barrier"}
METAL = (7, 7, 7, 7, 7, 7, 7, 71, 17, 1, 12, 2, 23, 3, 34, 4)     # by row; two digits = checkered pair
ORDERS = dict(zip(range(58, 63), "MCASD"))                          # Manual Counter Aggressive Safe Defend (bank00:0AE)


def bold_mask(text, w, h, cap=13, min_cap=7, min_scale=0.72):
    """rows of 0/1: Liberation Sans Bold, cap height as big as fits (squeezed down to min_scale), descenders kept
    inside h, centred across w with a 1-px margin right and below for the edge."""
    for size in range(40, 6, -1):
        f = ImageFont.truetype(str(FONT), size)
        top, base = f.getbbox("H")[1], f.getbbox("H")[3]
        desc = f.getbbox("g")[3] - base if any(c in "gjpqy" for c in text) else 0
        x0, _, x1, _ = f.getbbox(text)
        if base - top <= cap and base - top + desc <= h - 2 and (x1 - x0) * min_scale <= w - 1:
            break
    if base - top < min_cap:
        raise ValueError(f"{text!r} does not fit {w}x{h}")
    im = Image.new("L", (x1 - x0, h), 0)
    y = (h - 1 - (base - top + desc)) // 2 - top    # ink centred in rows 0..h-2 (the last row is for the edge)
    ImageDraw.Draw(im).text((-x0, y), text, font=f, fill=255)
    if im.width > w - 1:
        im = im.resize((w - 1, h), Image.LANCZOS)
    x = (w - 1 - im.width) // 2
    return [[1 if i - x in range(im.width) and im.getpixel((i - x, j)) >= 110 else 0 for i in range(w)]
            for j in range(h)]


def edged(mask, fill, edge):
    """index rows: fill(j, i) on the mask, `edge` on the pixels right of / below / diagonal to ink."""
    h, w = len(mask), len(mask[0])
    out = [[0] * w for _ in range(h)]
    for j in range(h):
        for i in range(w):
            if mask[j][i]:
                out[j][i] = fill(j, i)
            elif any(mask[j - dy][i - dx] for dy, dx in ((0, 1), (1, 0), (1, 1)) if j >= dy and i >= dx):
                out[j][i] = edge
    return out


def metal(j, i):
    v = METAL[min(j, 15)]
    return v if v < 10 else (v // 10, v % 10)[(i + j) & 1]


def order_icon(orig, letter):
    """repaint the box interior (10x12 inside the 16x16 icon's bevel) and set one game-font letter in it."""
    import font_en
    rows = [r[:] for r in orig]
    left = next(i for i in range(16) if orig[1][i] in (3, 4))      # bevel's left column (icons sit at x 0 or 1)
    for j in range(2, 14):
        for i in range(left + 1, left + 11):
            rows[j][i] = 5
    g = font_en.rows(letter)
    x0, y0 = left + 1 + (10 - len(g[0])) // 2, 3
    for j, r in enumerate(g):
        for i, c in enumerate(r):
            if c == "#":
                rows[y0 + j][x0 + i] = 7
    return rows


def _glyph_run(text, art, space):
    """[(x, rows)] for text set with 1-px gaps; returns (placements, width)."""
    x, out = 0, []
    for ch in text:
        if ch == " ":
            x += space
            continue
        rows = art(ch)
        out.append((x, rows))
        x += len(rows[0]) + 1
    return out, x - 1


def label_rows(text, w, h):
    """index rows for a map label: FILL text with a SHADOW one px down-right, centred in w x h."""
    import font_en
    big = _glyph_run(text, lambda c: font_en.rows(c), 3)
    small1 = _glyph_run(text.upper(), lambda c: TINY[c].split("/"), 2)
    words = text.upper().split(" ")
    cut = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))), default=1)
    small2 = [_glyph_run(" ".join(p), lambda c: TINY[c].split("/"), 2) for p in (words[:cut], words[cut:])]
    if big[1] + 1 <= w:
        lines, top = [big], font_en.TOP - 1         # cap top as the Japanese glyphs (row 3 of 16)
    elif small1[1] + 1 <= w:
        lines, top = [small1], 5
    elif len(words) > 1 and max(r[1] for r in small2) + 1 <= w:
        lines, top = small2, 2
    else:
        raise ValueError(f"map label {text!r} does not fit {w} px")
    mask = [[0] * w for _ in range(h)]
    for n, (placed, lw) in enumerate(lines):
        x0, y0 = (w - lw - 1) // 2, top + n * 7
        for x, rows in placed:
            for j, r in enumerate(rows):
                for i, c in enumerate(r):
                    if c == "#":
                        mask[y0 + j][x0 + x + i] = 1
    out = [[0] * w for _ in range(h)]
    for j in range(h):
        for i in range(w):
            if mask[j][i]:
                out[j][i] = FILL
            elif j and i and mask[j - 1][i - 1]:
                out[j][i] = SHADOW
    return out


# Staff credits (G13, D_SYSTEM 472.21-83): white text, antialiased into the image's 16-level grey ramp. Roles and
# the 35 name readings come from the Dreamcast fan translation's sourced credit list (D2: earlier fan patch); the 7
# names it could not source a reading for stay Japanese (docs/status.md, waiting on the owner).
CREDITS_SLOT = 472
CREDITS = {
    21: "Executive Producer", 22: "Chief Director", 23: "Director", 24: "Co-Director", 25: "Script",
    26: "Character Design & Original Art", 27: "Mechanical Design", 28: "Sound", 29: "Programming",
    30: "Scenario Data", 31: "Animation Data", 32: "Character Graphics", 33: "Unit Graphics", 34: "Effect Graphics",
    35: "Background Art", 36: "Battle Maps", 37: "CG Movies", 38: "Lead Mech Design",
    39: "Special Thanks", 40: "Planning & Production", 41: "Winky Soft Co., Ltd.",
    42: "Shigemitsu Takamiya", 43: "Kenichiro Matsumoto", 44: "Atsushi Kamata", 45: "Masahiro Sho", 46: "Toru Abe",
    47: "Kazuyoshi Horikawa", 48: "Takeshi Shimoyama", 49: "Koji Kurosumi", 50: "Tatsuya Fujiwara",
    51: "Yoshihiro Inada", 53: "Yoshinori Tokumura", 54: "Ryohei Inaoka", 55: "Akinori Yoshioka",
    56: "Motoyoshi Iwatsuru", 57: "Yoshiharu Buma", 58: "Koji Kikuchi", 59: "Kayoko Miyashita", 60: "Takako Nakata",
    61: "Naoya Inui", 63: "Atsuki Toda", 64: "Hiroyuki Fukuda", 65: "Hirotaka Okuda", 66: "Hiromasa Morishige",
    67: "Masato Nakamura", 68: "Shujiro Nakade", 69: "Wataru Yoshida", 70: "Naoki Nakashiba", 71: "Fumie Itosu",
    73: "Yoshiyasu Nakata", 74: "Hirofumi Ichikawa", 75: "Kayo Buma", 77: "Yoshiko Hotada", 78: "Momoko Suzuki",
    79: "Masahiko Iwasaki", 82: "Kenya Mizuno",
}
CREDITS_UNSOURCED = {52: "草開 一也", 62: "伊藤 健", 72: "須磨 敦史", 76: "内方 智士", 80: "?", 81: "?", 83: "?"}


def aa_rows(text, w, h, clut16, size=13, min_scale=0.6):
    """index rows: `text` antialiased (white on transparent) into the 16-colour ramp `clut16` (index 0 = clear),
    squeezed horizontally to fit w - 2 when needed (down to min_scale, then a smaller size)."""
    lum = [((c & 31) + (c >> 5 & 31) + (c >> 10 & 31)) / 93 for c in clut16]
    while True:
        f = ImageFont.truetype(str(FONT), size)
        x0, _, x1, _ = f.getbbox(text)
        cap_top, base = f.getbbox("H")[1], f.getbbox("H")[3]
        tw = x1 - x0
        if tw * min_scale <= w - 2 or size <= 8:
            break
        size -= 1
    im = Image.new("L", (tw + 2, h), 0)
    ImageDraw.Draw(im).text((1 - x0, (h - (base - cap_top)) // 2 - cap_top), text, font=f, fill=255)
    if im.width > w:
        im = im.resize((w, h), Image.LANCZOS)
    canvas = Image.new("L", (w, h), 0)
    canvas.paste(im, ((w - im.width) // 2, 0))
    ramp = range(1, 16)
    out = []
    for j in range(h):
        row = []
        for i in range(w):
            v = canvas.getpixel((i, j)) / 255
            row.append(0 if v < 0.15 else min(ramp, key=lambda k: abs(lum[k] - v)))
        out.append(row)
    return out


# Album thumbnails (G11, D_SYSTEM 36, 49-51, 56-58, 64-78; 8 bpp, 64x72): a photo over a light caption box with
# dark text, left-aligned. English (docs/album-captions.tsv, read off the images) is antialiased between the box
# colour and the darkest caption grey, each level mapped to the nearest colour of the image's own palette.
ALBUM_SLOTS = (36, 49, 50, 51, 56, 57, 58, *range(64, 79))


def album_captions():
    rows = (ROOT / "docs/album-captions.tsv").read_text(encoding="utf-8").splitlines()[1:]
    return {tuple(map(int, r.split("\t")[0].split("."))): r.split("\t")[2] for r in rows if r.strip()}


def caption_rows(orig, pal, text):
    """orig: index rows of the image; returns them with the caption box repainted and `text` set in it."""
    h, w = len(orig), len(orig[0])
    bg = orig[h - 2][2]
    top = next(j for j in range(h // 2, h) if all(v == bg for v in orig[j]))
    room_w, room_h = w - 5, h - top - 2
    rgb = [((c & 31), (c >> 5 & 31), (c >> 10 & 31)) for c in pal]     # for the darkest-grey pick below
    for max_lines, size in [(n, s) for n in (2, 3) for s in range(11, 7, -1)]:     # two lines if any size allows
        f = ImageFont.truetype(str(FONT), size)
        lines = []
        for word in text.split(" "):
            if lines and f.getlength(lines[-1] + " " + word) <= room_w:
                lines[-1] += " " + word
            else:
                lines.append(word)
        pitch = size - 1
        # a single long word (a mech name) may be squeezed to 80%
        if len(lines) <= max_lines and len(lines) * pitch + 2 <= room_h and all(f.getlength(ln) <= room_w / (0.8 if " " not in ln else 1)
                                                    for ln in lines):
            break
    else:
        raise ValueError(f"album caption {text!r} does not fit {room_w}x{room_h}")
    im = Image.new("L", (w, room_h), 0)
    cap_top = f.getbbox("H")[1]
    pad = max(1, min(3, room_h - len(lines) * pitch - 1))
    for n, ln in enumerate(lines):
        line = Image.new("L", (int(f.getlength(ln)) + 2, pitch + 3), 0)
        ImageDraw.Draw(line).text((0, -cap_top), ln, font=f, fill=255)
        if line.width > room_w:
            line = line.resize((room_w, line.height), Image.LANCZOS)
        im.paste(line, (3, pad + n * pitch))
    ink = min({v for r in orig[top:] for v in r}, key=lambda k: sum(rgb[k]))     # the Japanese text's darkest grey
    out = [r[:] for r in orig]
    for j, row in enumerate(blend(im, pal, bg, ink)):
        out[top + 1 + j] = [v if 2 <= i < w - 2 else bg for i, v in enumerate(row)]
    return out


def blend(im, pal, bg, ink):
    """index rows for an "L" image of antialiased text: each level -> the palette colour nearest bg..ink mixed."""
    rgb = [((c & 31), (c >> 5 & 31), (c >> 10 & 31)) for c in pal]
    cache = {}
    rows = []
    for j in range(im.height):
        row = []
        for i in range(im.width):
            v = im.getpixel((i, j))
            if v not in cache:
                t = v / 255
                want = [a * (1 - t) + b * t for a, b in zip(rgb[bg], rgb[ink])]
                cache[v] = bg if v < 40 else min(range(len(pal)), key=lambda k: sum((x - y) ** 2 for x, y in zip(rgb[k], want)))
            row.append(cache[v])
        rows.append(row)
    return rows


# Memory album screen (G10, D_SYSTEM 33.0, 320x240 8 bpp, linear rows despite w > 128): the red 思い出アルバム on the
# cream tag becomes "Memory Album"; the book cover's lettering is decorative fantasy script and stays.
ALBUM_TAG = (33, 0, (113, 22, 226, 40), "Memory Album")


def album_tag(rec, ent, pal):
    """{offset: index} pixel writes for the tag."""
    off, _, _, w, h, _, _ = ent
    x0, y0, x1, y1 = ALBUM_TAG[2]
    px = {(x, y): rec[off + y * w + x] for x in range(x0, x1) for y in range(y0, y1)}
    rgb = [((c & 31), (c >> 5 & 31), (c >> 10 & 31)) for c in pal]
    bg = max(set(px.values()), key=list(px.values()).count)
    ink = max(set(px.values()), key=lambda k: rgb[k][0] - rgb[k][1] - rgb[k][2])     # the reddest
    tw, th = x1 - x0, y1 - y0
    for size in range(16, 9, -1):
        f = ImageFont.truetype(str(FONT), size)
        if f.getlength(ALBUM_TAG[3]) <= tw - 2 and f.getbbox("H")[3] - f.getbbox("H")[1] <= th - 4:
            break
    im = Image.new("L", (tw, th), 0)
    top, base = f.getbbox("H")[1], f.getbbox("H")[3]
    ImageDraw.Draw(im).text(((tw - f.getlength(ALBUM_TAG[3])) // 2, (th - (base - top)) // 2 - top), ALBUM_TAG[3],
                            font=f, fill=255)
    return {off + (y0 + j) * w + x0 + i: v for j, r in enumerate(blend(im, pal, bg, ink)) for i, v in enumerate(r)}


def read8(rec, ent):
    off, _, _, w, h, _, _ = ent
    return [list(rec[off + j * w:off + (j + 1) * w]) for j in range(h)]


# New Year card (G12, D_SYSTEM 110.0, 320x224 8 bpp linear): the handwritten あけまして/おめでとうございます (pink, orange
# marker outline) becomes "Happy / New Year!"; 年 after "2000" is cleared, "2000" and the heart stay.
NEW_YEAR = 110
NY_CLEAR = [(92, 2, 213, 52), (213, 2, 232, 20)]
NY_KEEP = (178, 2, 214, 17)                         # "2000"
NY_LINES = [("Happy", 98, 4, 17), ("New Year!", 98, 25, 20)]       # text, x, y, size


def new_year(rec, ent, pal):
    """{offset: index} pixel writes for the card."""
    off, _, _, w, h, _, _ = ent
    rgb = [((c & 31), (c >> 5 & 31), (c >> 10 & 31)) for c in pal]
    keep = lambda x, y: NY_KEEP[0] <= x < NY_KEEP[2] and NY_KEEP[1] <= y < NY_KEEP[3]
    area = [(x, y) for x0, y0, x1, y1 in NY_CLEAR for x in range(x0, x1) for y in range(y0, y1) if not keep(x, y)]
    used = [rec[off + y * w + x] for x, y in area]
    paper = max(set(used), key=used.count)
    pink = max(set(used), key=lambda k: rgb[k][0] + rgb[k][2] - 2 * rgb[k][1])
    orange = max(set(used), key=lambda k: rgb[k][0] - rgb[k][2] + (rgb[k][1] > 10) * 10)
    core = Image.new("1", (w, h), 0)
    d = ImageDraw.Draw(core)
    d.fontmode = "1"
    for text, x, y, size in NY_LINES:
        f = ImageFont.truetype(str(FONT), size)
        d.text((x, y - f.getbbox("H")[1]), text, font=f, fill=1)
    writes = {}
    for x, y in area:               # only ink (saturated or dark) goes: the paper's own speckle stays
        c = rgb[rec[off + y * w + x]]
        if max(c) - min(c) > 2 or sum(c) < 80:
            writes[off + y * w + x] = paper
    for y in range(0, 56):                          # the lettering's box plus the outline
        for x in range(88, 236):
            if core.getpixel((x, y)):
                writes[off + y * w + x] = pink
            elif any(core.getpixel((x + dx, y + dy)) for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)
                     if 0 <= x + dx < w and 0 <= y + dy < h and abs(dx) + abs(dy) <= 3):
                writes[off + y * w + x] = orange
    return writes


# Attack cut-in 破 (G18, D_EFFECT 142/143/455/456, images 8 = white core + red glow + black halo, 9 = its yellow
# trail; 455/456 hold it mirrored for the other facing): "BREAK", as the Dreamcast fan patch did (D2). Each pixel's
# index is the one whose pixels in the original lie, on average, at the same ring distance from the core.
CUTIN_SLOTS = (142, 143, 455, 456)
CUTIN_TEXT = "BREAK"


def rings(core, maxd):
    """ring distance (3x3 steps) of every pixel from a "1" image's set pixels; maxd + 1 beyond."""
    import numpy as np
    cur = np.array(core, dtype=bool)
    dist = np.full(cur.shape, maxd + 1)
    for k in range(maxd + 1):
        dist[cur & (dist > k)] = k
        p = np.pad(cur, 1)
        steps = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)] + ([(-1, -1), (-1, 1), (1, -1), (1, 1)] if k % 2 else [])
        cur = np.logical_or.reduce([p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy, dx in steps])
    return dist.tolist()          # alternating 4- and 8-neighbour steps: octagonal rings, close to round


def cutin_rows(orig, pal, mirror, trail=False):
    """frame 8 (trail=False): each index placed at its mean ring distance from the core in the original;
    frame 9 (the trail): the text blurred, brightness mapped onto the ramp, ringed by the dark halo."""
    from PIL import ImageFilter
    h, w = len(orig), len(orig[0])
    lum = [sum(qx.rgb(c)) for c in pal]
    used = {v for r in orig for v in r} - {0}
    dark = min(used, key=lambda v: lum[v])
    pts = [(i, j) for j in range(h) for i in range(w) if orig[j][i] not in (0, dark)]
    cx, cy = sum(p[0] for p in pts) // len(pts), sum(p[1] for p in pts) // len(pts)
    f = ImageFont.truetype(str(FONT), 40)
    x0, y0, x1, y1 = f.getbbox(CUTIN_TEXT)
    txt = Image.new("1", (x1 - x0 + 16, y1 - y0 + 4), 0)
    ImageDraw.Draw(txt).text((8 - x0, 2 - y0), CUTIN_TEXT, font=f, fill=1)
    txt = txt.transform(txt.size, Image.AFFINE, (1, 0.25, -6, 0, 1, 0))         # slant like a brush stroke
    if mirror:
        txt = txt.transpose(Image.FLIP_LEFT_RIGHT)
    new = Image.new("1", (w, h), 0)
    margin = 20
    new.paste(txt, (min(max(cx - txt.width // 2, margin), w - txt.width - margin),
                    min(max(cy - txt.height // 2, margin), h - txt.height - margin)))
    if trail:
        glow = new.convert("L").filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(4))
        glow = [(g / 255) ** 0.6 * 255 for g in glow.getdata()]
        peak = max(glow) or 1
        ramp = sorted(used - {dark}, key=lambda v: lum[v])
        halo = rings(new, 14)
        return [[ramp[min(len(ramp) - 1, int(g / peak * len(ramp)))] if g / peak > 0.06
                 else dark if halo[j][i] <= 14 else 0
                 for i, g in enumerate(glow[j * w:(j + 1) * w])] for j in range(h)]
    top = max(used, key=lambda v: lum[v])
    core = Image.new("1", (w, h), 0)
    core.putdata([v == top for r in orig for v in r])
    d0 = rings(core, 90)
    sums = {}
    for j in range(h):
        for i in range(w):
            if orig[j][i]:
                sums.setdefault(orig[j][i], []).append(d0[j][i])
    prof = {v: sum(ds) / len(ds) for v, ds in sums.items()}
    reach = max(d0[j][i] for j in range(h) for i in range(w) if orig[j][i])
    d1 = rings(new, reach)
    order = sorted(prof, key=prof.get)
    return [[0 if d1[j][i] > reach else min(order, key=lambda v: abs(prof[v] - d1[j][i])) for i in range(w)]
            for j in range(h)]


def effect_records():
    """{D_EFFECT slot: new LZ record} for the cut-ins (slot 250 = D_SYSTEM 1's copy is added by insert.changes)."""
    data = (TREE / "D_EFFECT.BIN").read_bytes()
    ents = arc.entries(data)
    out = {}
    for slot in CUTIN_SLOTS:
        s, e = ents[slot]
        rec = bytearray(lz.unpack_record(data[s:e]))
        _, qents, clut = qx.parse(rec)
        for k in (8, 9):
            base = (qents[k][1] & 0xF) * 16
            put4(rec, qents[k], cutin_rows(read4(rec, qents[k]), clut[base:base + 16], slot >= 455, trail=k == 9))
        out[slot] = lz.pack_record(bytes(rec))
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
    s, e = ents[MAP_SLOT]
    _, qents, _ = qx.parse(lz.unpack_record(data[s:e]))
    for k, en in MAP_LABELS.items():
        out[(MAP_SLOT, k)] = label_rows(en, qents[k][3], qents[k][4])
    s, e = ents[PLATE_SLOT]
    _, qents, _ = qx.parse(lz.unpack_record(data[s:e]))
    for k, en in PLATES.items():
        out[(PLATE_SLOT, k)] = plate_rows(en, qents[k][3], qents[k][4])
    s, e = ents[GAUGE_SLOT]
    rec = lz.unpack_record(data[s:e])
    _, qents, _ = qx.parse(rec)
    for k, en in GAUGE.items():
        out[(GAUGE_SLOT, k)] = gauge_rows(read4(rec, qents[k]), en, k)
    for slot in (0, 1):
        s, e = ents[slot]
        rec = lz.unpack_record(data[s:e])
        _, qents, _ = qx.parse(rec)
        out[(slot, 57)] = edged(bold_mask("Prana", 24, 16, cap=9, min_cap=6), lambda j, i: 1, 8)
        for k, letter in ORDERS.items():
            out[(slot, k)] = order_icon(read4(rec, qents[k]), letter)
        if slot == 1:
            for k, en in BATTLE.items():
                out[(slot, k)] = edged(bold_mask(en, qents[k][3], qents[k][4]), metal, 8)
    caps = album_captions()
    for slot in ALBUM_SLOTS:
        s, e = ents[slot]
        rec = lz.unpack_record(data[s:e])
        _, qents, clut = qx.parse(rec)
        for k, ent in enumerate(qents):
            if (slot, k) in caps:
                base = (ent[1] & 0xF) * 256
                out[(slot, k)] = caption_rows(read8(rec, ent), clut[base:base + 256], caps[(slot, k)])
    s, e = ents[CREDITS_SLOT]
    _, qents, clut = qx.parse(lz.unpack_record(data[s:e]))
    for k, en in CREDITS.items():
        base = (qents[k][1] & 0xF) * 16
        out[(CREDITS_SLOT, k)] = aa_rows(en, qents[k][3], qents[k][4], clut[base:base + 16])
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
        assert magic in (0x5871, 0x5851), slot
        for k, rows in ims.items():
            if magic == 0x5871:
                put4(rec, qents[k], rows)
            else:                       # 8 bpp, w <= 128: linear rows
                off, _, _, w, h, _, _ = qents[k]
                assert w <= 128 and len(rows) == h and all(len(r) == w for r in rows)
                rec[off:off + w * h] = bytes(v for r in rows for v in r)
        out[slot] = lz.pack_record(bytes(rec))
        assert lz.unpack_record(out[slot]) == rec, slot
    slot, k = ALBUM_TAG[:2]
    s, e = ents[slot]
    rec = bytearray(lz.unpack_record(data[s:e]))
    _, qents, clut = qx.parse(rec)
    for o, v in album_tag(rec, qents[k], clut[(qents[k][1] & 0xF) * 256:][:256]).items():
        rec[o] = v
    out[slot] = lz.pack_record(bytes(rec))
    s, e = ents[NEW_YEAR]
    rec = bytearray(lz.unpack_record(data[s:e]))
    _, qents, clut = qx.parse(rec)
    for o, v in new_year(rec, qents[0], clut[:256]).items():
        rec[o] = v
    out[NEW_YEAR] = lz.pack_record(bytes(rec))
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
