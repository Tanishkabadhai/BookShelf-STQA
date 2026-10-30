"""BookShelf - small Flask web app used as the Application Under Test (AUT).

Two builds of the SAME application are provided so that testing can be demonstrated:
  --mode buggy : build v1.0, contains 8 deliberately seeded defects (BUG-01 .. BUG-08)
  --mode fixed : build v1.1, the defects are corrected (used for retest / regression)
The seeded defects are intentional and are documented in docs/02_BUG_TAXONOMY_AND_REGISTER.md.
"""
import argparse
import os
import re
import sqlite3
from contextlib import closing
from functools import wraps

from flask import (Flask, abort, flash, g, get_flashed_messages, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL DEFAULT '',
    copies INTEGER NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id));
"""


def create_app(mode=None, db_path="bookshelf.db"):
    mode = (mode or os.environ.get("APP_MODE", "fixed")).lower()
    if mode not in ("buggy", "fixed"):
        raise ValueError("mode must be 'buggy' or 'fixed'")
    buggy = mode == "buggy"

    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev-only-change-me", DATABASE=db_path, APP_MODE=mode)
    with closing(sqlite3.connect(db_path)) as con:
        con.executescript(SCHEMA)

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        con = g.pop("db", None)
        if con is not None:
            con.close()

    @app.context_processor
    def inject_build():
        return {"build": "v1.0 (buggy build)" if buggy else "v1.1 (fixed build)"}

    def login_required(view):
        @wraps(view)
        def wrapper(*a, **kw):
            if not session.get("user_id"):
                return redirect(url_for("login"))
            return view(*a, **kw)
        return wrapper

    def stored_password(raw):
        # BUG-03 (buggy): password is normalised to lower case before hashing/checking
        return raw.lower() if buggy else raw

    # ---------------------------------------------------------------- auth
    @app.route("/")
    def index():
        return redirect(url_for("books" if session.get("user_id") else "login"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            # BUG-01 (buggy): only checks that the email is non-empty
            email_ok = bool(email) if buggy else bool(EMAIL_RE.match(email))
            # BUG-02 (buggy): off-by-one, rejects a password of exactly 6 characters
            length_ok = len(password) > 6 if buggy else len(password) >= 6
            if not email_ok:
                flash("Enter a valid email address.", "error")
            elif not length_ok:
                flash("Password must be at least 6 characters.", "error")
            else:
                try:
                    with db() as con:
                        con.execute("INSERT INTO users(email, password_hash) VALUES (?, ?)",
                                    (email, generate_password_hash(stored_password(password))))
                except sqlite3.IntegrityError:
                    flash("Email already registered.", "error")
                else:
                    flash("Registration successful. Please log in.", "success")
                    return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            row = db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            if row and check_password_hash(row["password_hash"], stored_password(password)):
                session["user_id"] = row["id"]
                return redirect(url_for("books"))
            flash("Invalid email or password.", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        if not buggy:          # BUG-07 (buggy): session is never cleared on logout
            session.clear()
        flash("Logged out.", "success")
        return redirect(url_for("login"))

    # --------------------------------------------------------------- books
    def validate_book(uid, book_id=None):
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        raw = request.form.get("copies", "").strip()
        if not title:
            return "Title is required.", None
        if len(title) > 100:
            return "Title must be at most 100 characters.", None
        try:
            copies = int(raw)
        except ValueError:
            return "Copies must be a whole number.", None
        upper = 101 if buggy else 100    # BUG-04 (buggy): upper boundary off by one
        if copies < 1 or copies > upper:
            return "Copies must be between 1 and 100.", None
        if not buggy:                    # BUG-08 (buggy): duplicate titles are allowed
            dup = db().execute(
                "SELECT id FROM books WHERE user_id=? AND LOWER(title)=LOWER(?) AND id IS NOT ?",
                (uid, title, book_id)).fetchone()
            if dup:
                return "A book with this title already exists.", None
        return None, (title, author, copies)

    @app.route("/books")
    @login_required
    def books():
        q = request.args.get("q", "").strip()
        rows = db().execute("SELECT * FROM books WHERE user_id=? ORDER BY id",
                            (session["user_id"],)).fetchall()
        if q:
            if buggy:   # BUG-05 (buggy): search is case-sensitive
                rows = [r for r in rows if q in r["title"] or q in r["author"]]
            else:
                ql = q.lower()
                rows = [r for r in rows if ql in r["title"].lower() or ql in r["author"].lower()]
        return render_template("books.html", rows=rows, q=q)

    @app.route("/books/add", methods=["GET", "POST"])
    @login_required
    def add_book():
        if request.method == "POST":
            err, data = validate_book(session["user_id"])
            if err:
                flash(err, "error")
            else:
                with db() as con:
                    con.execute("INSERT INTO books(user_id,title,author,copies) VALUES (?,?,?,?)",
                                (session["user_id"], *data))
                flash("Book added.", "success")
                return redirect(url_for("books"))
        return render_template("book_form.html", heading="Add Book", book=None)

    @app.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_book(book_id):
        book = db().execute("SELECT * FROM books WHERE id=? AND user_id=?",
                            (book_id, session["user_id"])).fetchone()
        if book is None:
            abort(404)
        if request.method == "POST":
            err, data = validate_book(session["user_id"], book_id)
            if err:
                flash(err, "error")
            else:
                title, author, copies = data
                with db() as con:
                    if buggy:   # BUG-06 (buggy): author change is silently ignored
                        con.execute("UPDATE books SET title=?, copies=? WHERE id=?",
                                    (title, copies, book_id))
                    else:
                        con.execute("UPDATE books SET title=?, author=?, copies=? WHERE id=?",
                                    (title, author, copies, book_id))
                flash("Book updated.", "success")
                return redirect(url_for("books"))
        return render_template("book_form.html", heading="Edit Book", book=book)

    @app.route("/books/<int:book_id>/delete", methods=["POST"])
    @login_required
    def delete_book(book_id):
        with db() as con:
            con.execute("DELETE FROM books WHERE id=? AND user_id=?", (book_id, session["user_id"]))
        flash("Book deleted.", "success")
        return redirect(url_for("books"))

    return app


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Run the BookShelf application under test")
    ap.add_argument("--mode", choices=["buggy", "fixed"], default="buggy")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()
    create_app(args.mode).run(port=args.port, debug=False)
