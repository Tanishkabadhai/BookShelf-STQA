# Exploratory Testing Report
*Syllabus: Unit III (Experience-Based Techniques: Error Guessing, Exploratory Testing)*

Exploratory testing = simultaneous learning, test design and execution, guided by a **charter**, time-boxed. It complements the scripted suite: it is where *new* defects (usability, odd inputs) are found. Run each session manually on the **buggy build**, 20-30 minutes, and write what you actually observe.

## Charters
| Session | Charter | Ideas to explore (error guessing) |
|---|---|---|
| EX-1 | Explore registration and login with unusual input | spaces in email, very long email/password, SQL-like text `' OR 1=1 --`, uppercase email, unicode, pressing Enter vs clicking |
| EX-2 | Explore book management with unusual data | 100+ char title, `<b>bold</b>` in title (HTML injection), leading/trailing spaces, copies `007`, `1.5`, `1e2`, very long author |
| EX-3 | Explore navigation and session behaviour | browser Back after logout, editing `/books/<id>/edit` for an id you do not own, opening `/books/add` while logged out, two tabs |

## Session sheet (copy one per session and fill in)
| Field | Entry |
|---|---|
| Session ID / Tester / Date / Build / Browser | |
| Charter | |
| Duration (minutes) | |
| Areas covered | |
| Test notes (what you tried) | |
| Bugs found (title, steps, expected, actual, severity, screenshot) | |
| Issues / questions | |
| Coverage estimate: on charter / opportunity | |

## Rule for the final report
Only list a defect found in exploratory testing if you actually observed it, with steps and a screenshot. If you add it to the defect register use IDs `EXP-01`, `EXP-02`... and the taxonomy categories in document 02.
