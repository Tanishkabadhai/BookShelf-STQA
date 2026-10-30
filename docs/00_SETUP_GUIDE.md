# Setup Guide - How to get the project running (Windows first, Mac/Linux notes included)

You do not need to understand every file. For running the project you only touch **3 commands**. Follow the steps in order.

---
## Step 1 - Install the 3 things you need (one time)
1. **Python 3.10 or newer** - https://www.python.org/downloads/ . During install, **tick "Add Python to PATH"**.
   Check: open Command Prompt and type `python --version` (on Mac/Linux `python3 --version`).
2. **Google Chrome** (latest). Selenium downloads the matching driver by itself, so you need internet on the first run.
3. **VS Code** (optional but recommended, to open and read files) - https://code.visualstudio.com

## Step 2 - Put the files in ONE folder with this exact structure
The files were given to you one by one, so the folders were lost. Create a folder `stqa_project` (e.g. `C:\stqa_project`), make the sub-folders below, and place each downloaded file in the right place. File names must match exactly.

```
stqa_project/
  app.py
  requirements.txt
  pytest.ini
  run_cycles.py
  verify_modes.py
  README.md
  templates/        <- base.html, login.html, register.html, books.html, book_form.html
  static/           <- style.css
  static/img/       <- library.jpg, desk.jpg, empty-shelf.jpg, banner.jpg
  tests/            <- conftest.py, helpers.py, test_bookshelf.py
  ide/              <- BookShelf.side
  docs/             <- 00 to 05 .md files
  reports/          <- empty folder (results appear here)
```
Missing the `templates` folder or its 5 html files is the #1 reason the app shows an error. Missing `static/` does not break anything, the pages just look plain.

## Step 3 - Open a terminal inside the folder
- Windows: open `stqa_project` in File Explorer, click the address bar, type `cmd`, press Enter.
- VS Code: File > Open Folder > `stqa_project`, then Terminal > New Terminal.

## Step 4 - Install the libraries (one time)
```
python -m venv venv
venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```
(If PowerShell blocks `activate`, use Command Prompt instead, or skip the venv lines and just run the `pip install` line.)
You should see `(venv)` at the start of the line after activating. Every new terminal needs the `activate` line again.

## Step 5 - Run the 3 commands
**Command 1 - quick check, no browser needed**
```
python verify_modes.py
```
Expected: a table where all 8 BUG rows say `PRESENT` for the buggy build and `absent` for the fixed build, then `RESULT: all 8 defects present...`. If you see this, the project is installed correctly.

**Command 2 - look at the application yourself**
```
python app.py --mode buggy
```
Open http://127.0.0.1:5000 in Chrome. Register, log in, add books. The footer shows which build you are on. Stop the server with `Ctrl+C`. Use `--mode fixed` for the corrected build.

**Command 3 - run the automatic Selenium tests (the main part)**
```
python run_cycles.py
```
Chrome runs hidden (headless) and the three cycles execute one after another. Cycle 1 is *supposed* to show failures - those are the bugs being found. To use Firefox instead of Chrome, set `BROWSER=firefox` first. To watch the browser, set `HEADLESS=0` first (Windows: `set HEADLESS=0`, PowerShell: `$env:HEADLESS="0"`).

## Step 6 - Find your results (these go in your report)
| File in `reports/` | What it is |
|---|---|
| `cycle1_buggy_full.html` | test report of Cycle 1 (open in browser) |
| `bug_log_cycle1_buggy_full.csv` | defect log: which test failed, linked BUG id, message, screenshot (open in Excel) |
| `cycle2_fixed_retest.html`, `cycle3_fixed_regression.html` | retest and regression reports |
| `screenshots/` | picture of the browser at each failure |

## Step 7 - Selenium IDE part (manual, 10 minutes)
1. Install the **Selenium IDE** extension from the Chrome Web Store.
2. In a terminal run `python app.py --mode buggy` and leave it running.
3. Open the extension > *Open an existing project* > choose `ide/BookShelf.side`.
4. Run the suite **Regression**, take a screenshot of the result panel. Then stop the app, start it with `--mode fixed`, run again, take another screenshot.

## Step 8 - Exploratory testing (manual)
Open `docs/04_EXPLORATORY_TESTING.md`, run each charter for 20-30 min on `--mode buggy`, and fill the session sheet with only what you really saw.

---
## Which file is for what (cheat sheet)
| You want to... | Use |
|---|---|
| Read the plan / taxonomy / syllabus mapping | `docs/01` to `docs/05` |
| Start the application | `app.py` |
| See the test code | `tests/test_bookshelf.py` (each `test_tcNN` is one test case) |
| Run everything | `run_cycles.py` |
| Run only the quick smoke tests | `python -m pytest -m smoke` |
| Run one test | `python -m pytest -k tc09` |

Files you can ignore for now: `conftest.py`, `helpers.py`, `pytest.ini`, `requirements.txt`, `templates/` (support files that make the above work).

## Common problems
| Problem | Fix |
|---|---|
| `python` is not recognized | Reinstall Python with "Add to PATH" ticked, reopen the terminal |
| `No module named flask/selenium/pytest` | Activate the venv, then `pip install -r requirements.txt` |
| `TemplateNotFound` | `templates/` folder or an html file is missing/misnamed |
| `SessionNotCreated` / driver errors | Update Chrome; make sure you are online (driver downloads on first run) |
| `Address already in use` | An old `app.py` is still running; close it (Ctrl+C) or use `--port 5001` |
| Tests say `ModuleNotFoundError: app` | Run the commands from inside the `stqa_project` folder |
| Setting env vars in a single line | cmd: `set APP_MODE=buggy&& python -m pytest` ; PowerShell: `$env:APP_MODE="buggy"; python -m pytest` |

If anything fails, copy the full error text and send it to me.

**Next:** after Step 6-8, send me the CSV files, the error text if any, and your screenshots/notes, and I will write the final test report, project report and viva questions from your real results.
