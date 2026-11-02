"""bmess.py: D_BMESS battle-message records: walk, list text, rebuild with new text.

    python -X utf8 tools/bmess.py            # coverage over every record (bytes the walk reaches)
    python -X utf8 tools/bmess.py 2          # one record: entry points, text units, unreached bytes

Grammar, from the walker at 0x800337F0..0x80033DBC (docs/re/text.md "D_BMESS"). Every offset is a u16 added to
its own address (unsigned, so always forward):
- header: 12 u16 at 0x00..0x16 (category picked from battle state: HP %, phase, ...), then at 0x18 two lists of
  3-byte entries {u16 offset, u8 character id}, each ending with FFFF (the game scans them for the speaker).
- bytecode from each target, copied to an output buffer until FF:
  F0-FA xx = two-byte glyph; other bytes < FF except FC = one byte (glyph, FB, FD nl, FE page);
  FC a 3F = random pick: u16 list (self-relative entries) up to FFFF, jump to one; no fall-through;
  FC lo 3x hi = 5 bytes, x 0-7: flag ((x & 3) << 8 | lo) test (0x80036E2C); x < 4 jumps when clear, x >= 4
            when set; the u16 at +3 is the target; else fall through;
  FC a 3C b c = 5 bytes, inline face change; FC a b = 3 bytes, other control (speaker 01 4x, ...);
  FF = end.
The game loads up to four records at 0x3000 strides of one 0xC000 heap block (0x80069980), so a record must
stay <= RECORD_MAX (a build with battle text raises the stride: insert.BM_STRIDE).
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import arc  # noqa: E402

RECORD_MAX = 0x3000
HDR_FIELDS = 12


def u16(r, p):
    return struct.unpack_from("<H", r, p)[0]


def header_fields(r):
    """[(field position, target)] of the header: 12 offsets, then the two 3-byte speaker lists."""
    out = [(2 * i, 2 * i + u16(r, 2 * i)) for i in range(HDR_FIELDS)]
    p = 2 * HDR_FIELDS
    for _ in range(2):
        while p + 2 <= len(r) and u16(r, p) != 0xFFFF:
            out.append((p, p + u16(r, p)))
            p += 3
        p += 2
    return out, p


def walk(r):
    """Walk every reachable instruction. Returns (ins, fields, hdr_end): ins = {pos: (kind, length)} with kind
    'text' (one glyph or FB/FD/FE), 'ctl' (FC 3-/5-byte, kept inside text), 'jump', 'list', 'end';
    fields = [(field position, target)] for every self-relative u16 in the record."""
    fields, hdr_end = header_fields(r)
    todo = [t for _, t in fields if hdr_end <= t < len(r)]
    ins = {}
    while True:
        if not todo:   # messages no offset reaches (dead text) still start right after an FF: walk them too
            todo = [p + 1 for p, (k, _) in ins.items() if k == "end" and p + 1 < len(r) and p + 1 not in ins
                    and r[p + 1]]
            if not todo:
                break
        p = todo.pop()
        while hdr_end <= p < len(r) and p not in ins:
            b = r[p]
            if b == 0xFF:
                ins[p] = ("end", 1)
                break
            if b != 0xFC:
                n = 2 if 0xF0 <= b <= 0xFA else 1
                ins[p] = ("text", n)
                p += n
                continue
            c = r[p + 2]
            if c == 0x3F:
                q = p + 3
                if r[q] == 0xFC:   # slot 113 0x1952: a jump op sits between FC 00 3F and the entries (the game
                    fields.append((q + 3, q + 3 + u16(r, q + 3)))  # reads garbage there); keep its pointer
                    todo.append(q + 3 + u16(r, q + 3))
                    q += 5
                while u16(r, q) != 0xFFFF:
                    fields.append((q, q + u16(r, q)))
                    todo.append(q + u16(r, q))
                    q += 2
                ins[p] = ("list", q + 2 - p)
                break
            if 0x30 <= c <= 0x37:
                fields.append((p + 3, p + 3 + u16(r, p + 3)))
                todo.append(p + 3 + u16(r, p + 3))
                ins[p] = ("jump", 5)
                p += 5
                continue
            n = 5 if c == 0x3C else 3
            ins[p] = ("ctl", n)
            p += n
    return ins, fields, hdr_end


def texts(r):
    """[(start, end)] text units: runs of text/ctl instructions, split at every branch target, ending before
    the FF (or jump/list) that closes them."""
    ins, fields, _ = walk(r)
    targets = {t for _, t in fields}
    out, start = [], None
    for p in sorted(ins):
        kind, n = ins[p]
        if start is not None and (kind not in ("text", "ctl") or p in targets or p != last):
            out.append((start, last))
            start = None
        if kind in ("text", "ctl"):
            if start is None:
                start = p
            last = p + n
    if start is not None:
        out.append((start, last))
    return out


def rebuild(r, edits, limit=RECORD_MAX):
    """New record with edits {unit start: new bytes} (each replacing a unit from texts()); every offset field
    is re-aimed. Fails on a target that is not a unit boundary, an offset past u16, or a record > RECORD_MAX."""
    units = dict(texts(r))
    _, fields, _ = walk(r)
    bad = [s for s in edits if s not in units]
    if bad:
        raise ValueError(f"edits at {bad[:3]} are not text units")
    out, mp, p = bytearray(), {}, 0
    for s in sorted(edits):
        out += r[p:s]
        for q in range(p, s + 1):
            mp[q] = q + len(out) - s
        out += edits[s]
        p = units[s]
    shift = len(out) - p
    for q in range(p, len(r) + 1):
        mp[q] = q + shift
    out += r[p:]
    inside = {q for s in edits for q in range(s + 1, units[s])}
    for f, t in fields:
        if t in inside or f in inside:
            raise ValueError(f"field {f:#x} -> {t:#x} lands inside an edited unit")
        v = mp[t] - mp[f]
        if not 0 <= v <= 0xFFFE:
            raise ValueError(f"field {f:#x}: offset {v:#x} does not fit a u16")
        struct.pack_into("<H", out, mp[f], v)
    if len(out) > limit:
        raise ValueError(f"record {len(out):#x} > {limit:#x} (its load slot)")
    return bytes(out)


def records():
    """[(first slot, record bytes)] of D_BMESS, aliases once."""
    d = (ROOT / "work/disc/tree/D_BMESS.BIN").read_bytes()
    seen, out = set(), []
    for slot, (s, e) in enumerate(arc.entries(d)):
        if s not in seen:
            seen.add(s)
            out.append((slot, d[s:e]))
    return out


def main():
    from tbl import Table
    T = Table.load(ROOT / "tbl/jp.tbl")
    show = int(sys.argv[1]) if len(sys.argv) > 1 else None
    tot = cov = nunits = 0
    for slot, r in records():
        ins, fields, hdr_end = walk(r)
        c = hdr_end + sum(n for _, n in ins.values())
        tot, cov = tot + len(r), cov + c
        units = texts(r)
        nunits += len(units)
        if show == slot:
            print(f"slot {slot} len {len(r):#x} hdr_end {hdr_end:#x} fields {len(fields)} units {len(units)}")
            for s, e in units[:20]:
                print(f"   {s:#06x} {T.decode(r, s, e - s)[0][:70]}")
            seen = bytearray(len(r))
            seen[:hdr_end] = b"\1" * hdr_end
            for p, (_, n) in ins.items():
                seen[p:p + n] = b"\1" * n
            j = 0
            while j < len(r):
                if not seen[j]:
                    k = j
                    while k < len(r) and not seen[k]:
                        k += 1
                    print(f"   gap {j:#x}..{k:#x}: {r[j:min(k, j + 24)].hex(' ')}")
                    j = k
                j += 1
    print(f"{len(records())} records, {nunits} text units, walked {cov}/{tot} bytes")


if __name__ == "__main__":
    main()
