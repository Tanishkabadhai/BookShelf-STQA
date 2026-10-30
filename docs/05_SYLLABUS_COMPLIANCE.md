# Syllabus Compliance Checklist (SPPU 2019 Pattern - Software Testing and Quality Assurance)
Only topics that appear in the supplied syllabus are claimed. "Where" points to the file in this project.

| Unit | Syllabus topic (as listed) | Where demonstrated | Status |
|---|---|---|---|
| I | Objectives of testing; Testing vs Debugging; Why software has errors; Defects, failures, causes and effects | Test Plan s1; Bug taxonomy (cause column); seeded defects fixed in v1.1 | Covered |
| II | Test plan - purpose and contents; strategy and approach | `01_TEST_PLAN.md` s1-s5 | Covered |
| II | Test cases and test data; entry-exit criteria; execution schedule | TC01-TC18 + data table; Test Plan s5-s7 | Covered |
| II | Test metrics - coverage, productivity, efficiency, defect acceptance/rejection, effort & schedule variance | Formulas in Test Plan s8; values come from your real CSV logs | Covered (values to be filled from real run) |
| II | Test report, Test monitoring & control | `reports/*.html`, `bug_log_*.csv`, cycle plan | Covered |
| III | Black box testing | whole Selenium suite (UI-only, no code knowledge) | Covered |
| III | Equivalence Class Partition; Boundary Value Analysis | TC02, TC03, TC04, TC11 | Covered |
| III | Error guessing; Exploratory testing | `04_EXPLORATORY_TESTING.md` | Covered (sessions must be performed by you) |
| III | System testing; Sanity/Smoke; Regression; Retest | `-m smoke`, cycles 1-3 | Covered |
| III | Non-functional: Cookies testing, Session testing | TC09, TC10 (BUG-07) | Partly (only session/cookie aspects) |
| V | Automation testing process, benefits, choosing tools; automation frameworks | `03_REGRESSION_SCRIPTS.md` s3; helper/test/report layers | Covered |
| V | Selenium WebDriver; Selenium IDE | `tests/`, `ide/BookShelf.side` | Covered |
| I/II/VI | Defect-related terms ("bug taxonomy", severity, priority, life cycle) | `02_BUG_TAXONOMY_AND_REGISTER.md` | **Supporting terminology.** The topic requires a bug taxonomy; the syllabus lists defects/causes (Unit I) and defect acceptance/rejection (Unit II) but not a named taxonomy, so the category scheme is a standard practice used to organise those. |
| VI | Pareto diagram of defects | Doc 02 s4 | **Optional**, not implemented |

## Not covered (gaps, intentionally)
- Unit I/IV/VI theory (TQM, ISO/CMM, Six Sigma, SQA plan, quality models): not part of the assigned topic; prepare for viva from notes.
- Unit III white-box coverage techniques, performance, security (beyond session), installation testing: out of the topic.
- Unit V Selenium RC/Grid, SoapUI, Tosca, Appium, JMeter: not needed for the topic.

## Out-of-syllabus implementation tools (necessary only to build/run the AUT and scripts)
Python, Flask, SQLite, pytest and pytest-html (test runner/report). They are *tools*, not academic concepts; no extra theory is introduced. Selenium WebDriver itself is bound to Python as one of its supported languages.
