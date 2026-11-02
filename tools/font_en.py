"""font_en.py: the English font: narrow proportional glyphs + the variable-width (VWF) hook.

The game's 1 bpp font has 8x16 half-width cells for A-Z a-z 0-9 (codes 01-1A, 1B-34, 36-3F) and a few symbols
(F0 00.. = 0x100..), all drawn on a fixed 8-px advance. English set at 8 px did not fit the menus (fields sit at
fixed pen positions sized for 12-px kanji), so (D4: engine work first, docs/decisions.md D10):
- every English glyph is redrawn here, left-aligned and narrow (most letters 5 px of ink), into its cell: the
  Latin cells, the existing symbol cells, and 24 punctuation cells added into blank cells 0x114-0x12B;
- the glyph routine 0x80034530 ends a one-byte-cell glyph (code < 0x200) with `x += 8` at 0x80035258; the hook
  replaces that with `x += ADV[code]` from a 0x200-byte table (kana and anything not English keep 8, kanji keep
  their own `x += 12` path). The routine positions glyphs in 2-px steps (4 bpp, byte = 2 px), so every advance is
  even: ink width + 1 px gap, rounded up to even. It blits all 8 columns of a cell, so the next glyph overwrites
  this one's columns past its advance: the art must stay inside the advance (check() enforces it).
- the 8x8 ASCII mode (flag 0x40 at cursor+4) keeps 8.

Art: rows from cell row 4 (cap top) down; cap height and digits rows 4-13, x-height rows 7-13, descenders 14-15.
Bit order in the cell is the renderer's nibble order (bits 6,7,4,5,2,3,0,1 = x 0..7).

    python -X utf8 tools/font_en.py check          # metrics self-test
    python -X utf8 tools/font_en.py sheet OUT.png  # render the glyphs at their advances
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

ORDER = [6, 7, 4, 5, 2, 3, 0, 1]          # bit for pixel x (fontsheet.py / the draw routine's nibble tables)
FONT_BASE = 0xA03CC                       # file offset of glyph cell 0
TOP = 4                                   # cell row of the art's first row

# 0x114.. -- punctuation absent from the Japanese font as a half-width cell, drawn into blank cells.
GLYPHS = {
    0x114: ".", 0x115: ",", 0x116: "'", 0x117: "-", 0x118: '"', 0x119: "(", 0x11A: ")",
    0x11B: "[", 0x11C: "]", 0x11D: ";", 0x11E: "&", 0x11F: "*", 0x120: "<", 0x121: ">",
    0x122: "#", 0x123: "$", 0x124: "@", 0x125: "_", 0x126: "`", 0x127: "{", 0x128: "}",
    0x129: "|", 0x12A: "\\", 0x12B: "^",
}
LATIN = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
EXISTING = {" ": 0x00, "?": 0x108, "!": 0x109, ":": 0x10A, "/": 0x103, "=": 0x104,
            "+": 0x105, "%": 0x100, "~": 0x101}
SPACE_ADV = 4

ART = {
    # capitals, 10 rows
    "A": ".###./#...#/#...#/#...#/#...#/#####/#...#/#...#/#...#/#...#",
    "B": "####./#...#/#...#/#...#/####./#...#/#...#/#...#/#...#/####.",
    "C": ".###./#...#/#..../#..../#..../#..../#..../#..../#...#/.###.",
    "D": "####./#...#/#...#/#...#/#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../#..../####./#..../#..../#..../#..../#####",
    "F": "#####/#..../#..../#..../####./#..../#..../#..../#..../#....",
    "G": ".###./#...#/#..../#..../#.###/#...#/#...#/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#...#/#####/#...#/#...#/#...#/#...#/#...#",
    "I": "###/.#./.#./.#./.#./.#./.#./.#./.#./###",
    "J": "..###/...#./...#./...#./...#./...#./...#./#..#./#..#./.##..",
    "K": "#...#/#...#/#..#./#.#../##.../#.#../#..#./#..#./#...#/#...#",
    "L": "#..../#..../#..../#..../#..../#..../#..../#..../#..../#####",
    "M": "#.....#/##...##/#.#.#.#/#..#..#/#..#..#/#.....#/#.....#/#.....#/#.....#/#.....#",
    "N": "#...#/##..#/##..#/#.#.#/#.#.#/#..##/#..##/#...#/#...#/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/#...#/####./#..../#..../#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/#...#/####./#.#../#..#./#..#./#...#/#...#",
    "S": ".###./#...#/#..../#..../.###./....#/....#/....#/#...#/.###.",
    "T": "#####/..#../..#../..#../..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/#...#/#...#/.#.#./.#.#./.#.#./..#..",
    "W": "#.....#/#.....#/#.....#/#.....#/#.....#/#..#..#/#..#..#/#.#.#.#/##...##/#.....#",
    "X": "#...#/#...#/.#.#./.#.#./..#../..#../.#.#./.#.#./#...#/#...#",
    "Y": "#...#/#...#/#...#/.#.#./.#.#./..#../..#../..#../..#../..#..",
    "Z": "#####/....#/...#./...#./..#../..#../.#.../.#.../#..../#####",
    # lower case: x-height rows 3-9, ascenders from row 0, descenders rows 10-11
    "a": "...../...../...../.###./....#/.####/#...#/#...#/#..##/.##.#",
    "b": "#..../#..../#..../####./#...#/#...#/#...#/#...#/#...#/####.",
    "c": "..../..../..../.###/#.../#.../#.../#.../#.../.###",
    "d": "....#/....#/....#/.####/#...#/#...#/#...#/#...#/#...#/.####",
    "e": "...../...../...../.###./#...#/#...#/#####/#..../#...#/.###.",
    "f": ".##/#../#../###/#../#../#../#../#../#..",
    "g": "...../...../...../.####/#...#/#...#/#...#/#...#/.####/....#/#...#/.###.",
    "h": "#..../#..../#..../####./#...#/#...#/#...#/#...#/#...#/#...#",
    "i": "./#/./#/#/#/#/#/#/#",
    "j": "../.#/../.#/.#/.#/.#/.#/.#/.#/.#/#.",
    "k": "#.../#.../#.../#.../#..#/#.#./##../#.#./#..#/#..#",
    "l": "#/#/#/#/#/#/#/#/#/#",
    "m": "......./......./......./###.##./#..#..#/#..#..#/#..#..#/#..#..#/#..#..#/#..#..#",
    "n": "...../...../...../####./#...#/#...#/#...#/#...#/#...#/#...#",
    "o": "...../...../...../.###./#...#/#...#/#...#/#...#/#...#/.###.",
    "p": "...../...../...../####./#...#/#...#/#...#/#...#/####./#..../#..../#....",
    "q": "...../...../...../.####/#...#/#...#/#...#/#...#/.####/....#/....#/....#",
    "r": ".../.../.../#.#/##./#../#../#../#../#..",
    "s": "...../...../...../.####/#..../#..../.###./....#/....#/####.",
    "t": ".../.#./.#./###/.#./.#./.#./.#./.#./..#",
    "u": "...../...../...../#...#/#...#/#...#/#...#/#...#/#...#/.####",
    "v": "...../...../...../#...#/#...#/#...#/.#.#./.#.#./.#.#./..#..",
    "w": "......./......./......./#.....#/#.....#/#.....#/#.....#/#..#..#/#.#.#.#/.#...#.",
    "x": "...../...../...../#...#/.#.#./.#.#./..#../.#.#./.#.#./#...#",
    "y": "...../...../...../#...#/#...#/#...#/#...#/#...#/.####/....#/#...#/.###.",
    "z": "...../...../...../#####/...#./..#../..#../.#.../#..../#####",
    # digits: all 5 wide (advance 6) so numbers stay in columns
    "0": ".###./#...#/#...#/#..##/#.#.#/#.#.#/##..#/#...#/#...#/.###.",
    "1": "..#../.##../..#../..#../..#../..#../..#../..#../..#../.###.",
    "2": ".###./#...#/....#/....#/...#./..#../.#.../#..../#..../#####",
    "3": ".###./#...#/....#/....#/..##./....#/....#/....#/#...#/.###.",
    "4": "...#./..##./..##./.#.#./.#.#./#..#./#####/...#./...#./...#.",
    "5": "#####/#..../#..../####./....#/....#/....#/....#/#...#/.###.",
    "6": ".###./#...#/#..../#..../####./#...#/#...#/#...#/#...#/.###.",
    "7": "#####/....#/....#/...#./...#./..#../..#../..#../..#../..#..",
    "8": ".###./#...#/#...#/#...#/.###./#...#/#...#/#...#/#...#/.###.",
    "9": ".###./#...#/#...#/#...#/#...#/.####/....#/....#/#...#/.###.",
    # symbols
    "?": ".###./#...#/....#/...#./..#../..#../..#../...../..#../..#..",
    "!": "#/#/#/#/#/#/#/./#/#",
    ":": "../../../##/##/../../../##/##",
    "/": "....#/....#/...#./...#./..#../..#../.#.../.#.../#..../#....",
    "=": "...../...../...../...../#####/...../#####",
    "+": "...../...../...../..#../..#../#####/..#../..#..",
    "%": "##..#/##..#/...#./...#./..#../..#../.#.../.#.../#..##/#..##",
    "~": "...../...../...../...../.#.../#.#.#/...#.",
    ".": "../../../../../../../../##/##",
    ",": "../../../../../../../../##/##/.#/#.",
    "'": "#/#/#",
    "-": ".../.../.../.../.../.../###",
    '"': "#.#/#.#/#.#",
    "(": ".#/#./#./#./#./#./#./#./#./.#",
    ")": "#./.#/.#/.#/.#/.#/.#/.#/.#/#.",
    "[": "##/#./#./#./#./#./#./#./#./##",
    "]": "##/.#/.#/.#/.#/.#/.#/.#/.#/##",
    ";": "../../../##/##/../../../##/##/.#/#.",
    "&": ".##../#..#./#..#./.##../.#.../#.#.#/#..#./#..#./#..##/.##.#",
    "*": "...../...../..#../#.#.#/.###./#.#.#/..#..",
    "<": "..../..../...#/..#./.#../#.../.#../..#./...#",
    ">": "..../..../#.../.#../..#./...#/..#./.#../#...",
    "#": "...../.#.#./.#.#./#####/.#.#./.#.#./#####/.#.#./.#.#.",
    "$": "..#../.####/#.#../#.#../.###./..#.#/..#.#/####./..#..",
    "@": "......./.#####./#.....#/#..##.#/#.#.#.#/#.#.#.#/#..###./#....../.#####.",
    "_": "...../...../...../...../...../...../...../...../...../...../#####",
    "`": "#./.#",
    "{": "..#/.#./.#./.#./#../.#./.#./.#./.#./..#",
    "}": "#../.#./.#./.#./..#/.#./.#./.#./.#./#..",
    "|": "#/#/#/#/#/#/#/#/#/#/#/#",
    "\\": "#.../#.../.#../.#../.#../..#./..#./..#./...#/...#",
    "^": "..#../.#.#./#...#",
}


def code_of(ch):
    if ch in EXISTING:
        return EXISTING[ch]
    if "A" <= ch <= "Z":
        return 0x01 + ord(ch) - ord("A")
    if "a" <= ch <= "z":
        return 0x1B + ord(ch) - ord("a")
    if "0" <= ch <= "9":
        return 0x36 + ord(ch) - ord("0")
    return {v: k for k, v in GLYPHS.items()}[ch]


def rows(ch):
    """the art as a list of row strings (cell rows TOP..)."""
    return ART[ch].split("/")


def ink_width(ch):
    return max(len(r) for r in rows(ch))


def advance(ch):
    """even advance: ink + 1 px gap, rounded up to even (the routine places glyphs in 2-px steps)."""
    if ch == " ":
        return SPACE_ADV
    w = ink_width(ch) + 1
    return w + (w & 1)


def cell(ch):
    """16 rows x 8 columns of 0/1."""
    out = [[0] * 8 for _ in range(16)]
    for y, r in enumerate(rows(ch)):
        for x, c in enumerate(r):
            if c == "#":
                out[TOP + y][x] = 1
    return out


def glyph_bytes(ch):
    """16 bytes, one per row, in the renderer's bit order."""
    out = bytearray()
    for row in cell(ch):
        b = 0
        for x, v in enumerate(row):
            if v:
                b |= 1 << ORDER[x]
        out.append(b)
    return bytes(out)


