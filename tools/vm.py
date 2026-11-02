"""vm.py: the scenario VM's bytecode (D_SCE scene records, the resident system script, EXE menus).

    python -X utf8 tools/vm.py info SLOT [SLOT..]     # disassemble D_SCE records, print text blocks + holes
    python -X utf8 tools/vm.py text SLOT              # decoded text of one scene

Facts (docs/re/text.md, all verified against the emulator trace work/scratch/tr1):
- Opcode length table at RAM 0x800C8480 (EXE file 0xB8C80): one byte per opcode. A length of 0 means
  the op is not implemented (the interpreter would spin), so a 0 at an instruction boundary is a decode error.
- The interpreter (0x800581A0) fetches an op at `base`, copies `length` bytes to state+0x54, calls
  handler[op] (table 0x800C8080), and then advances `base += state+0x48` when the handler returns odd.
  Multi-frame ops return an even value (0x80) and keep the op; the advance in state+0x48 may be rewritten
  by the handler, which is how ops with argument bytes past the table length work.
- Jump/branch ops set state+0x48 to a displacement from the *current* op, so target = op_off + displacement.
- Op 0x78 = text: `78 style [args]` then the text, terminated by FF. style 1 and 2 carry two argument
  bytes before the text (a portrait/speaker id); styles 0, 8..12 carry none. The handler formats the text
  into a 0x400-byte buffer and leaves state+0x48 = the whole `78 style args text FF` length.
- Several opcodes are sub-op dispatchers: the second byte indexes a handler table, and each sub-handler can
  consume more argument bytes (SUBK below, derived from the handlers with tools/re.py). Examples:
  `1E 00 <4 args>` inserts two runtime values into the text, `08 <u16 frames>` waits.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import arc  # noqa: E402

# Opcode length table, RAM 0x800C8480 (256 bytes). tools/re.py lengths() re-reads it from the EXE.
LEN = bytes.fromhex(
    "0003050305020104030305030202020102030604050804040404000201010202"
    "0101010101010100010106060a02060202020103060702020903030101020000"
    "02010202030601020204010405000003010604040204040206050a0c05010201"
    "0302060701010302040406040801030401090100020101000202020300000101"
    "020104020206030404020300010105000307070b0a0d03030101000103060508"
    "07030604030406020b0602020203030402000000010107070501020100000701"
    "0200000103010202040303010102010201050507020101010400030502010000"
    "0101020101010101010101010000000001010101010101010104000000000000")
assert len(LEN) == 256

# Sub-op dispatchers: op -> {second byte: extra argument bytes after the 2-byte op}.
# Derived from the handlers (each sub-handler's `addiu K; sw state+0x48`); docs/re/text.md.
SUBK = {
    0x16: {19: 1, 25: 2, 26: 2, 32: 1, 44: 4, 48: 2, 50: 2, 51: 2, 53: 3, 56: 2, 57: 2, 58: 2},
    0x1B: {0: 1, 12: 4, 16: 2, 18: 2, 19: 2, 21: 3, 24: 2, 25: 2, 26: 2},
    0x1E: {0: 4, 4: 2, 6: 2, 7: 2, 9: 3, 12: 2, 13: 2, 14: 2},
    0x1F: {0: 2, 1: 2, 2: 2},
    0x5C: {15: 1, 17: 1, 20: 10, 21: 1, 22: 1, 23: 1, 24: 1, 26: 1, 27: 1, 28: 1},
    0xAD: {26: 2, 28: 2, 32: 2, 36: 2, 46: 2, 54: 2},
    0xAE: {10: 2, 12: 2, 16: 2, 20: 2, 30: 2, 38: 2, 50: 3},
    0xB0: {6: 2, 14: 2, 26: 3, 45: 2, 47: 2, 53: 3, 54: 2, 56: 1},
    0xC0: {2: 2, 15: 1, 21: 1, 22: 1, 26: 2, 27: 1, 29: 5, 30: 6, 32: 1, 33: 1, 35: 3, 36: 2, 38: 1,
           40: 2, 42: 1, 47: 2, 48: 2, 49: 2, 54: 1, 55: 1, 56: 2, 58: 2, 61: 2, 62: 2, 63: 2},
    0xC8: {0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 8: 2, 9: 2, 10: 2, 11: 2, 12: 2, 13: 2, 16: 2, 17: 4,
           18: 1, 19: 2, 20: 2, 21: 2},
    0xDC: {0: 2, 1: 4, 2: 1, 3: 2, 4: 2, 5: 2},
}

TEXT = 0x78
CHOICE = 0x7A
STYLE_ARGS = {1: 2, 2: 3}          # text-op styles with argument bytes before the text (verified from the data)
JUMP_REL = {0x01: 1, 0x07: 2, 0x14: 1}   # op: bias in target = op_off + displacement + bias
CALL_REL = {0x03: 1}
JUMP_ABS = {0x02: 1}               # op: bias, displacement is a u32
CALL_ABS = {0x04: 1}
STOP = {0x06, 0x0B, 0xB4}          # return, goto scene, table goto (ends the record's flow)


def s16(a, b):
    v = a | (b << 8)
    return v - 0x10000 if v & 0x8000 else v


def jump_disp(rec, i):
    """s16 displacement of the relative jump/call op at i.

    Ops 01/03/14 carry it at +1. Op 07 is `07 <count> <s16>` — the repeat count comes first (handler
    0x80058920 loads byte 1 as a counter in state+0x46), so its displacement sits at +2."""
    if rec[i] == 0x07:
        return s16(rec[i + 2], rec[i + 3])
    return s16(rec[i + 1], rec[i + 2])


def text_end(rec, i):
    """End (index of the terminating FF) of the text at i, walking it glyph by glyph.

    The formatter reads one glyph at a time: F0..FA are two-byte glyph codes (so an FF may be the
    low byte of a glyph and does not end the text), FC carries two argument bytes, FB/FD/FE one byte.
    A plain FF ends the string."""
    while i < len(rec):
        b = rec[i]
        if b == 0xFF:
            return i
        if 0xF0 <= b <= 0xFA:
            i += 2
        elif b == 0xFC:
            i += 3
        else:
            i += 1
    return None


def text_op(rec, i):
    """(text start, end index of the terminating FF) for the 78 op at i.

    `78 78 <inner 78 op>` is a wrapper: the text belongs to the inner op (seen for battle-style
    windows), so follow it. Returns None when the text does not terminate."""
    if i + 1 >= len(rec):
        return None
    style = rec[i + 1]
    if style == 0x78:            # `78 78 <style> <args>`: the inner op starts at the second 78
        return text_op(rec, i + 1)
    start = i + 2 + STYLE_ARGS.get(style & 0x0F, 0)
    end = text_end(rec, start)
    return None if end is None else (start, end)


def text_at(rec, i):
    """(start, end) of the text of a 78 op at i: text starts after the style args, ends before FF."""
    return text_op(rec, i)


def insn_len(rec, i):
    """(length, kind) for the instruction at i; kind 'op' | 'text'. None = not decodable."""
    if not 0 <= i < len(rec):
        return None
    op = rec[i]
    if op == TEXT:
        t = text_at(rec, i)
        return None if t is None else (t[1] + 1 - i, "text")
    if op == CHOICE:
        if i + 1 >= len(rec):
            return None
        ln = 2 + 2 * rec[i + 1]
        return (ln, "op") if i + ln <= len(rec) else None
    ln = LEN[op]
    if ln == 0:
        return None
    if op in SUBK and i + 1 < len(rec):
        ln += SUBK[op].get(rec[i + 1], 0)
    return (ln, "op") if i + ln <= len(rec) else None


def walk(rec, start=0):
    """Control-flow walk from `start`.

    Returns (seen, errors): seen maps instruction offset -> (length, kind, op); errors lists
    (offset, reason) for instruction starts that do not decode or point outside the record.
    """
    seen, errors, work = {}, [], [start]
    while work:
        i = work.pop()
        if i in seen:
            continue
        if not 0 <= i < len(rec):
            errors.append((i, "outside record"))
            continue
        r = insn_len(rec, i)
        if r is None:
            errors.append((i, f"bad op {rec[i]:02X}"))
            continue
        ln, kind = r
        seen[i] = (ln, kind, rec[i])
        op = rec[i]
        if kind == "text":
            work.append(i + ln)
        elif op == CHOICE:
            for k in range(rec[i + 1]):
                off = s16(rec[i + 2 + 2 * k], rec[i + 3 + 2 * k])
                work.append(i + 2 + 2 * k + off)
            work.append(i + ln)
        elif op in JUMP_REL:
            work.append(i + jump_disp(rec, i) + JUMP_REL[op])
            if op == 0x14 or op == 0x07:
                work.append(i + ln)
        elif op in CALL_REL:
            work.append(i + jump_disp(rec, i) + CALL_REL[op])
            work.append(i + ln)
        elif op in JUMP_ABS or op in CALL_ABS:
            bias = JUMP_ABS.get(op) or CALL_ABS[op]
            d = int.from_bytes(rec[i + 1:i + 5], "little")
            work.append(i + d + bias)
            if op in CALL_ABS:
                work.append(i + ln)
        elif op in STOP:
            pass
        else:
            work.append(i + ln)
    return seen, errors


def texts(rec, seen=None):
    """Text blocks of a record: [(offset, text_start, text_end)] (offset = the 78 op)."""
    if seen is None:
        seen, _ = walk(rec)
    out = []
    for i, (ln, kind, op) in sorted(seen.items()):
        if kind == "text":
            start, end = text_op(rec, i)
            out.append((i, start, end))
    return out


def scan_texts(rec):
    """Every 78 op whose text decodes to plausible text, wherever it is (catches unreached code).

    Candidates must have printable text of 1..400 bytes containing at least one kana/kanji code,
    and the byte after FF must not continue the text (i.e. FF is the terminator)."""
    out = []
    for i in range(len(rec) - 2):
        if rec[i] != TEXT:
            continue
        style = rec[i + 1] & 0x0F
        if style in (3, 4, 5, 6, 7):
            continue
        t = text_at(rec, i)
        if not t or not 1 <= t[1] - t[0] <= 400:
            continue
        body = rec[t[0]:t[1]]
        if any(c >= 0xF0 or 0x40 <= c <= 0xEE for c in body):
            out.append((i, t[0], t[1]))
    return out

def sce_records():
    """[(slot, rec)] for every D_SCE record."""
    data = (ROOT / "work/disc/tree/D_SCE.BIN").read_bytes()
    return [(slot, data[s:e]) for slot, (s, e) in enumerate(arc.entries(data))]


def main():
    from tbl import Table
    T = Table.load(ROOT / "tbl/jp.tbl")
    recs = dict(sce_records())
    for arg in sys.argv[1:]:
        slot = int(arg, 0)
        rec = recs[slot]
        seen, errors = walk(rec)
        ts = texts(rec, seen)
        print(f"slot {slot}: {len(rec):#x} bytes, {len(seen)} instructions, {len(ts)} text blocks, "
              f"{len(errors)} decode errors")
        for i, a, b in ts[:int(__import__('os').environ.get('N', '20'))]:
            print(f"  {i:06x} style {rec[i + 1]:02X} {b - a:3d}b {T.decode(rec, a, b - a)[0]!r}")
        for i, why in errors[:10]:
            print(f"  ! {i:#06x} {why}")


if __name__ == "__main__":
    main()
