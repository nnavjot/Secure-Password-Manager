

from flask import Blueprint, render_template, session, redirect, url_for

vault_bp = Blueprint("vault", __name__)


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@vault_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("vault/dashboard.html", username=session["username"])
