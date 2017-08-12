import json
import os

import time
from flask import Blueprint,render_template,request,redirect,url_for
from flask import session

from app.main.model.UsersModel import Users

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
    user = Users.objects(account=account).first()
    if account:
        if password:
            if not user:
                return render_template('login.html', erro=1, erromsg='用户名错误!')
            else:
                if user.password != password:
                    return render_template('login.html', erro=1, erromsg='密码错误!')
                else:
                    if user.device_code == '':
                        return render_template('login.html', erro=1, erromsg='用户未绑定机器码！')
                    else:
                        user.update(set__latest_login_time=time.time() * 1000)
                        user_json = json.loads(user.to_json())
                        session['user'] = user_json
                        session['file_count'] = len(os.listdir(os.getcwd().replace('\\app\\main\\view','') + "\\excel\\"))
                        return redirect('/manage/task')
        else:
            return render_template('login.html', erro=1, erromsg='密码不能为空!')
    else:
        return render_template('login.html', erro=1, erromsg='用户名不能为空!')
