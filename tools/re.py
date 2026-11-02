"""re.py: RE helpers for the PS1 EXE (capstone MIPS): disassemble, list VM opcode lengths and handlers.

    python -X utf8 tools/re.py ops                # opcode, length, handler, whether the handler writes the VM pc
    python -X utf8 tools/re.py dis 8006c3dc 40    # disassemble N instructions at a RAM address

Facts (docs/re/script.md): EXE base 0x80010000 at file 0x800; VM state struct 0x800CD570 (+0x40 script base,
+0x48 pc offset, +0x54 current instruction bytes); opcode length table 0x800C8480; handler table 0x800C8080.
"""
import struct
import sys
from pathlib import Path

import capstone

ROOT = Path(__file__).resolve().parents[1]
EXE = (ROOT / "work/disc/tree/SLPS_026.52").read_bytes()
BASE = 0x80010000
LEN_TABLE, HANDLERS = 0x800C8480, 0x800C8080


def off(addr):
    return addr - BASE + 0x800


def u32(addr):
    return struct.unpack_from("<I", EXE, off(addr))[0]


def lengths():
    return list(EXE[off(LEN_TABLE):off(LEN_TABLE) + 256])


def handlers():
    return list(struct.unpack_from("<256I", EXE, off(HANDLERS)))


def dis(addr, n):
    md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS32 + capstone.CS_MODE_LITTLE_ENDIAN)
    return list(md.disasm(EXE[off(addr):off(addr) + 4 * n], addr))


def handler_body(addr, limit=400):
    """Instructions from addr to the first `jr $ra` (plus delay slot)."""
    out = []
    for ins in dis(addr, limit):
        out.append(ins)
        if ins.mnemonic == "jr" and ins.op_str == "$ra":
            break
    return out


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dis":
        for ins in dis(int(sys.argv[2], 16), int(sys.argv[3]) if len(sys.argv) > 3 else 40):
            print(f"{ins.address:08X}  {ins.mnemonic:8s} {ins.op_str}")
    elif cmd == "xref":  # code that builds a RAM address: lui hi + addiu/ori/lw/sw lo (signed) within 12 words
        target = int(sys.argv[2], 16)
        hi, lo = (target + 0x8000) >> 16, target & 0xFFFF
        words = struct.unpack_from(f"<{(len(EXE) - 0x800) // 4}I", EXE, 0x800)
        for i, w in enumerate(words):
            if w >> 26 == 0x0F and w & 0xFFFF == hi:
                rt = (w >> 16) & 31
                for k in range(i + 1, min(i + 13, len(words))):
                    v = words[k]
                    if (v >> 21) & 31 == rt and v & 0xFFFF == lo and v >> 26 in (0x09, 0x0D, 0x20, 0x21, 0x23, 0x24,
                                                                                  0x25, 0x28, 0x29, 0x2B):
                        print(f"{BASE + 4 * i:08X} lui -> {BASE + 4 * k:08X}")
                        break
    elif cmd == "ops":
        L, H = lengths(), handlers()
        for op in range(256):
            body = handler_body(H[op])
            pcw = [i for i in body if i.mnemonic == "sw" and "0x48(" in i.op_str]
            calls = sorted({i.op_str for i in body if i.mnemonic == "jal"})
            print(f"{op:02X} len={L[op]:2d} h={H[op]:08X} n={len(body):3d} pcwrite={len(pcw)} calls={' '.join(calls)[:60]}")
