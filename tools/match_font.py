"""match_font.py: first-guess character for every glyph of the game font, by template matching against MS Gothic 12 px.

Writes work/font/match.tsv: code, best char, distance, 2nd char, distance. Candidates: JIS X 0208 (cp932 double-byte).
Then tools/build_tbl.py turns the reviewed result into tbl/jp.tbl.

    python -X utf8 tools/match_font.py [--font C:/Windows/Fonts/msgothic.ttc] [--first 200 --last a4c]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fontsheet import EXE, glyph  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def candidates():
    out = []
    for hi in list(range(0x81, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            try:
                c = bytes([hi, lo]).decode("cp932")
            except UnicodeDecodeError:
                continue
            if c.isprintable() and c != "\u3000":
                out.append(c)
    return out


def norm(a):
    """Crop to bounding box and place in a 14x14 frame at the top-left corner of the box (shift-tolerant compare)."""
    ys, xs = np.nonzero(a)
    if len(ys) == 0:
        return None, (0, 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (ys.min(), xs.min())


def render(font, ch, size=16):
    im = Image.new("1", (size, size), 0)
    ImageDraw.Draw(im).text((0, 0), ch, font=font, fill=1)
    return np.array(im, dtype=np.uint8)


def dt(a):
    from scipy.ndimage import distance_transform_edt
    return distance_transform_edt(1 - a) if a.any() else np.full(a.shape, 16.0)


def chamfer_all(g, T, DT):
    """Symmetric chamfer distance of glyph g to every template (T masks, DT their distance transforms), best of
    shifts -1..1; tolerant of the 1-px stroke offsets between the game's font design and MS Gothic."""
    best = np.full(len(T), 1e9)
    tsum = T.sum(axis=(1, 2)).clip(1)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            s = np.roll(np.roll(g, dy, 0), dx, 1)
            ds = dt(s)
            a = (DT * s).sum(axis=(1, 2)) / max(1, s.sum())
            b = (T * ds).sum(axis=(1, 2)) / tsum
            best = np.minimum(best, a + b)
    return best


def dist(a, b):
    """Min Hamming distance of a against b over small shifts, on a 16x16 canvas."""
    best = 10 ** 9
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            s = np.roll(np.roll(b, dy, 0), dx, 1)
            best = min(best, int(np.count_nonzero(a != s)))
    return best


def main():
    fontpath = arg("--font", "C:/Windows/Fonts/msgothic.ttc")
    first, last = int(arg("--first", "0"), 16), int(arg("--last", "a4c"), 16)
    font = ImageFont.truetype(fontpath, 12)
    font.fontmode = "1"
    cands = candidates()
    # Render candidates and align each one's bounding-box centre to (8, 8).
    def centred(a):
        ys, xs = np.nonzero(a)
        if len(ys) == 0:
            return a
        cy, cx = (ys.min() + ys.max()) // 2, (xs.min() + xs.max()) // 2
        return np.roll(np.roll(a, 8 - cy, 0), 8 - cx, 1)
    tmpl = np.array([centred(render(font, c)) for c in cands])
    DT = np.array([dt(t) for t in tmpl])
    exe = EXE.read_bytes()
    out = ROOT / "work/font/match.tsv"
    glyphs, best, scores = {}, {}, {}
    for code in range(first, last + 1):
        g = np.zeros((16, 16), dtype=np.uint8)
        for y, r in enumerate(glyph(exe, code)):
            g[y, :len(r)] = r
        if not g.any():
            continue
        g = centred(g)
        glyphs[code] = g
        sc = chamfer_all(g, tmpl, DT)
        scores[code] = sc
        top = np.argsort(sc)[:2]
        best[code] = [(round(float(sc[i]), 2), int(i)) for i in top]
    # Anchors: confident matches. The font is a kanji subset stored in runs of rising JIS order, so a glyph between
    # two anchors of one run must be a character between them in cp932 order: re-match it within that window.
    codes = sorted(best)
    anchor = {c: best[c][0][1] for c in codes if best[c][0][0] <= 0.35 and best[c][1][0] - best[c][0][0] >= 0.25}
    lines = ["code\tch\td\tch2\td2\thow"]
    akeys = sorted(anchor)
    import bisect
    for code in range(first, last + 1):
        if code not in best:
            lines.append(f"{code:03X}\t\t\t\t\tempty")
            continue
        (d1, i1), (d2, i2) = best[code][0], best[code][1]
        how = "free"
        if code in anchor:
            how = "anchor"
        else:
            k = bisect.bisect_left(akeys, code)
            if 0 < k < len(akeys):
                lo, hi = anchor[akeys[k - 1]], anchor[akeys[k]]
                if lo < hi and hi - lo < 400:
                    win = sorted((round(float(scores[code][i]), 2), i) for i in range(lo + 1, hi))
                    if win:
                        (d1, i1) = win[0]
                        (d2, i2) = win[1] if len(win) > 1 else (99, i1)
                        how = "window"
        lines.append(f"{code:03X}\t{cands[i1]}\t{d1}\t{cands[i2]}\t{d2}\t{how}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out, len(lines) - 1, "anchors", len(anchor))


if __name__ == "__main__":
    main()
