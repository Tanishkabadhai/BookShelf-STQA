# Narration of the Test Scripts
*Syllabus: Unit III (regression, retest, smoke, BVA/ECP, session testing), Unit V (automation process, Selenium WebDriver and IDE)*

This document explains, in plain language, what every script does, why it exists and what result to expect on each build. "Buggy" = build v1.0, "Fixed" = build v1.1. Expected results are the **design intent**; your real results come from your own run (`reports/`).

---
## 1. How a test run works (the big picture)
1. `pytest` reads `pytest.ini`, finds `tests/` and loads `conftest.py` (setup code) and `test_bookshelf.py` (the tests).
2. `conftest.py` starts the BookShelf server in the background on a free port with a temporary database, using the build chosen by `APP_MODE` (`buggy` or `fixed`).
3. It opens one headless Chrome window controlled by Selenium WebDriver.
4. Before every test it opens the login page and deletes cookies, so each test starts logged out and independent of the others.
5. The test performs user actions through helper functions (type, click), then **asserts** what the page should show. If the assertion is false, the test fails, which means a defect (or a wrong test) was found.
6. After each test, a hook records the result, takes a screenshot on failure and later writes `bug_log_<tag>.csv`.
7. `run_cycles.py` repeats this for the three cycles.

## 2. The support scripts
### `tests/helpers.py` (the helper layer)
| Item | What it does |
|---|---|
| `unique_email()` | makes a new email like `user3fa9c1d2@test.com` every call, so tests never clash on "email already registered" |
| `Site.open(path)` | goes to a page of the app |
| `Site.fill(id, text)` | finds an input by id, clears it, types text (an empty text just clears the field) |
| `Site.click(id)` / `click_element(el)` | clicks, then **waits until the next page has fully loaded**, so a test never reads the old page (this removes a race condition that makes tests flaky) |
| `Site.msg()` | returns the text of the message banner (`#msg`), or empty text if none |
| `Site.register / login` | fill and submit the two forms |
| `Site.new_logged_in_user()` | registers a fresh user, then logs in; used by every test that needs a logged-in state |
| `Site.add_book / search` | fill and submit the add-book form / the search box |
| `Site.rows() / titles()` | return the book rows / the list of visible book titles for assertions |

### `tests/conftest.py` (fixtures and reporting)
| Item | What it does |
|---|---|
| `base_url` fixture | starts the server once per run and gives the tests its address |
| `driver` fixture | starts headless Chrome once per run; implicit wait 3 seconds (WebDriver keeps looking for an element for up to 3 s before giving up) |
| `site` fixture | gives each test a clean, logged-out browser and a `Site` helper |
| report hook | records outcome, linked defect, one-line failure reason, screenshot path |
| session-finish hook | writes `reports/bug_log_<tag>.csv` and prints a one-line summary |

### Markers
`@pytest.mark.smoke` quick build check (`pytest -m smoke`: TC01, TC06). `@pytest.mark.regression` applied to all tests. `@pytest.mark.defect("BUG-xx")` links a test to the defect it is designed to expose, so the CSV shows which defect each failure maps to.

---
## 3. Narration of each automated test case
Format: **goal - steps - expected - buggy build - why it matters.**

### F1 Registration
**TC01 register_valid_user** (smoke, ECP valid class)
Steps: register with a new valid email and a valid password. Expected: page moves to login and shows "Registration successful". Buggy: pass. Why: proves the basic path works before anything else is tested.

**TC02 register_invalid_email_rejected** (ECP invalid classes, BUG-01) runs 3 times
Steps: try to register with `plainaddress` (no "@"), `no@dot` (no dot in the domain), `@nouser.com` (nothing before "@"). Expected: stays on the register page with "Enter a valid email address". Buggy: **fails** all 3, because the buggy build accepts any non-empty email and redirects to login. Why: each value represents a different class of invalid email.

**TC03 register_password_5_chars_rejected** (BVA, just below the minimum)
Steps: register with the 5-character password `abcde`. Expected: message says at least 6 characters. Buggy: pass. Why: shows the lower side of the boundary works.

**TC04 register_password_6_chars_accepted** (BVA, exactly the minimum, BUG-02)
Steps: register with the 6-character password `abcdef`. Expected: "Registration successful". Buggy: **fails**, because the buggy code checks `length > 6` instead of `>= 6`, so a valid 6-character password is rejected. Why: classic off-by-one at a boundary.

**TC05 register_duplicate_email_rejected**
Steps: register an email, then register the same email again. Expected: "already registered". Buggy: pass. Why: the email must be unique.

### F2 Login and logout
**TC06 login_valid_credentials** (smoke)
Steps: create a user and log in with the correct password. Expected: the URL contains `/books`. Buggy: pass.

**TC07 login_wrong_password_rejected**
Steps: register, then log in with a wrong password. Expected: stays on `/login`, message "Invalid email or password". Buggy: pass.

**TC08 password_is_case_sensitive** (BUG-03)
Steps: register with `Secret1`, then log in with `secret1`. Expected: login rejected. Buggy: **fails**, because the buggy build converts passwords to lower case, so `secret1` logs in. Why: a security defect that reduces password strength.

