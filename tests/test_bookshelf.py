"""Automated Selenium WebDriver test suite for BookShelf (Test Plan section 5).

Each test is a black-box scenario. Tests marked @pytest.mark.defect("BUG-xx") are designed
to expose one specific seeded defect; they FAIL on the buggy build and PASS on the fixed build.
"""
import pytest
from selenium.webdriver.common.by import By

from helpers import PASSWORD, unique_email

pytestmark = pytest.mark.regression


# ============================ F1 - Registration ==========================
@pytest.mark.smoke
def test_tc01_register_valid_user(site):
    """TC01 Register with a valid email and password (ECP valid class)"""
    site.register(unique_email(), PASSWORD)
    assert "/login" in site.d.current_url
    assert "Registration successful" in site.msg()


@pytest.mark.defect("BUG-01")
@pytest.mark.parametrize("bad_email", ["plainaddress", "no@dot", "@nouser.com"])
def test_tc02_register_invalid_email_rejected(site, bad_email):
    """TC02 Registration must reject malformed email addresses (ECP invalid classes)"""
    site.register(bad_email, PASSWORD)
    assert "/register" in site.d.current_url
    assert "valid email" in site.msg()


def test_tc03_register_password_5_chars_rejected(site):
    """TC03 BVA: password of 5 characters (just below minimum) is rejected"""
    site.register(unique_email(), "abcde")
    assert "at least 6" in site.msg()


@pytest.mark.defect("BUG-02")
def test_tc04_register_password_6_chars_accepted(site):
    """TC04 BVA: password of exactly 6 characters (minimum) is accepted"""
    site.register(unique_email(), "abcdef")
    assert "Registration successful" in site.msg()


def test_tc05_register_duplicate_email_rejected(site):
    """TC05 Registering the same email twice is rejected"""
    email = unique_email()
    site.register(email, PASSWORD)
    site.register(email, PASSWORD)
    assert "already registered" in site.msg()


# ============================ F2 - Login / Logout ========================
@pytest.mark.smoke
def test_tc06_login_valid_credentials(site):
    """TC06 Login with correct credentials opens the book list"""
    site.new_logged_in_user()
    assert "/books" in site.d.current_url


def test_tc07_login_wrong_password_rejected(site):
    """TC07 Login with a wrong password is rejected"""
    email = unique_email()
    site.register(email, PASSWORD)
    site.login(email, "WrongPass9")
    assert "/login" in site.d.current_url
    assert "Invalid email or password" in site.msg()


@pytest.mark.defect("BUG-03")
def test_tc08_password_is_case_sensitive(site):
    """TC08 Password with different letter case must be rejected"""
    email = unique_email()
    site.register(email, "Secret1")
    site.login(email, "secret1")
    assert "/login" in site.d.current_url
    assert "Invalid email or password" in site.msg()


@pytest.mark.defect("BUG-07")
def test_tc09_logout_ends_session(site):
    """TC09 After logout, protected pages must not be reachable (session testing)"""
    site.new_logged_in_user()
    site.click("logout-link")
    site.open("/books")
    assert "/login" in site.d.current_url


def test_tc10_protected_page_requires_login(site):
    """TC10 Opening /books without logging in redirects to login"""
    site.open("/books")
    assert "/login" in site.d.current_url


# ============================ F3 - Add book (BVA / ECP on copies) ========
COPIES_CASES = [
    pytest.param("0", False, id="copies_0_below_min"),
    pytest.param("1", True, id="copies_1_min"),
    pytest.param("2", True, id="copies_2_above_min"),
    pytest.param("99", True, id="copies_99_below_max"),
    pytest.param("100", True, id="copies_100_max"),
    pytest.param("101", False, marks=pytest.mark.defect("BUG-04"), id="copies_101_above_max"),
    pytest.param("-5", False, id="copies_negative"),
    pytest.param("abc", False, id="copies_non_numeric"),
    pytest.param("", False, id="copies_empty"),
]


@pytest.mark.parametrize("copies,should_accept", COPIES_CASES)
def test_tc11_add_book_copies_boundaries(site, copies, should_accept):
    """TC11 Boundary value analysis + equivalence classes for the 'copies' field (valid 1-100)"""
    site.new_logged_in_user()
    title = f"Book {copies or 'blank'}"
    site.add_book(title, "Some Author", copies)
    if should_accept:
        assert title in site.titles()
    else:
        assert "Copies must" in site.msg()
        site.open("/books")
        assert title not in site.titles()


def test_tc12_add_book_title_required(site):
    """TC12 A book cannot be saved without a title"""
    site.new_logged_in_user()
    site.add_book("", "Author", 3)
    assert "Title is required" in site.msg()


@pytest.mark.defect("BUG-08")
def test_tc13_duplicate_title_rejected(site):
    """TC13 The same title cannot be added twice by one user (data integrity)"""
    site.new_logged_in_user()
    site.add_book("Clean Code", "Robert Martin", 2)
    site.add_book("clean code", "Robert Martin", 2)
    assert "already exists" in site.msg()
    site.open("/books")
    assert len(site.rows()) == 1


# ============================ F4 - Search ================================
@pytest.mark.defect("BUG-05")
def test_tc14_search_is_case_insensitive(site):
    """TC14 Searching 'python' finds 'Python Basics' (functional)"""
    site.new_logged_in_user()
    site.add_book("Python Basics", "A. Author", 1)
    site.add_book("Java Basics", "B. Author", 1)
    site.search("python")
    assert site.titles() == ["Python Basics"]


def test_tc15_search_no_match_message(site):
    """TC15 A search with no match shows the 'No books found' message"""
    site.new_logged_in_user()
    site.add_book("Python Basics", "A. Author", 1)
    site.search("zzzz")
    assert "No books found" in site.d.find_element(By.ID, "empty").text


# ============================ F5/F6 - Edit & Delete ======================
@pytest.mark.defect("BUG-06")
def test_tc16_edit_book_updates_author(site):
    """TC16 Editing a book saves the changed author and copies"""
    site.new_logged_in_user()
    site.add_book("Clean Code", "Robert Martin", 3)
    site.d.find_element(By.CSS_SELECTOR, "a.edit-link").click()
    site.fill("author", "R. C. Martin")
    site.fill("copies", "4")
    site.click("save-btn")
    row = site.rows()[0].text
    assert "R. C. Martin" in row and " 4 " in f" {row} "


def test_tc17_delete_book(site):
    """TC17 Deleting a book removes only that book"""
    site.new_logged_in_user()
    site.add_book("Book One", "A", 1)
    site.add_book("Book Two", "B", 2)
    site.rows()[0].find_element(By.CSS_SELECTOR, "button.delete-btn").click()
    assert site.titles() == ["Book Two"]


def test_tc18_user_cannot_see_other_users_books(site):
    """TC18 Books are private: a second user sees an empty list"""
    site.new_logged_in_user()
    site.add_book("Private Book", "Me", 1)
    site.click("logout-link")
    site.d.delete_all_cookies()
    site.new_logged_in_user()
    assert "Private Book" not in site.titles()