def adv_table():
    """0x200 bytes: the advance of every one-byte-cell glyph code (8 = the game's own)."""
    t = bytearray([8] * 0x200)
    for ch in ART:
        t[code_of(ch)] = advance(ch)
    t[0] = SPACE_ADV
    return bytes(t)


# Hook: the glyph routine's tail `lhu v0,0(fp) / nop / addiu v0,v0,8 / sh v0,0(fp)` at 0x80035258 (the kanji path
# jumps to the sh with v0 = x + 12; the 8x8 ASCII path jumps to 0x80035258). In the one-byte path s2 = code*16 +
# 16 there (s2 = code << 4, +1 per row, 16 rows; nothing else writes it).
HOOK_SITE = 0x80035258
HOOK_ORIG = bytes.fromhex("0000c297" "00000000")   # lhu v0,0(fp) / nop  (then addiu v0,v0,8, now unreached)
BACK = 0x80035264                                  # sh v0,0(fp)


def _ins(word):
    return word.to_bytes(4, "little")


def hook_code(at, table):
    """the hook placed at `at` (RAM), reading the advance table at `table`."""
    v0, v1, a0, s2, fp, zero = 2, 3, 4, 18, 30, 0
    lbu = lambda rt, off, rs: 0x90000000 | rs << 21 | rt << 16 | (off & 0xFFFF)  # noqa: E731
    andi = lambda rt, rs, imm: 0x30000000 | rs << 21 | rt << 16 | imm  # noqa: E731
    addiu = lambda rt, rs, imm: 0x24000000 | rs << 21 | rt << 16 | (imm & 0xFFFF)  # noqa: E731
    bnez = lambda rs, n: 0x14000000 | rs << 21 | (n & 0xFFFF)  # noqa: E731
    srl = lambda rd, rt, sa: rt << 16 | rd << 11 | sa << 6 | 2  # noqa: E731
    addu = lambda rd, rs, rt: rs << 21 | rt << 16 | rd << 11 | 0x21  # noqa: E731
    lui = lambda rt, imm: 0x3C000000 | rt << 16 | imm  # noqa: E731
    j = lambda target: 0x08000000 | (target & 0x0FFFFFFF) >> 2  # noqa: E731
    lo = table & 0xFFFF
    hi = (table + 0x8000) >> 16
    code = [
        lbu(v1, 4, fp),             # cursor flags
        0,                          # load delay
        andi(v1, v1, 0x40),         # 8x8 ASCII mode keeps 8
        bnez(v1, 11 - 4),           # -> the j (word 11); the offset counts from the delay slot (word 4)
        addiu(a0, zero, 8),
        srl(v1, s2, 4),
        addiu(v1, v1, -1),          # code
        andi(v1, v1, 0x1FF),
        lui(a0, hi),
        addu(a0, a0, v1),
        lbu(a0, lo, a0),            # ADV[code]; the j below covers its load delay
        j(BACK),
        addu(v0, v0, a0),           # delay slot: x += advance
    ]
    return b"".join(map(_ins, code))


