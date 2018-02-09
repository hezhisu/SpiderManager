from functools import wraps

from flask import session,url_for,redirect
from mongoengine import connect

connect('spider_log')
def check_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if  not session or not session['user']:
            return redirect('/')
        else:
            return func(*args, **kwargs)
    return wrapper