**TC09 logout_ends_session** (session testing, BUG-07)
Steps: log in, click Log out, then open `/books` directly. Expected: redirected to `/login`. Buggy: **fails**, because the buggy logout does not clear the session, so `/books` still opens. Why: after logout nobody should reach private pages (Unit III session/cookies testing).

**TC10 protected_page_requires_login**
Steps: with no login, open `/books`. Expected: redirected to `/login`. Buggy: pass. Why: guards against unauthenticated access; it is also a regression guard.

### F3 Adding books
**TC11 add_book_copies_boundaries** (BVA + ECP, BUG-04) runs 9 times
Valid range for copies is 1 to 100.
| Value | Class | Expected |
|---|---|---|
| 0 | just below minimum | rejected |
| 1 | minimum | accepted |
| 2 | just above minimum | accepted |
| 99 | just below maximum | accepted |
| 100 | maximum | accepted |
| 101 | just above maximum | rejected (**buggy accepts, fails**) |
| -5 | negative class | rejected |
| abc | non-numeric class | rejected |
| (empty) | empty class | rejected |
Steps for each: log in, add a book titled "Book <value>" with that copies value. Accepted values must show the title in the list; rejected values must show "Copies must..." and the title must not appear in the list.

**TC12 add_book_title_required**
Steps: add a book with an empty title. Expected: "Title is required". Buggy: pass.

**TC13 duplicate_title_rejected** (data integrity, BUG-08)
Steps: add "Clean Code", then add "clean code" (different case). Expected: "already exists", and only 1 row in the list. Buggy: **fails**, because the buggy build stores duplicates.

### F4 Search
**TC14 search_is_case_insensitive** (BUG-05)
Steps: add "Python Basics" and "Java Basics", search for `python`. Expected: only "Python Basics". Buggy: **fails**, because the buggy search is case-sensitive and finds nothing.

**TC15 search_no_match_message**
Steps: add one book, search `zzzz`. Expected: the page shows "No books found". Buggy: pass.

### F5, F6, F7 Edit, delete, privacy
**TC16 edit_book_updates_author** (BUG-06)
Steps: add "Clean Code" by "Robert Martin", 3 copies; click Edit; change author to "R. C. Martin" and copies to 4; Save. Expected: the row shows the new author and 4. Buggy: **fails**, because the buggy update ignores the author field.

**TC17 delete_book**
Steps: add two books, delete the first. Expected: only "Book Two" remains. Buggy: pass.

**TC18 user_cannot_see_other_users_books**
Steps: user A adds "Private Book", logs out, cookies are cleared, user B registers and logs in. Expected: B's list does not contain "Private Book". Buggy: pass.

**Totals.** 18 test cases, run as 28 instances (TC02 x3, TC11 x9). Designed failures on the buggy build: BUG-01 x3, BUG-02, BUG-03, BUG-04, BUG-05, BUG-06, BUG-07, BUG-08 = **10 instances** failing, 18 passing. Expected on the fixed build: **28 pass**.

---
## 4. Narration of the Selenium IDE tests (`ide/BookShelf.side`)
Selenium IDE records and replays actions without code. The 4 tests share a unique email built from the current time (`u${ts}@test.com`) so reruns never clash.

| Test | What the commands do | Buggy build | Fixed build |
|---|---|---|---|
| IDE-01 Register and Login | open register page, type a new email and password, click register, check the success message, log in, check that "Add book" is present | pass | pass |
| IDE-02 Add book and case-insensitive search (BUG-05) | same sign-up, add "Clean Code", check it is listed, search `clean code` in lower case, check the book is still found | fails at the last check | pass |
| IDE-03 Invalid email rejected (BUG-01) | register with email `abc`, check the message "Enter a valid email address." | fails (registration succeeds instead) | pass |
| IDE-04 Logout ends session (BUG-07) | sign up, log in, click Log out, open `/books`, check the login button is shown | fails (books page opens) | pass |

**WebDriver vs IDE in this project:** IDE gives four quick recorded checks with no code, good for demonstrating record-and-replay. WebDriver gives parametrised, reusable, reportable tests; this is why the main regression suite is in WebDriver.

---
## 5. Narration of the three cycles (regression process)
| Cycle | Command (inside `run_cycles.py`) | Build | What happens | Purpose |
|---|---|---|---|---|
| 1 | full suite | buggy v1.0 | all 28 run, designed failures appear, CSV + screenshots saved | defect detection |
| 2 | `pytest --lf` | fixed v1.1 | only the tests that failed in cycle 1 run again | **retest** |
| 3 | full suite | fixed v1.1 | all 28 run again | **regression test** (did the fixes break anything else?) |

Between cycle 1 and 2 the "developer" step happens: the defects are logged (CSV), fixed in code, and the build is switched from v1.0 to v1.1.

## 6. What to say if asked "how do the scripts find bugs?"
Each test has an oracle: a rule from the requirements (for example "copies 101 must be rejected"). The script performs the user action, then compares the real page with the rule. A mismatch is a failure, the failure is mapped to a defect id in the CSV, and a screenshot is saved as evidence.
