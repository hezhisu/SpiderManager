import json

import requests
from flask import Blueprint,render_template,session,redirect

from app.main.view import check_session

blueprint = Blueprint('index', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/manage/task')
@check_session
def index():
    payload = {'user_id': session['user']['_id']['$oid'], 'ignore_verify': 1}
    r = requests.get("http://59.110.160.234:5000/spider/api/v1/tasks", params=payload)
    print(json.loads(r.text))
    return render_template('index.html',manager = session['user'],select_menu='manage_task',task=json.loads(r.text))


