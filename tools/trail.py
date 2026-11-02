"""trail.py: VM handlers that branch through helper 0x8005832C (a table of self-relative s16s right after the
instruction; a0 = the entry index). Run from the repo root:

    python -X utf8 tools/trail.py      # op[/sub], table length, a0 per call site, `add K` advances, vm.SUBK

docs/re/text.md "trailing offset tables". '?…' = the index comes from a register (read the handler)."""
import sys
sys.path.insert(0, "tools")
import subops, vm
R = subops.R
HELP = "0x8005832c"


def analyse(h):
    body = R.handler_body(h, 800)
    idx = []
    for k, ins in enumerate(body):
        if ins.mnemonic == "jal" and ins.op_str == HELP:
            a0 = None
            for p in [body[k + 1]] + list(reversed(body[max(0, k - 4):k])):
                if p.op_str.startswith("$a0, "):
                    if p.mnemonic == "move" and p.op_str == "$a0, $zero":
                        a0 = 0
                    elif p.mnemonic in ("addiu", "ori") and "$zero" in p.op_str:
                        a0 = int(p.op_str.split(", ")[-1], 0)
                    else:
                        a0 = "?" + p.mnemonic + " " + p.op_str
                    break
            idx.append(a0)
    adds = []
    for k, ins in enumerate(body):
        if ins.mnemonic == "sw" and "0x48(" in ins.op_str and "$sp" not in ins.op_str:
            prev = body[max(0, k - 4):k]
            if any(p.mnemonic == "lw" and "0x48(" in p.op_str for p in prev):
                K = next((int(p.op_str.split(", ")[-1], 0) for p in reversed(prev) if p.mnemonic == "addiu"), None)
                adds.append(K)
    return idx, adds


rows = []
H = R.handlers()
for op in range(256):
    idx, adds = analyse(H[op])
    if idx:
        rows.append((f"{op:02X}", vm.LEN[op], idx, adds, None))
for op in sorted(vm.SUBK):
    t = subops.sub_table(op)
    for s in range(64):
        h = R.u32(t + 4 * s)
        if not 0x80010000 <= h < 0x800C0000:
            break
        idx, adds = analyse(h)
        if idx:
            rows.append((f"{op:02X}/{s}", vm.LEN[op], idx, adds, vm.SUBK[op].get(s)))
for r in rows:
    print(*r)
