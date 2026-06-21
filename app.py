from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf.csrf import CSRFProtect
from cryptography.fernet import Fernet
import sqlite3
import bcrypt
import secrets
import string
import os

app = Flask(__name__)
app.secret_key = "mysecretkey123"


csrf = CSRFProtect(app)


KEY_FILE = "secret.key"
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        FERNET_KEY = f.read()
else:
    FERNET_KEY = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(FERNET_KEY)

fernet = Fernet(FERNET_KEY)


def get_db():
    conn = sqlite3.connect("vault.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            site TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if len(password) < 6:
            flash("Password must be at least 6 characters")
            return render_template("register.html")

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                         (username, hashed.decode()))
            conn.commit()
            conn.close()
            flash("Account created! Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already taken.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    entries = conn.execute("SELECT * FROM passwords WHERE user_id = ?",
                           (session["user_id"],)).fetchall()
    conn.close()

   
    decrypted = []
    for e in entries:
        decrypted.append({
            "id": e["id"],
            "site": e["site"],
            "username": e["username"],
            "password": fernet.decrypt(e["password"].encode()).decode()
        })

    return render_template("dashboard.html", entries=decrypted)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        site = request.form["site"]
        username = request.form["username"]
        password = request.form["password"]

        encrypted = fernet.encrypt(password.encode()).decode()

        conn = get_db()
        conn.execute("INSERT INTO passwords (user_id, site, username, password) VALUES (?, ?, ?, ?)",
                     (session["user_id"], site, username, encrypted))
        conn.commit()
        conn.close()
        flash("Password saved!")
        return redirect(url_for("dashboard"))

    return render_template("add.html")


@app.route("/delete/<int:entry_id>")
@login_required
def delete(entry_id):
    conn = get_db()
    conn.execute("DELETE FROM passwords WHERE id = ? AND user_id = ?",
                 (entry_id, session["user_id"]))
    conn.commit()
    conn.close()
    flash("Entry deleted.")
    return redirect(url_for("dashboard"))


@app.route("/generate")
@login_required
def generate():
   
    chars = string.ascii_letters + string.digits + "!@#$%"
    password = "".join(secrets.choice(chars) for _ in range(14))
    return {"password": password}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
