"""patch.py: rebuild a VM bytecode record after its inline text changes length.

    import patch
    new, off_map = patch.rebuild(old, {op_off: text_body_bytes})   # text_body excludes the FF terminator
    patch.verify(old, new, off_map)                                # control flow + text blocks unchanged

A record is the bytecode of one D_SCE scene (or a resident sub-script, or an EXE VM region). Text lives inline
behind op 0x78, so replacing a Japanese line with a longer English one shifts every byte after it, and with it
every offset operand in the record. rebuild() re-emits the record instruction by instruction and rewrites the
offset operands vm.py knows:

    01 rel s16, 02 abs u32, 03 call rel s16, 04 call abs u32, 07 repeat rel s16, 14 cond rel s16,
    7A choice item s16s

Instruction boundaries come from the control-flow walk first and the linear sweep second (decode()): the sweep
decodes unreachable padding as instructions, and such a bogus instruction can span a real instruction start,
which would leave a real operand unrewritten. Bytes that neither finds are copied through as raw bytes, so every
byte offset has a new home and nothing is lost.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import vm  # noqa: E402

KNOWN = {0x01, 0x02, 0x03, 0x04, 0x07, 0x14, vm.CHOICE}


class Instr:
    __slots__ = ("off", "ln", "kind", "op")

    def __init__(self, off, ln, kind, op):
        self.off, self.ln, self.kind, self.op = off, ln, kind, op

    def __repr__(self):
        return f"<{self.off:05X} {self.ln} {self.kind} {self.op:02X}>"


def sweep(rec):
    """[Instr] in file order: a linear decode, skipping bytes that do not decode."""
    ins, i = [], 0
    while i < len(rec):
        r = vm.insn_len(rec, i)
        if r is None:
            i += 1
            continue
        ln, kind = r
        ins.append(Instr(i, ln, kind, rec[i]))
        i += ln
    return ins


def decode(rec):
    """([Instr] we trust, {off: Instr}) — a consistent instruction partition of the record.

    Priority: a text block the linear sweep found is authoritative (extraction proved every one of them
    roundtrips, and a real branch never enters the middle of one), then the control-flow walk's boundaries,
    then the rest of the sweep. A walk instruction that would span a text block is bogus (the walk lost the
    thread in a data table) and its bytes become raw. Operand targets of trusted instructions that land in
    undecoded bytes are decoded too, so a jump into a byte run we could not decode still has an instruction."""
    sp = sweep(rec)
    texts = {it.off: it for it in sp if it.kind == "text"}
    walked, _ = vm.walk(rec)
    starts = {it.off: it for it in sp}
    for off, (ln, kind, op) in walked.items():
        if kind != "text" or off not in texts:
            starts.setdefault(off, Instr(off, ln, kind, rec[off]))
    starts.update(texts)
    text_off = sorted(texts)
    out, i = [], 0
    import bisect
    while i < len(rec):
        it = starts.get(i)
        cut = False
        if it is not None:
            k = bisect.bisect_right(text_off, i)
            cut = k < len(text_off) and text_off[k] < i + it.ln
        if it is None or cut:
            starts.pop(i, None)
            i += 1
            continue
        out.append(it)
        i += it.ln
    # a trusted instruction may jump into a byte run we could not decode: honour that boundary
    extra = {}
    for it in out:
        if it.off not in walked and it.off not in texts:
            continue
        for pos, width, target in operand_fields(rec, it):
            if (0 <= target < len(rec) and target not in starts and target not in texts
                    and vm.insn_len(rec, target)):
                extra[target] = vm.insn_len(rec, target)
    for target in sorted(extra):
        ln, kind = extra[target]
        if any(it.off < target < it.off + it.ln for it in out):
            continue
        starts[target] = Instr(target, ln, kind, rec[target])
        out.append(starts[target])
    out.sort(key=lambda it: it.off)
    return out, starts


def operand_fields(rec, it):
    """[(pos, width, target_old)] for the offset operands of one instruction."""
    o, n, op = it.off, it.ln, it.op
    out = []
    if op in (0x01, 0x03) and n >= 3:
        out.append((o + 1, 2, o + vm.s16(rec[o + 1], rec[o + 2]) + 1))
    elif op in (0x02, 0x04) and n >= 5:
        out.append((o + 1, 4, o + int.from_bytes(rec[o + 1:o + 5], "little") + 1))
    elif op == 0x07 and n >= 4:
        out.append((o + 2, 2, o + vm.s16(rec[o + 2], rec[o + 3]) + 2))
    elif op == 0x14 and n >= 3:
        out.append((o + 1, 2, o + vm.s16(rec[o + 1], rec[o + 2]) + 1))
    elif op == vm.CHOICE and n >= 2:
        for k in range(rec[o + 1]):
            p = o + 2 + 2 * k
            out.append((p, 2, p + vm.s16(rec[p], rec[p + 1])))
    return out


def _value(it, pos, target_new, new_off):
    """Operand value that makes the operand at `pos` point at target_new from instruction new_off."""
    op = it.op
    if op in (0x01, 0x02, 0x03, 0x04, 0x14):
        return target_new - new_off - 1
    if op == 0x07:
        return target_new - new_off - 2
    return target_new - (new_off + (pos - it.off))       # choice item: relative to the item itself


def rebuild(rec, edits, report=None):
    """New record bytes with each text block in `edits` replaced (key = text-op offset, value = body bytes).

    Returns (bytes, {old byte offset: new byte offset})."""
    ins, starts = decode(rec)
    by_off = {it.off: it for it in ins}
    for off in edits:
        it = by_off.get(off)
        if it is None or it.kind != "text":
            raise ValueError(f"{off:05X}: not a text block of this record (script/ out of date, or the block "
                             f"is inside a byte run the decoder does not trust)")
    out, mp, i = bytearray(), {}, 0
    ins_at = {it.off: it for it in ins}
    while i < len(rec):
        mp[i] = len(out)
        it = ins_at.get(i)
        if it is None:
            out.append(rec[i])
            i += 1
            continue
        if it.kind == "text" and i in edits:
            start, _ = vm.text_op(rec, i)
            out += rec[i:start] + edits[i] + b"\xff"
        else:
            out += rec[i:i + it.ln]
        i += it.ln
    mp[len(rec)] = len(out)
    for it in ins:
        new_off = mp[it.off]
        for pos, width, target_old in operand_fields(rec, it):
            t_new = mp.get(target_old)
            if t_new is None:
                if report is not None and 0 <= target_old < len(rec):
                    report.append(f"{it.off:05X} op {it.op:02X}: target {target_old:05X} has no new home")
                continue
            v = _value(it, pos, t_new, new_off)
            if width == 1:
                if not 0 <= v <= 0xFF:
                    raise ValueError(f"offset overflow: operand at {it.off:05X} needs {v}")
            else:
                lo, hi = (-(1 << 15), (1 << 15) - 1) if it.op in (0x01, 0x03, 0x07, 0x14, vm.CHOICE) else (0, (1 << 32) - 1)
                if not lo <= v <= hi:
                    raise ValueError(f"offset overflow: operand at {it.off:05X} to {target_old:05X} needs {v}")
            out[new_off + (pos - it.off):new_off + (pos - it.off) + width] = (v & ((1 << (8 * width)) - 1)).to_bytes(width, "little")
    return bytes(out), mp


def verify(old, new, mp, report=None):
    """Fail unless the rebuilt record decodes to the same instruction graph as the original."""
    oi, _ = decode(old)
    ni, _ = decode(new)
    if len(oi) != len(ni):
        raise AssertionError(f"instruction count {len(oi)} -> {len(ni)}")
    for a, b in zip(oi, ni):
        if a.kind != b.kind or a.op != b.op:
            raise AssertionError(f"instruction {a.off:05X} changed kind: {a!r} -> {b!r}")
        if b.off != mp.get(a.off):
            raise AssertionError(f"instruction {a.off:05X} at {b.off:05X}, expected {mp.get(a.off):05X}")
        for pos, width, target in operand_fields(old, a):
            npos = b.off + (pos - a.off)
            if a.op in (0x02, 0x04):
                got = b.off + int.from_bytes(new[npos:npos + width], "little") + 1
            elif a.op == 0x07:
                got = b.off + vm.s16(new[npos], new[npos + 1]) + 2
            elif a.op == vm.CHOICE:
                got = npos + vm.s16(new[npos], new[npos + 1])
            else:
                got = b.off + vm.s16(new[npos], new[npos + 1]) + 1
            want = mp.get(target)
            if want is None:
                if report is not None:
                    report.append(f"{a.off:05X} op {a.op:02X}: target {target:05X} was not remapped")
                continue
            if got != want:
                raise AssertionError(f"{a.off:05X} op {a.op:02X}: target {target:05X} -> {got:05X}, want {want:05X}")
    return True


def unknown_offset_like(rec, report):
    """Report 2-byte values in unknown ops' argument bytes that resolve to an instruction start.

    A sub-op we have not decoded may carry an offset; if its value lands exactly on an instruction start it is
    almost certainly one, and the build must rewrite it (or the tour will show a hang)."""
    ins, starts = decode(rec)
    hits = 0
    for it in ins:
        if it.kind != "op" or it.op in KNOWN or it.ln < 3:
            continue
        for pos in range(it.off + 1, it.off + it.ln - 1):
            for bias in (0, 1, 2):
                for base in (pos, it.off):
                    t = base + vm.s16(rec[pos], rec[pos + 1]) + bias
                    if t in starts and t != it.off:
                        report.append(f"{it.off:05X} op {it.op:02X} arg @{pos - it.off}: -> {t:05X} (bias {bias}, base {base - it.off:+d})")
                        hits += 1
    return hits
