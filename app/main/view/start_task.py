import os
import win32api
from flask import Blueprint, render_template, session, request, jsonify
from app.main.view import check_session

blueprint = Blueprint('start_task', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/start/task',methods=['POST'])
@check_session
def start_task():
    task_json = request.form['task_json']
    print(task_json)
    config_file = open(os.getcwd().replace('\\app\\main\\view','') + '\\spider\\config.json', encoding='utf8',mode='w+')
    config_file.write(task_json)
    config_file.close()
    win32api.ShellExecute(0, 'open', os.getcwd().replace('\\app\\main\\view','') + '\\redis\\redis-server.exe', '', '', 1)
    win32api.ShellExecute(0, 'open', os.getcwd().replace('\\app\\main\\view','') + '\\spider\\spider.exe', '', '', 1)
    return jsonify({'msg': 'ok'})