def site_patch(at):
    """the 2 words written at HOOK_SITE: `j hook` with the original lhu in its delay slot."""
    return _ins(0x08000000 | (at & 0x0FFFFFFF) >> 2) + bytes.fromhex("0000c297")


# Message pixel width 0x80031010(id): 8 per one-byte code (`j 800310E4 / addiu t0,t0,8` at 0x800310A0), 12 per
# F0-F9 pair (`j 800310E4 / addiu t0,t0,0xC` at 0x800310B4, a3 already on the 2nd byte). Callers size and place
# windows from it (location label right-aligned at 0x139 - w, weapon-name popup w + 0x29, event title centred),
# so it must agree with the VWF. Loop registers: t0 width, a3 ptr, v1 byte, t1-t3 constants; a1/v0 are free.
WIDTH_SITES = ((0x800310A0, bytes.fromhex("39c40008" "08000825")),     # j 800310E4 / addiu t0,t0,8
               (0x800310B4, bytes.fromhex("39c40008" "0c000825")))     # j 800310E4 / addiu t0,t0,0xC
WIDTH_BACK = 0x800310E4


def width_code(at, table):
    """two stubs at `at`: one-byte code, then the F0-F9 pair. Returns (bytes, [stub addresses])."""
    v0, v1, a1, a3, t0, zero = 2, 3, 5, 7, 8, 0
    lbu = lambda rt, off, rs: 0x90000000 | rs << 21 | rt << 16 | (off & 0xFFFF)  # noqa: E731
    addiu = lambda rt, rs, imm: 0x24000000 | rs << 21 | rt << 16 | (imm & 0xFFFF)  # noqa: E731
    bne = lambda rs, rt, n: 0x14000000 | rs << 21 | rt << 16 | (n & 0xFFFF)  # noqa: E731
    addu = lambda rd, rs, rt: rs << 21 | rt << 16 | rd << 11 | 0x21  # noqa: E731
    lui = lambda rt, imm: 0x3C000000 | rt << 16 | imm  # noqa: E731
    j = lambda target: 0x08000000 | (target & 0x0FFFFFFF) >> 2  # noqa: E731
    hl = lambda a: ((a + 0x8000) >> 16, a & 0xFFFF)  # noqa: E731
    h0, l0 = hl(table)
    h1, l1 = hl(table + 0x100)
    one = [lui(v0, h0), addu(v0, v0, v1), lbu(v0, l0, v0), 0, j(WIDTH_BACK), addu(t0, t0, v0)]
    # 0 v0=F0, 1 bne -> word 8 (not F0: kanji, a1 = 12 from the delay slot), 3 second byte, 5 load delay,
    # 7 ADV[0x100 + byte], 8 j back, 9 t0 += a1
    two = [addiu(v0, zero, 0xF0), bne(v1, v0, 8 - 2), addiu(a1, zero, 12), lbu(v0, 0, a3), lui(a1, h1),
           0, addu(a1, a1, v0), lbu(a1, l1, a1), j(WIDTH_BACK), addu(t0, t0, a1)]
    code = one + two
    return b"".join(map(_ins, code)), [at, at + 4 * len(one)]


