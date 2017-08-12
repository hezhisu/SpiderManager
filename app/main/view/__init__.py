from functools import wraps

from flask import session,url_for,redirect


def check_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if  not session or not session['user']:
            return redirect('/')
        else:
            return func(*args, **kwargs)
    return wrapper