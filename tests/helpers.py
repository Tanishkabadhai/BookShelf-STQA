"""Small helper layer over Selenium WebDriver so that test scripts read like test steps."""
import time
import uuid

from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By

PASSWORD = "Secret1"


def unique_email():
    return f"user{uuid.uuid4().hex[:8]}@test.com"


class Site:
    def __init__(self, driver, base_url):
        self.d = driver
        self.base = base_url

    # -- generic -------------------------------------------------------
    def open(self, path):
        self.d.get(self.base + path)

    def fill(self, element_id, text):
        el = self.d.find_element(By.ID, element_id)
        el.clear()
        if text != "":                 # some drivers reject send_keys("")
            el.send_keys(text)

    def click(self, element_id):
        self.click_element(self.d.find_element(By.ID, element_id))

    def click_element(self, element):
        """Click, then wait until the browser has finished loading the next page.

        Without this wait a test can read the OLD page (race condition = flaky test).
        """
        old_page = self.d.find_element(By.TAG_NAME, "html")
        element.click()
        deadline = time.time() + 5
        while time.time() < deadline:            # 1) wait for the old page to be replaced
            try:
                old_page.is_enabled()
            except StaleElementReferenceException:
                break
            except WebDriverException:           # page is mid-navigation
                time.sleep(0.05)
                continue
            time.sleep(0.05)
        deadline = time.time() + 10
        while time.time() < deadline:            # 2) wait until the new page is complete
            try:
                if self.d.execute_script("return document.readyState") == "complete":
                    return
            except WebDriverException:
                pass
            time.sleep(0.05)

    def msg(self):
        found = self.d.find_elements(By.ID, "msg")
        return found[0].text if found else ""

    # -- user actions --------------------------------------------------
    def register(self, email, password):
        self.open("/register")
        self.fill("email", email)
        self.fill("password", password)
        self.click("register-btn")

    def login(self, email, password):
        self.open("/login")
        self.fill("email", email)
        self.fill("password", password)
        self.click("login-btn")

    def new_logged_in_user(self, password=PASSWORD):
        email = unique_email()
        self.register(email, password)
        self.login(email, password)
        return email

    def add_book(self, title, author, copies):
        self.open("/books/add")
        self.fill("title", title)
        self.fill("author", author)
        self.fill("copies", str(copies))
        self.click("save-btn")

    def search(self, text):
        self.open("/books")
        self.fill("q", text)
        self.click("search-btn")

    # -- observations --------------------------------------------------
    def rows(self):
        return self.d.find_elements(By.CSS_SELECTOR, "tr.book-row")

    def titles(self):
        return [r.find_element(By.CSS_SELECTOR, ".col-title").text for r in self.rows()]