def vwf_blob(at):
    """glyph hook + width stubs + advance table at RAM `at` (4-aligned). Returns (bytes, [(site, 8 bytes)])."""
    n = len(hook_code(at, 0)) + len(width_code(at, 0)[0])
    table = at + n
    w, stubs = width_code(at + len(hook_code(at, 0)), table)
    blob = hook_code(at, table) + w + adv_table()
    sites = [(HOOK_SITE, HOOK_ORIG, site_patch(at))]
    for (site, orig), stub in zip(WIDTH_SITES, stubs):
        sites.append((site, orig, _ins(0x08000000 | (stub & 0x0FFFFFFF) >> 2) + bytes(4)))
    return blob, sites


def patch(exe, put):
    """Write every English glyph into the EXE font through `put` (cells only; the hook goes with the bank)."""
    for ch in sorted(ART, key=code_of):
        code = code_of(ch)
        put(exe, FONT_BASE + code * 16, glyph_bytes(ch), f"font_en {ch!r} cell {code:03X}")
    return exe


CANARY = "The quick brown fox jumps over the lazy dog!?,.:;'\"-()[]&*<>#$@_`{}|\\^ 0123456789"


def check():
    for ch, art in ART.items():
        rs = rows(ch)
        assert len(rs) + TOP <= 16, ch
        w = ink_width(ch)
        assert all(len(r) == w for r in rs), (ch, [len(r) for r in rs])
        assert set(art) <= set("#./"), ch
        assert any("#" in r for r in rs), ch
        assert advance(ch) % 2 == 0 and ink_width(ch) < advance(ch) <= 8, ch   # ink stays inside the advance
    missing = [c for c in CANARY if c != " " and c not in ART]
    assert not missing, f"no glyph for {missing!r}"
    assert len({code_of(c) for c in ART}) == len(ART)
    assert all(0x114 <= c <= 0x12B for c in GLYPHS)
    print(f"font_en ok: {len(ART)} glyphs, advances {sorted({advance(c) for c in ART})}")


def text_px(s):
    """pixel width of plain English (no codes) at the VWF advances."""
    return sum(advance(c) if c in ART or c == " " else 8 for c in s)


def sheet(out, text=CANARY):
    from PIL import Image
    zoom = 4
    w = text_px(text)
    im = Image.new("L", (w * zoom + 8, 16 * zoom + 8), 255)
    x0 = 4
    for ch in text:
        if ch in ART:
            for y, row in enumerate(cell(ch)):
                for x, v in enumerate(row):
                    if v:
                        im.paste(0, (x0 + x * zoom, 4 + y * zoom, x0 + x * zoom + zoom, 4 + y * zoom + zoom))
        x0 += (advance(ch) if ch in ART or ch == " " else 8) * zoom
    im.save(out)
    print(out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        check()
    elif cmd == "sheet":
        sheet(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else CANARY)
