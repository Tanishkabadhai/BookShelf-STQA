# Selection of Platform, Languages and Tools
*Syllabus: Unit V ("how to choose automation testing tools", Selenium tool suite, automation frameworks). The topic asks to select a relevant system environment/platform and programming languages.*

## 1. Selection criteria
Taken from the Unit V idea of choosing tools: cost, language and browser support, learning curve, community and documentation, reporting, maintainability, and fit with the assignment.

## 2. Decisions
| Area | Choice | Alternatives considered | Reason (and trade-off) |
|---|---|---|---|
| Application type | Web application | desktop, mobile app | the topic says web-based; testable in any browser |
| Platform / OS | Platform independent: Windows, Linux or macOS | single OS | Python, Flask and Chrome run on all three, so it works on any student laptop |
| Browser | Google Chrome | Firefox, Edge | most widely used, Selenium Manager fetches its driver automatically. Trade-off: no cross-browser testing (listed as future scope with Selenium Grid) |
| AUT language and framework | Python with Flask | Java (Spring), PHP, Node.js | smallest amount of code for a few pages, free, easy to explain in a viva. Trade-off: not an enterprise stack |
| Database | SQLite | MySQL, PostgreSQL | no installation or server, one file. Trade-off: not for multi-user production use |
| Front end | Server-rendered HTML + CSS, no JavaScript framework | React/Angular single-page app | stable pages and ids make tests reliable; the project is about testing, not UI engineering |
| Test automation tool | Selenium WebDriver + Selenium IDE | Appium, SoapUI, Tosca (syllabus), Cypress/Playwright (outside syllabus) | Selenium is the tool the topic requires, free and browser-based. Appium targets mobile apps and SoapUI targets APIs, neither fits a browser UI test; Tosca is commercial |
| Test script language | Python | Java, C#, JavaScript | Selenium supports all of them. Python is short and readable, and works with pytest. Trade-off: Java is more common in industry; the Selenium concepts are the same |
| Test runner (outside syllabus) | pytest + pytest-html | unittest, TestNG | parametrised tests (BVA tables), markers (smoke/defect), and an HTML report with little code. It is a tool, not an exam concept |
| Record-and-replay | Selenium IDE (Chrome extension) | none | required by the topic; used for 4 quick tests |
| Reports | pytest-html report, CSV defect log, failure screenshots | manual Excel | generated automatically, same every run |

## 3. Why two builds (v1.0 and v1.1) of the same app
Testing, defect logging, retesting and regression need a build that has defects and a later build with fixes. The defects are deliberately seeded and documented so the whole process can be shown honestly.

## 4. Environment summary (for the report)
Windows/Linux/macOS, Python 3.10+, Flask, SQLite, Google Chrome, Selenium 4 (WebDriver, IDE extension), pytest, VS Code. All free and open source.
