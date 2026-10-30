"""Browser-free sanity check of the two AUT builds (Flask test client, no Selenium).

Confirms each seeded defect is present in the buggy build and absent in the fixed build.
This checks the application only; it does NOT replace the Selenium test cycles.
"""
import tempfile, os, re
from app import create_app


def run(mode):
    path = os.path.join(tempfile.mkdtemp(), "t.db")
    app = create_app(mode, path)
    c = app.test_client()
    out = {}
    post = lambda url, **d: c.post(url, data=d, follow_redirects=True).get_data(as_text=True)
    out["BUG-01"] = "Registration successful" in post("/register", email="abc", password="Secret1")
    out["BUG-02"] = "Registration successful" not in post("/register", email="a@b.com", password="abcdef")
    post("/register", email="u@t.com", password="Secret1")
    page = post("/login", email="u@t.com", password="secret1")
    out["BUG-03"] = "add-link" in page
    post("/login", email="u@t.com", password="Secret1")   # ensure logged in for later checks
    out["BUG-04"] = "Book added" in post("/books/add", title="B101", author="x", copies="101")
    post("/books/add", title="Clean Code", author="Martin", copies="2")
    out["BUG-08"] = "Book added" in post("/books/add", title="clean code", author="Martin", copies="2")
    out["BUG-05"] = "Clean Code" not in c.get("/books?q=clean").get_data(as_text=True)
    bid = re.search(r"/books/(\d+)/edit", c.get("/books").get_data(as_text=True)).group(1)
    post(f"/books/{bid}/edit", title="Clean Code", author="R. C. Martin", copies="4")
    out["BUG-06"] = "R. C. Martin" not in c.get("/books").get_data(as_text=True)
    c.get("/logout")
    out["BUG-07"] = c.get("/books").status_code == 200   # still reachable after logout
    return out


if __name__ == "__main__":
    b, f = run("buggy"), run("fixed")
    print(f"{'Defect':8} {'buggy build':12} {'fixed build':12}")
    for k in sorted(b):
        print(f"{k:8} {'PRESENT' if b[k] else 'absent':12} {'PRESENT' if f[k] else 'absent':12}")
    ok = all(b.values()) and not any(f.values())
    print("\nRESULT:", "all 8 defects present in buggy build and absent in fixed build" if ok else "MISMATCH - investigate")
