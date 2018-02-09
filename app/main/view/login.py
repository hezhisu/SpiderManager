import json
import os
import requests
from flask import Blueprint,render_template,request,redirect,url_for
from flask import session

blueprint = Blueprint('login', __name__,
                      template_folder='templates',
                      static_folder='static')

@blueprint.route('/')
def start():
    return render_template('login.html', erro=0)
@blueprint.route('/login',methods=['POST'])
def login():
    account = request.form['account']
    password = request.form['password']
    if account:
        if password:
            payload = {'account': account, 'password': password}
            r = requests.post('http://59.110.160.234:5000/spider/api/v1/users/manage/login', data=payload)
            print(json.loads(r.text))
            if 'error' in json.loads(r.text):
                return render_template('login.html', erro=1, erromsg=json.loads(r.text)['error'])
            else:
                session['user'] = json.loads(r.text)
                session['file_count'] = len(os.listdir(os.getcwd().replace('\\app\\main\\view', '') + "\\excel\\"))
                return redirect('/manage/task')
        else:
            return render_template('login.html', erro=1, erromsg='密码不能为空!')
    else:
        return render_template('login.html', erro=1, erromsg='用户名不能为空!')
