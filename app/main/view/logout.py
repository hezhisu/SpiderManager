import json

import time
from flask import Blueprint,render_template,request,redirect,url_for
from flask import session
blueprint = Blueprint('logout', __name__,
                      template_folder='templates',
                      static_folder='static')

@blueprint.route('/logout')
def logout():
    session['user'] = ''
    return redirect('/')