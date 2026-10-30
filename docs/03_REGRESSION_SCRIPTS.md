# Regression Test Scripts and Procedure
*Syllabus: Unit III (Regression Test, Retest, Sanity/Smoke), Unit V (automation process, Selenium IDE, WebDriver)*

## 1. Definitions
- **Retest:** re-running the test cases that *failed* to confirm the defect fix.
- **Regression test:** re-running the *whole* suite on the new build to confirm that fixes did not break existing features.
- **Smoke/sanity:** quick check (`pytest -m smoke`) that the build is testable at all.

## 2. Script inventory
| Script | Tool | Purpose |
|---|---|---|
| `tests/test_bookshelf.py` | Selenium WebDriver + pytest | 18 test cases (28 instances) - the regression suite |
| `tests/helpers.py` | WebDriver | page actions (register, login, add book, search) |
| `tests/conftest.py` | pytest | starts AUT + Chrome, screenshots on failure, writes defect log CSV |
| `ide/BookShelf.side` | Selenium IDE | 4 recorded tests as suite "Regression" |
| `run_cycles.py` | Python | runs Cycle 1, 2, 3 automatically |
| `verify_modes.py` | Flask test client | browser-free check that seeded defects exist in v1.0 only |

## 3. Automated Process (Unit V)
1. Select scenarios worth automating (stable, repeatable, high value) - see Test Plan section 4.
2. Build scripts with reusable helpers (a simple automation framework: helper layer + test layer + reporting layer).
3. Execute -> collect results -> analyse failures -> log defects -> re-run.

## 4. How to run
```
pip install -r requirements.txt
python verify_modes.py                 # optional, no browser
python run_cycles.py                   # Cycles 1-3, needs Chrome
# or manually:
set APP_MODE=buggy&& pytest --html=reports/cycle1.html --self-contained-html     (Windows cmd)
APP_MODE=buggy pytest --html=reports/cycle1.html --self-contained-html           (Linux/macOS)
pytest -m smoke                        # smoke subset
```
Set `HEADLESS=0` to watch the browser. Optional: `BROWSER=firefox` runs the same suite in Firefox (Chrome is the default).

## 5. Selenium IDE procedure
1. Install the Selenium IDE extension in Chrome; start the app: `python app.py --mode buggy`.
2. In the IDE choose *Open an existing project* -> `ide/BookShelf.side`.
3. Run suite **Regression**. Expected on v1.0: IDE-01 passes; IDE-02, IDE-03, IDE-04 fail at the commented assertions.
4. Stop the app, start `--mode fixed`, run the suite again; all four are expected to pass.
5. Screenshot the IDE results panel for the report.

## 6. Cycle plan
| Cycle | Build | Tests | Purpose | Expected (design intent) |
|---|---|---|---|---|
| 1 | v1.0 | full | detect defects | 10 failing instances covering BUG-01..08 |
| 2 | v1.1 | previously failed (`--lf`) | retest | all pass |
| 3 | v1.1 | full | regression | all 28 pass |

These "expected" values come from the design and from `verify_modes.py`; replace them with your *actual* results from the CSV/HTML reports.
