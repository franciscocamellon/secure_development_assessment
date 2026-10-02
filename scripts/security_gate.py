import json
import sys
from pathlib import Path

BANDIT_REPORT = Path(sys.argv[1] if len(sys.argv) > 1 else "bandit.json")

if not BANDIT_REPORT.exists():
    print("Security gate: bandit report missing")
    raise SystemExit(2)

report = json.loads(BANDIT_REPORT.read_text(encoding="utf-8"))
high = [item for item in report.get("results", []) if item.get("issue_severity") == "HIGH"]
if high:
    print(f"Security gate BLOCKED: {len(high)} HIGH severity Bandit finding(s).")
    for finding in high:
        print(f"- {finding.get('test_id')}: {finding.get('issue_text')} @ {finding.get('filename')}:{finding.get('line_number')}")
    raise SystemExit(1)
print("Security gate PASSED: no HIGH severity Bandit findings.")
