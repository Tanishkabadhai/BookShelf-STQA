"""Fixtures (server + browser) and defect-log reporting for the Selenium test suite.

Environment variables
  APP_MODE    buggy | fixed   which build of the AUT is started (default: fixed)
  REPORT_TAG  label used in report file names (default: APP_MODE)
  HEADLESS    set to 0 to watch the browser (default: headless)
  BROWSER     chrome (default) | firefox | webkit   (webkit = WebKitGTK, Linux only)
"""
import csv
import os
import re
import threading
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from werkzeug.serving import make_server

from app import create_app
from helpers import Site

MODE = os.environ.get("APP_MODE", "fixed").lower()
TAG = os.environ.get("REPORT_TAG", MODE)
REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
RESULTS = []


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    db_file = tmp_path_factory.mktemp("db") / "test.db"
    server = make_server("127.0.0.1", 0, create_app(MODE, str(db_file)), threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


def make_driver():
    headless = os.environ.get("HEADLESS", "1") != "0"
    browser = os.environ.get("BROWSER", "chrome").lower()
    if browser == "firefox":
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        opts = FirefoxOptions()
        if headless:
            opts.add_argument("-headless")
        drv = webdriver.Firefox(options=opts)
    elif browser == "webkit":
        from selenium.webdriver.webkitgtk.options import Options as WebKitOptions
        opts = WebKitOptions()
        if os.environ.get("WEBKIT_BINARY"):
            opts.binary_location = os.environ["WEBKIT_BINARY"]
        drv = webdriver.WebKitGTK(options=opts)
    else:
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        for arg in ("--no-sandbox", "--disable-gpu", "--window-size=1280,900"):
            opts.add_argument(arg)
        drv = webdriver.Chrome(options=opts)      # Selenium Manager locates the driver
    drv.set_window_size(1280, 900)
    return drv


@pytest.fixture(scope="session")
def driver():
    drv = make_driver()
    drv.implicitly_wait(3)
    yield drv
    drv.quit()


@pytest.fixture
def site(driver, base_url):
    driver.get(base_url + "/login")
    driver.delete_all_cookies()               # every test starts logged out
    return Site(driver, base_url)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call" and not (rep.when == "setup" and rep.failed):
        return
    marker = item.get_closest_marker("defect")
    shot = ""
    if rep.failed:
        drv = item.funcargs.get("driver")
        if drv is not None:
            (REPORT_DIR / "screenshots").mkdir(parents=True, exist_ok=True)
            safe = re.sub(r"\W+", "_", item.name)
            shot = f"screenshots/{TAG}_{safe}.png"
            try:
                drv.save_screenshot(str(REPORT_DIR / shot))
            except Exception:
                shot = ""
    detail = ""
    if rep.failed and rep.longreprtext:
        detail = rep.longreprtext.strip().splitlines()[-1][:200]
    doc = (item.function.__doc__ or "").strip().splitlines()
    RESULTS.append({
        "test_id": item.name,
        "description": doc[0] if doc else "",
        "outcome": rep.outcome.upper(),
        "linked_defect": marker.args[0] if marker else "",
        "failure_detail": detail,
        "screenshot": shot,
    })


def pytest_sessionfinish(session, exitstatus):
    if not RESULTS:
        return
    REPORT_DIR.mkdir(exist_ok=True)
    path = REPORT_DIR / f"bug_log_{TAG}.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(RESULTS[0].keys()))
        w.writeheader()
        w.writerows(RESULTS)
    total = len(RESULTS)
    failed = [r for r in RESULTS if r["outcome"] == "FAILED"]
    defects = sorted({r["linked_defect"] for r in failed if r["linked_defect"]})
    print(f"\n[{TAG}] build={MODE} executed={total} passed={total - len(failed)} "
          f"failed={len(failed)} defects_exposed={len(defects)} {defects}")
    print(f"[{TAG}] defect log written to {path}")
