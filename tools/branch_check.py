"""For each candidate sub-op branch form, how often does the target land on an instruction start of the decode?"""
import sys, collections
sys.path.insert(0, "tools")
import vm, patch

FORMS = {  # (op, sub): (disp pos, bias)
    (0x16, 19): (3, 3), (0x16, 25): (2, 2), (0x5C, 20): (10, 10),
    **{(0xC8, s): (2, 2) for s in (0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 19, 20, 21)},
    **{(0xDC, s): (2, 2) for s in (3, 4, 5)},
}
TOP = {0x3A: (1, 1), 0x55: (1, 1), 0xF9: (1, 1), 0xD2: (3, 3), 0xDB: (3, 3), 0xD3: (5, 5), 0x15: (1, 1),
       0x33: (1, 1), 0x56: (1, 1), 0x6B: (1, 1), 0xD1: (3, 3)}
# 0E n <s16 self-relative> (n < 6): pointer = operand position + s16
e_hit = e_miss = 0
for slot, rec in vm.sce_records():
    ins, _ = patch.decode(rec)
    so = {it.off for it in ins}
    for it in ins:
        if it.op == 0x0E and it.kind == "op" and it.off + 4 <= len(rec):
            n = rec[it.off + 1]
            ps = [it.off + 2] if n < 6 else [it.off + 2 + 2 * k for k in range(6)]
            for p in ps:
                if p + 2 > len(rec):
                    continue
                t = p + vm.s16(rec[p], rec[p + 1])
                if t in so:
                    e_hit += 1
                else:
                    e_miss += 1
print("0E", e_hit, e_miss)
hit, miss, ex = collections.Counter(), collections.Counter(), {}
skips = 0
for slot, rec in vm.sce_records():
    ins, starts = patch.decode(rec)
    cov = 0
    for it in ins:
        cov += it.ln
    skips += len(rec) - cov
    so = {it.off for it in ins}
    for it in ins:
        if it.kind != "op" or it.ln < 2:
            continue
        key = (it.op, rec[it.off + 1])
        if it.op in TOP:
            key = (it.op, -1)
            p, b = TOP[it.op]
        elif key not in FORMS:
            continue
        else:
            p, b = FORMS[key]
        if it.off + p + 2 > len(rec):
            continue
        t = it.off + vm.s16(rec[it.off + p], rec[it.off + p + 1]) + b
        if t in so:
            hit[key] += 1
        else:
            miss[key] += 1
            ex.setdefault(key, (slot, it.off, t, rec[it.off:it.off + it.ln].hex(" ")))
print("undecoded bytes", skips)
for k in sorted(set(hit) | set(miss)):
    print(f"{k[0]:02X}/{k[1]:2d} hit {hit[k]:5d} miss {miss[k]:4d}", ex.get(k, ""))
