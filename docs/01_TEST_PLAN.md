# Test Plan - BookShelf Web Application
*Syllabus: Unit II (Test Planning - artifacts, strategy, contents, entry/exit criteria, schedule, metrics)*

## 1. Purpose and objectives
Verify that BookShelf (a small Flask + SQLite web application where a registered user manages a personal list of books) behaves as specified, expose defects with Selenium WebDriver and Selenium IDE, and prove through regression testing that fixes do not break working features. (Unit I: objectives of testing.)

## 2. Application under test (AUT)
| Item | Detail |
|---|---|
| Platform / environment | Windows/Linux/macOS desktop, Python 3.10+, Google Chrome (latest) |
| Languages | Python (Flask, SQLite), HTML/CSS |
| Builds | **v1.0 (buggy)** - first build delivered for testing; **v1.1 (fixed)** - build after defect fixes |
| Why these choices | see `09_TECHNOLOGY_SELECTION.md` |
| Start command | `python app.py --mode buggy` / `python app.py --mode fixed` (http://127.0.0.1:5000) |

## 3. Features to be tested
| ID | Feature | Business rule (test oracle) |
|---|---|---|
| F1 | Registration | Valid email format; password >= 6 chars; email unique |
| F2 | Login / Logout | Correct, case-sensitive password; logout ends the session; /books needs login |
| F3 | Add book | Title required (<=100 chars); copies whole number **1-100**; no duplicate title (case-insensitive) per user |
| F4 | Search | Matches title or author, case-insensitive; "No books found." when empty |
| F5 | Edit book | Title, author and copies are all saved; same validation as F3 |
| F6 | Delete book | Removes only the selected book |
| F7 | Data privacy | A user sees only their own books |

**Not tested (out of scope):** performance/load, cross-browser, mobile layout, accessibility, password reset (not implemented).

## 4. Test strategy and approach
- **Level:** system-level, black-box functional testing through the browser UI (Unit III: Black Box Testing, System Testing).
- **Design techniques:** Equivalence Class Partitioning and Boundary Value Analysis (copies, password length, email), Error Guessing, Exploratory Testing.
- **Non-functional (limited):** Session testing and Cookies testing (logout/session), as listed in Unit III.
- **Automation:** Selenium WebDriver (Python) suite = 18 test cases / 28 executed test instances; Selenium IDE project = 4 record-and-replay tests (Unit V).
- **Cycle model:** Cycle 1 full run on v1.0 -> log defects -> developer fixes -> Cycle 2 retest of failed cases on v1.1 -> Cycle 3 full regression on v1.1.

## 5. Test cases and test data
Automated cases are in `tests/test_bookshelf.py` (TC01-TC18). Key test data:

| Field | Equivalence classes | Boundary / representative values |
|---|---|---|
| Password length | invalid (<6), valid (>=6) | 5 (reject), 6 (accept) |
| Copies | invalid (<1), valid (1-100), invalid (>100), non-numeric, empty | 0, 1, 2, 99, 100, 101, -5, "abc", "" |
| Email | valid, missing "@", missing domain dot, missing user part | `plainaddress`, `no@dot`, `@nouser.com` |

## 6. Entry and exit criteria
**Entry:** build deployed and starts; Chrome + ChromeDriver available; dependencies installed (`pip install -r requirements.txt`); smoke tests (TC01, TC06) pass.
**Exit:** 100% of planned test cases executed; no open Critical/High defects; all fixed defects retested and verified; full regression suite passes on the final build; test report and defect log completed.
**Suspension:** application will not start or login is completely broken.

## 7. Roles and schedule
| Role | Responsibility |
|---|---|
| Test manager / tester (student) | planning, scripts, execution, reports |
| Developer (student, same person) | fixes defects, switches build v1.0 -> v1.1 |

Execution schedule: Day 1 plan + scripts; Day 2 Cycle 1 + exploratory sessions; Day 3 fixes, Cycle 2, Cycle 3, final report.

## 8. Test metrics to report (Unit II)
Fill from `reports/bug_log_*.csv` after you run the suite. **Do not estimate values.**
- Test case coverage = executed test cases / planned test cases x 100
- Test case productivity = test cases executed / effort in hours
- Test efficiency = defects found in testing / total defects (found + escaped) x 100
- Defect acceptance ratio = defects accepted as valid / defects reported x 100 (rejected = invalid/duplicate)
- Effort and schedule variance = (actual - planned) / planned x 100

## 9. Risks
| Risk | Mitigation |
|---|---|
| Locators break if the UI changes | all elements have stable `id`/class attributes |
| Chrome/driver version mismatch | Selenium Manager (Selenium >= 4.6) auto-resolves the driver |
| Tests depend on each other | each test registers a fresh unique user and starts logged out |

## 10. Deliverables
Test plan, test cases/scripts, Selenium IDE project, defect log + bug taxonomy, regression run reports (HTML + CSV), exploratory session reports, final test summary.
