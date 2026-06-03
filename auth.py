from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, g
)
import bcrypt
from datetime import datetime, timedelta
from database import get_db

auth_bp = Blueprint("auth", __name__)



def hash_password(plaintext: str) -> str:
    """Return a bcrypt hash string (salt is embedded in the digest)."""
    # cost factor 12 — ~300ms on modern hardware, acceptable UX / strong defence
    return bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt(rounds=12)).decode()


def check_password(plaintext: str, hashed: str) -> bool:
    """Constant-time comparison; returns True if password matches."""
    return bcrypt.checkpw(plaintext.encode(), hashed.encode())



@auth_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("vault.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("vault.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        

        

        db = get_db()

        existing = db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()

        if existing:
            flash("Username or email already registered.", "error")
            return render_template("auth/register.html")

        pw_hash = hash_password(password)

        db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, pw_hash)
        )
        db.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("vault.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and user["locked_until"]:
            locked_until = datetime.fromisoformat(user["locked_until"])
            if datetime.utcnow() < locked_until:
                remaining = int((locked_until - datetime.utcnow()).seconds / 60) + 1
                flash(f"Account locked. Try again in {remaining} minute(s).", "error")
                return render_template("auth/login.html")
            else:
                db.execute(
                    "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
                    (user["id"],)
                )
                db.commit()

       
        
        db.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
            (user["id"],)
        )
        db.commit()

        session.clear()
        session["user_id"]  = user["id"]
        session["username"] = user["username"]
        session.permanent   = False  
        return redirect(url_for("vault.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
