import os
import win32api
from flask import Blueprint, render_template, session, request, jsonify
from app.main.view import check_session

blueprint = Blueprint('view_excel', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/view/excel',methods=['POST'])
@check_session
def view_excel():
    excel_name = request.form['excel_name']
    win32api.ShellExecute(0, 'open', ''.join(
        [os.getcwd().replace('\\app\\main\\view', ''), '\\excel\\', excel_name]), '', '', 1)
    return jsonify({'msg':'ok'})