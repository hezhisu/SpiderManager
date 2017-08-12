import os
import win32api
from flask import Blueprint, render_template, session, request, jsonify
from app.main.view import check_session

blueprint = Blueprint('file_watcher', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/file/watcher')
@check_session
def file_watcher():
    print('polling file_watcher')
    file_count = len(os.listdir(os.getcwd().replace('\\app\\main\\view','') + "\\excel\\"))
    if file_count > session['file_count']:
        session['file_count'] = file_count
        return jsonify({'code': True})
    else:
        return jsonify({'code': False})