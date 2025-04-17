from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorate routes to require admin privileges.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("You don't have permission to access this page", "danger")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function