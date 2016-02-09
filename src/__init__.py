"""A place to define all decorators.

Attributes
----------
    None
"""
from flask import redirect
from flask import url_for
from flask import session

from functools import wraps


def users_only(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if 'player_login' not in session:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_func


def guests_only(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if 'player_login' in session:
            return redirect(url_for('main.homepage'))
        return f(*args, **kwargs)
    return decorated_func


def admins_only(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if 'admin_login' not in session:
            return redirect(url_for('admin.index'))
        return f(*args, **kwargs)
    return decorated_func


def notadmins_only(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if 'admin_login' in session:
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_func
