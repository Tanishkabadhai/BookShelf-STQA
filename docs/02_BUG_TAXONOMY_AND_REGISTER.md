# Bug Taxonomy and Defect Register
*Syllabus: Unit I (defects, failures, causes/effects), Unit II (defect acceptance/rejection), Unit III (black box, non-functional)*

## 1. Bug taxonomy used in this project
| Category | Definition | Typical cause | Example here |
|---|---|---|---|
| **Input validation** | invalid input accepted or valid input rejected | missing/incorrect checks | BUG-01 |
| **Boundary (off-by-one)** | wrong behaviour at a range edge | `>` vs `>=`, wrong limit | BUG-02, BUG-04 |
| **Functional / logic** | feature does not do what the requirement says | wrong logic, omitted field | BUG-05, BUG-06 |
| **Security / session** | authentication or session handling flaw | credential or session mishandled | BUG-03, BUG-07 |
| **Data integrity** | inconsistent or duplicated data stored | missing uniqueness rule | BUG-08 |
| **Usability / UI** | confusing messages, layout, labels | design omission | (exploratory findings) |

**Severity:** Critical (system unusable / security breach) - High (major feature wrong) - Medium (feature partly wrong, workaround exists) - Low (cosmetic).
**Priority:** P1 fix now - P2 fix before release - P3 can wait.
**Defect life cycle:** New -> Assigned -> Open -> Fixed -> Retest -> Verified/Closed (or Reopened / Rejected-Duplicate / Deferred).

## 2. Defect register (seeded defects in build v1.0)
These defects were **deliberately seeded** into the AUT so that the testing process can be demonstrated. Expected-detection column is the *design intent*; actual detection is recorded in your bug log after running.

| ID | Feature | Category | Severity | Expected result | Defect in v1.0 | Detected by |
|---|---|---|---|---|---|---|
| BUG-01 | F1 | Input validation | Medium | malformed email rejected | any non-empty text accepted | TC02 (x3), IDE-03 |
| BUG-02 | F1 | Boundary | Medium | 6-char password accepted | rejected (needs 7+) | TC04 |
| BUG-03 | F2 | Security | High | password case-sensitive | `secret1` logs in as `Secret1` | TC08 |
| BUG-04 | F3 | Boundary | Medium | copies 101 rejected | 101 accepted | TC11 (copies_101) |
| BUG-05 | F4 | Functional | Medium | search case-insensitive | case-sensitive | TC14, IDE-02 |
| BUG-06 | F5 | Functional | High | edited author saved | author change ignored | TC16 |
| BUG-07 | F2 | Security / session | High | logout ends session | /books still opens | TC09, IDE-04 |
| BUG-08 | F3 | Data integrity | Low | duplicate title rejected | duplicates stored | TC13 |

## 3. Bug report template (one per defect, copy from the CSV log)
`ID | Title | Build | Feature | Steps to reproduce | Expected | Actual | Severity | Priority | Evidence (screenshot path) | Status`

## 4. Defect analysis (after Cycle 1)
Count defects per category from `bug_log_cycle1_buggy_full.csv`. *Optional (Unit VI, Pareto diagrams):* draw a Pareto chart of defects by category. Marked optional - not required by the topic.
