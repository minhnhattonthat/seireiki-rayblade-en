"""Thingy-style table codec with control codes, hex escapes and multi-byte keys.

Table lines: `XX=あ`, `XXYY=漢`, `00=\\s` (space), control codes `F0={end}`, `F1={wait:1}` (1 argument byte). Unknown bytes decode
as `[XX]` and encode back, so decode -> encode is byte-exact: the basis of the extraction roundtrip test.

    from tbl import Table
    t = Table.load("tbl/jp.tbl"); text, used = t.decode(rom, 0x1234A); assert t.encode(text) == rom[0x1234A:0x1234A + used]
"""
import re
from pathlib import Path

CTRL = re.compile(r"\{(\w+)(?::(\d+))?\}$")
TERMINATORS = {"end", "goto"}  # decoding stops after these (goto = unconditional jump)
TOKEN = re.compile(r"\{(\w+)(?::([0-9A-Fa-f]*))?\}|\[([0-9A-Fa-f]{2})\]")


class Table:
    def __init__(self, lines):
        self.dec, self.ctrl, self.enc, self.ctrl_enc, self.pats = {}, {}, {}, {}, []
        for n, line in enumerate(lines, 1):
            line = line.rstrip("\r\n")
            if not line or line.startswith("#"):
                continue
            key, sep, val = line.partition("=")
            val = " " if val == r"\s" else val  # `00=\s` = space; editors and strip() eat a literal trailing space
            if not sep or not val:
                raise ValueError(f"table line {n}: bad entry {line!r} (write a space value as {key}=\\s)")
            m = CTRL.match(val)
            if "??" in key:
                # `FC??3C={face:2}`: a control whose key has wildcard bytes; they print before the arg bytes
                if not m:
                    raise ValueError(f"table line {n}: a ?? key must be a control code")
                pat = [None if key[i:i + 2] == "??" else int(key[i:i + 2], 16) for i in range(0, len(key), 2)]
                self.pats.append((pat, m[1], int(m[2] or 0)))
                self.ctrl_enc.setdefault(m[1], (pat, int(m[2] or 0)))
                continue
            code = bytes.fromhex(key)
            if m:
                argc = int(m[2] or 0)
                self.ctrl[code] = (m[1], argc)
                self.ctrl_enc.setdefault(m[1], (code, argc))
            else:
                self.dec[code] = val
                self.enc.setdefault(val, code)
        self.keylen = max(map(len, (*self.dec, *self.ctrl)), default=1)
        self.vallen = max(map(len, self.enc), default=1)

    @classmethod
    def load(cls, path):
        return cls(Path(path).read_text(encoding="utf-8-sig").splitlines())

    def decode(self, data, pos=0, length=None, maxlen=4096):
        """length=None: decode through {end}/{goto}. Else decode exactly `length` bytes. Returns (text, consumed)."""
        start, out = pos, []
        stop = len(data) if length is None else pos + length
        while pos < stop:
            if length is None and pos - start >= maxlen:
                raise ValueError(f"no {{end}} within {maxlen} bytes of {start:#x}")
            hit = self._match_pat(data, pos, stop)
            if hit:
                name, args, n = hit
                out.append(f"{{{name}:{args.hex().upper()}}}")
                pos += n
                continue
            for k in range(min(self.keylen, stop - pos), 0, -1):
                code = bytes(data[pos:pos + k])
                if code in self.ctrl:
                    name, argc = self.ctrl[code]
                    args = bytes(data[pos + k:pos + k + argc])
                    pos += k + argc
                    out.append(f"{{{name}:{args.hex().upper()}}}" if argc else f"{{{name}}}")
                    if name in TERMINATORS and length is None:
                        return "".join(out), pos - start
                    break
                if self.enc.get(self.dec.get(code)) == code:
                    out.append(self.dec[code])
                    pos += k
                    break
            else:
                out.append(f"[{data[pos]:02X}]")
                pos += 1
        if length is None:
            raise ValueError(f"ran off end of data decoding from {start:#x}")
        return "".join(out), pos - start

    def _match_pat(self, data, pos, stop):
        """(name, wildcard bytes + arg bytes, length) of the ?? control at pos, or None."""
        for pat, name, argc in self.pats:
            n = len(pat) + argc
            if pos + n > stop or any(b is not None and data[pos + i] != b for i, b in enumerate(pat)):
                continue
            wild = bytes(data[pos + i] for i, b in enumerate(pat) if b is None)
            return name, wild + bytes(data[pos + len(pat):pos + n]), n
        return None

    def encode(self, text: str) -> bytes:
        out, i = bytearray(), 0
        while i < len(text):
            m = TOKEN.match(text, i)
            if m:
                if m[3]:
                    out.append(int(m[3], 16))
                else:
                    if m[1] not in self.ctrl_enc:
                        raise ValueError(f"unknown control {{{m[1]}}} at {i} in {text!r}")
                    code, argc = self.ctrl_enc[m[1]]
                    args = bytes.fromhex(m[2] or "")
                    if isinstance(code, list):          # ?? pattern: wildcards first, then the arg bytes
                        nw = code.count(None)
                        if len(args) != nw + argc:
                            raise ValueError(f"{{{m[1]}}} needs {nw + argc} bytes at {i} in {text!r}")
                        w = iter(args[:nw])
                        out += bytes(next(w) if b is None else b for b in code) + args[nw:]
                        i = m.end()
                        continue
                    if len(args) != argc:
                        raise ValueError(f"{{{m[1]}}} needs {argc} arg bytes at {i} in {text!r}")
                    out += code + args
                i = m.end()
                continue
            for k in range(min(self.vallen, len(text) - i), 0, -1):
                if text[i:i + k] in self.enc:
                    out += self.enc[text[i:i + k]]
                    i += k
                    break
            else:
                raise ValueError(f"unencodable {text[i]!r} at {i} in {text!r}")
        return bytes(out)


if __name__ == "__main__":
    t = Table(["10=あ", "11=い", "8001=漢", "20=A", "F1={wait:1}", "F0={end}"])
    data = b"\x10\x8a\x80\x01\xf1\x05\x20\xf0"
    text, used = t.decode(data)
    assert text == "あ[8A]漢{wait:05}A{end}" and used == len(data), text
    assert t.encode(text) == data
    s = Table(["00=\\s", "20=A"])
    assert s.decode(b"\x20\x00\x20", length=3)[0] == "A A" and s.encode("A A") == b"\x20\x00\x20"
    p = Table(["20=A", "FC={ctl:2}", "FC??3C={face:2}", "FF={end}"])
    raw = b"\xfc\x04\x3c\xff\x10\x20\xfc\x3c\x3e\xff"
    assert p.decode(raw)[0] == "{face:04FF10}A{ctl:3C3E}{end}", p.decode(raw)
    assert p.encode(p.decode(raw)[0]) == raw
    print("selftest ok")
