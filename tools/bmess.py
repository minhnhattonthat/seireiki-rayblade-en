"""Explore D_BMESS: find FC 00 3F u16 lists (relative to list start, FF FF end) and the messages they point at."""
import sys, struct, collections
sys.path.insert(0, "tools")
import arc, vm
from tbl import Table
T = Table.load("tbl/jp.tbl")
d = open("work/disc/tree/D_BMESS.BIN", "rb").read()
E = arc.entries(d)
show = int(sys.argv[1]) if len(sys.argv) > 1 else -1
tot_cov = tot = 0
ops = collections.Counter()
seen = set()
for slot, (s, e) in enumerate(E):
    if s in seen:
        continue
    seen.add(s)
    r = d[s:e]
    hdr = struct.unpack_from("<H", r, 0)[0]
    cats = [struct.unpack_from("<H", r, 2 * i)[0] for i in range(hdr // 2)] if hdr < 0x80 else []
    cov = bytearray(len(r))
    cov[:hdr] = b"\x01" * hdr
    msgs = set()
    i = 0
    lists = 0
    while True:
        i = r.find(b"\xfc\x00\x3f", i)
        if i < 0:
            break
        base, k, offs = i + 3, i + 3, []
        while k + 2 <= len(r) and r[k:k + 2] != b"\xff\xff":
            offs.append(struct.unpack_from("<H", r, k)[0])
            k += 2
        cov[i:k + 2] = b"\x01" * (k + 2 - i)
        lists += 1
        for o in offs:
            msgs.add(base + o)
        i = k + 2
    for m in sorted(msgs):
        end = vm.text_end(r, m) if m < len(r) else None
        if end is None:
            continue
        cov[m:end + 1] = b"\x01" * (end + 1 - m)
    c = sum(cov)
    tot += len(r)
    tot_cov += c
    if slot == show or show == -2:
        print(f"slot {slot} len {len(r):#x} hdr {hdr:#x} cats {[hex(x) for x in cats]} lists {lists} msgs {len(msgs)} cov {c}/{len(r)}")
        # uncovered runs
        j = 0
        while j < len(r):
            if not cov[j]:
                k = j
                while k < len(r) and not cov[k]:
                    k += 1
                print(f"   gap {j:#x}..{k:#x}: {r[j:min(k, j + 24)].hex(' ')}")
                j = k
            else:
                j += 1
        for m in sorted(msgs)[:5]:
            end = vm.text_end(r, m)
            print("   msg", hex(m), T.decode(r, m, end - m)[0][:60])
print("coverage", tot_cov, tot)
