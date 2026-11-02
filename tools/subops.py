"""subops.py: audit the VM's sub-op dispatchers (ops whose 2nd byte picks a handler) against vm.SUBK.

    python -X utf8 tools/subops.py            # every sub-handler that writes the VM advance (state+0x48)

For each write of state+0x48 in a sub-handler it prints how the value is formed:
  add K     lw 0x48 .. addiu K .. sw 0x48           -> the op is LEN + K bytes long (vm.SUBK = K)
  branch K  lbu a; lbu b; sll 8; or; sll 16; sra 16; addiu K; sw 0x48
            -> a relative branch: target = op + s16 + K; the bytes it reads give the operand offset
  set K     addiu/ori K straight into 0x48 (absolute length)
A sub-op with a `branch` needs its offset operand rewritten when text grows (patch.operand_fields).
Found this way: 5C sub 20 is `5C 14 <8 args> <s16>` (cond branch, fallthrough 12 = LEN 5 + 7); the first SUBK
derivation took the branch's `+0xA` for the length.
"""
import importlib.util
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
_s = importlib.util.spec_from_file_location("vmre", ROOT / "tools/re.py")
R = importlib.util.module_from_spec(_s)
_s.loader.exec_module(R)
import vm  # noqa: E402


def sub_table(op):
    """RAM address of the sub-handler table the dispatcher for `op` indexes (lui/addiu pair in its body)."""
    body = R.handler_body(R.handlers()[op])
    hi = {}
    for ins in body:
        if ins.mnemonic == "lui":
            reg, imm = ins.op_str.split(", ")
            hi[reg] = int(imm, 0) << 16
        elif ins.mnemonic == "addiu":
            d, s, imm = ins.op_str.split(", ")
            if s in hi:
                a = (hi[s] + int(imm, 0)) & 0xFFFFFFFF
                if 0x800C0000 <= a < 0x800CC000:
                    return a
    return None


def classify(body):
    out = []
    for k, ins in enumerate(body):
        if ins.mnemonic != "sw" or "0x48(" not in ins.op_str:
            continue
        prev = body[max(0, k - 8):k]
        names = [p.mnemonic for p in prev]
        kimm = None
        for p in reversed(prev):
            if p.mnemonic in ("addiu", "ori"):
                kimm = int(p.op_str.split(", ")[-1], 0)
                break
        if "sra" in names:
            out.append(("branch", kimm))
        elif any(p.mnemonic == "lw" and "0x48(" in p.op_str for p in prev):
            out.append(("add", kimm))
        else:
            out.append(("set", kimm))
    return out


def audit():
    rows = []
    for op in sorted(vm.SUBK):
        t = sub_table(op)
        if t is None:
            rows.append((op, None, "no table found", None))
            continue
        for sub in range(64):
            h = R.u32(t + 4 * sub)
            if not 0x80010000 <= h < 0x800C0000:
                break
            body = R.handler_body(h, 600)
            rows.append((op, sub, classify(body), vm.SUBK[op].get(sub)))
    return rows


if __name__ == "__main__":
    for op, sub, kinds, known in audit():
        if not kinds or kinds == "no table found":
            if kinds:
                print(f"{op:02X}: {kinds}")
            continue
        flag = ""
        adds = [k for kind, k in kinds if kind == "add"]
        if any(kind == "branch" for kind, _ in kinds):
            flag = "  <-- BRANCH"
        elif adds and known != adds[0]:
            flag = f"  <-- SUBK has {known}"
        elif not adds and known:
            flag = f"  <-- SUBK has {known}, no add found"
        print(f"{op:02X} sub {sub:2d}: {kinds}{flag}")
