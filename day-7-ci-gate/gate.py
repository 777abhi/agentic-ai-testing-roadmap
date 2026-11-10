"""Day 7: release gate. Runs every day's suite and exits non-zero if any fails."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAYS = ["day-1-tool-contracts", "day-2-trajectory-eval", "day-3-mcp-server", "day-4-red-teaming",
        "day-5-multi-agent", "day-6-budgets"]


def run_gate():
    results = {}
    for d in DAYS:
        p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / d)],
                           cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT)}, capture_output=True, text=True)
        results[d] = {"passed": p.returncode == 0, "tail": p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""}
    return results


if __name__ == "__main__":
    res = run_gate()
    (ROOT / "gate-report.json").write_text(json.dumps(res, indent=2))
    for d, r in res.items():
        print(("PASS " if r["passed"] else "FAIL ") + d + "  " + r["tail"])
    ok = all(r["passed"] for r in res.values())
    print("GATE:", "OPEN ✅" if ok else "CLOSED ❌")
    sys.exit(0 if ok else 1)
