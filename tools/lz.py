"""lz.py: the game's LZ codec (EXE 0x80025574: a0 = dst, a1 = src). Compressed records = u32 LE size + stream.

Stream: flag bits read MSB-first from flag bytes, a new flag byte fetched when the previous 8 are used up.
  1            literal byte
  0 1  HI LO   long copy: v = HI<<8 | LO; offset = (v >> 3) - 0x2000; n = v & 7; n ? n + 2 : (next byte + 1);
               next byte 0 = end of stream
  0 0  b b  O  short copy: n = (bb) + 2 (2..5); offset = O - 0x100
Copies read from dst + offset (negative) and may overlap.

    python -X utf8 tools/lz.py test work/disc/tree/D_FACE.BIN     # decompress every record, recompress, roundtrip
"""
import struct
import sys


class _Bits:
    def __init__(self, src, pos):
        self.src, self.pos, self.flags, self.left = src, pos, 0, 0

    def bit(self):
        if self.left == 0:
            self.flags, self.left = self.src[self.pos], 8
            self.pos += 1
        self.left -= 1
        return (self.flags >> self.left) & 1

    def byte(self):
        b = self.src[self.pos]
        self.pos += 1
        return b


def decompress(src, pos=0, size=None):
    """Decompress a stream starting at src[pos] (after the u32 size). Returns (data, end_pos)."""
    r, out = _Bits(src, pos), bytearray()
    while True:
        if r.bit():
            out.append(r.byte())
            continue
        if r.bit():
            v = r.byte() << 8
            v |= r.byte()
            off, n = (v >> 3) - 0x2000, v & 7
            if n:
                n += 2
            else:
                c = r.byte()
                if c == 0:
                    break
                n = c + 1
        else:
            n = (r.bit() << 1 | r.bit()) + 2
            off = r.byte() - 0x100
        s = len(out) + off
        if s < 0:
            raise ValueError(f"copy before start at out {len(out):#x}")
        for i in range(n):
            out.append(out[s + i])
    if size is not None:
        # Some original streams (D_FACE) run past the header size with zero bytes before their end code;
        # the header size is the real data length.
        if len(out) < size or any(out[size:]):
            raise ValueError(f"size {len(out):#x} != header {size:#x}")
        del out[size:]
    return bytes(out), r.pos


def unpack_record(rec):
    size = struct.unpack_from("<I", rec)[0]
    return decompress(rec, 4, size)[0]


class _Writer:
    def __init__(self):
        self.out, self.flagpos, self.nbits = bytearray(), -1, 8

    def bit(self, b):
        if self.nbits == 8:
            self.flagpos, self.nbits = len(self.out), 0
            self.out.append(0)
        if b:
            self.out[self.flagpos] |= 0x80 >> self.nbits
        self.nbits += 1


def compress(data):
    """Greedy LZ with hash chains; output decompresses to `data` exactly (not byte-identical to the original tool)."""
    w, i, n = _Writer(), 0, len(data)
    heads = {}
    while i < n:
        best_len, best_off = 0, 0
        if i + 2 < n:
            key = data[i:i + 3]
            for j in reversed(heads.get(key, [])[-64:]):
                off = j - i
                if off < -0x2000:
                    break
                ln = 0
                while ln < 256 and i + ln < n and data[j + ln] == data[i + ln]:
                    ln += 1
                if ln > best_len:
                    best_len, best_off = ln, off
                    if ln == 256:
                        break
        if best_len >= 2 and best_off >= -0x100 and best_len <= 5 and not (best_len >= 3 and best_off < -0x100):
            w.bit(0); w.bit(0)
            k = best_len - 2
            w.bit(k >> 1); w.bit(k & 1)
            w.out.append(best_off + 0x100)
        elif best_len >= 3:
            w.bit(0); w.bit(1)
            v = (best_off + 0x2000) << 3
            if best_len <= 9:
                v |= best_len - 2
                w.out += bytes([v >> 8, v & 0xFF])
            else:
                w.out += bytes([v >> 8, v & 0xFF, best_len - 1])
        else:
            best_len = 1
            w.bit(1)
            w.out.append(data[i])
        for k in range(i, min(i + best_len, n - 2)):
            heads.setdefault(data[k:k + 3], []).append(k)
        i += best_len
    w.bit(0); w.bit(1)
    w.out += b"\x00\x00\x00"  # long copy with n = 0 and ext byte 0 = end
    return bytes(w.out)


def pack_record(data):
    return struct.pack("<I", len(data)) + compress(data)


if __name__ == "__main__":
    sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
    import arc
    path = sys.argv[2]
    d = open(path, "rb").read()
    ok = bad = 0
    for s, e in sorted(set(arc.entries(d))):
        rec = d[s:e]
        try:
            plain = unpack_record(rec)
        except Exception as x:  # noqa: BLE001 - report and continue: not every record is compressed
            bad += 1
            continue
        assert unpack_record(pack_record(plain)) == plain
        ok += 1
    print(f"{path}: {ok} records decompress + roundtrip, {bad} not LZ")
