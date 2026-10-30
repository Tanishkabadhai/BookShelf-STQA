"""Runs the three test cycles of the regression demonstration (needs Chrome installed).

  Cycle 1  buggy build v1.0 - full suite            -> defects detected
  Cycle 2  fixed build v1.1 - re-run failed tests   -> retesting (--lf)
  Cycle 3  fixed build v1.1 - full suite            -> regression testing
Reports: reports/cycle*.html (pytest-html) and reports/bug_log_cycle*.csv
"""
import os
import subprocess
import sys

CYCLES = [
    ("cycle1_buggy_full", "buggy", []),
    ("cycle2_fixed_retest", "fixed", ["--lf"]),
    ("cycle3_fixed_regression", "fixed", []),
]

for tag, mode, extra in CYCLES:
    env = dict(os.environ, APP_MODE=mode, REPORT_TAG=tag)
    cmd = [sys.executable, "-m", "pytest", f"--html=reports/{tag}.html", "--self-contained-html", *extra]
    print(f"\n=== {tag} (APP_MODE={mode}) ===")
    subprocess.run(cmd, env=env)   # cycle 1 is EXPECTED to fail
