"""check.py: the one-command check (tests + extraction gate). The pre-commit hook runs it; exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

steps = [[sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")],
         # roundtrip + coverage of script/ (skip while the disc is not unpacked yet)
         [sys.executable, "-X", "utf8", str(ROOT / "tools" / "extract.py"), "check"]]
if not (ROOT / "work/disc/tree/D_SCE.BIN").exists():
    steps = steps[:1]
lint = ROOT / "tools" / "lint.py"
if lint.exists():
    steps.append([sys.executable, "-X", "utf8", str(lint)])

for cmd in steps:
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode:
        sys.exit(f"check failed: {' '.join(cmd[2:])}")
print("check ok")
