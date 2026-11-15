"""Prints a Markdown summary of the test cycles (used by the GitHub Actions workflow).

Reads reports/bug_log_*.csv written by tests/conftest.py. Never fails the build by itself;
it only makes the results (and the real error messages) visible on the run's Summary page.
"""
import csv
import glob
import os

ORDER = ["cycle1_buggy_full", "cycle2_fixed_retest", "cycle3_fixed_regression"]
TITLES = {
    "cycle1_buggy_full": "Cycle 1 - full suite on v1.0 (failures are expected)",
    "cycle2_fixed_retest": "Cycle 2 - retest of the defect cases on v1.1",
    "cycle3_fixed_regression": "Cycle 3 - full regression on v1.1",
}


def load(tag):
    path = os.path.join("reports", f"bug_log_{tag}.csv")
    if not os.path.exists(path):
        return None
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


print("## Selenium test cycles\n")
print("| Cycle | Executed | Passed | Failed | Defects exposed |")
print("|---|---|---|---|---|")
details = []
for tag in ORDER:
    rows = load(tag)
    if rows is None:
        print(f"| {TITLES[tag]} | no log produced | | | |")
        details.append((tag, None))
        continue
    failed = [r for r in rows if r["outcome"] != "PASSED"]
    defects = sorted({r["linked_defect"] for r in failed if r["linked_defect"]})
    print(f"| {TITLES[tag]} | {len(rows)} | {len(rows) - len(failed)} | {len(failed)} | {len(defects)} {', '.join(defects)} |")
    details.append((tag, failed))

c1 = load("cycle1_buggy_full")
if c1:
    exposed = {r["linked_defect"] for r in c1 if r["outcome"] != "PASSED" and r["linked_defect"]}
    unlinked = [r["test_id"] for r in c1 if r["outcome"] != "PASSED" and not r["linked_defect"]]
    print(f"\nDesign check for cycle 1: {len(exposed)} of 8 seeded defects exposed; "
          f"{len(unlinked)} failure(s) not linked to a seeded defect.")

LOGS = {"cycle1_buggy_full": "log_cycle1.txt", "cycle2_fixed_retest": "log_cycle2.txt", "cycle3_fixed_regression": "log_cycle3.txt"}


def pytest_failure_lines(tag):
    """The 'FAILED ... - message' lines pytest prints in its short summary (-ra)."""
    path = os.path.join("reports", LOGS[tag])
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as fh:
        return [ln.strip() for ln in fh if ln.startswith(("FAILED ", "ERROR "))]


for tag, failed in details:
    if not failed:
        continue
    print(f"\n### Failures in {tag}\n")
    lines = pytest_failure_lines(tag)
    if lines:
        for ln in lines[:15]:
            print(f"- `{ln[:230]}`")
    else:
        for r in failed[:15]:
            print(f"- `{r['test_id']}` ({r['linked_defect'] or 'no linked defect'}): {r['failure_detail'][:200]}")
if all(rows is None for _, rows in details):
    print("\nNo test log was produced. Open the failed step above and read its last lines: "
          "the error is usually in installing the dependencies or in starting Chrome.")
