import os
import win32api
from flask import Blueprint, render_template, session, request, jsonify
from app.main.view import check_session

blueprint = Blueprint('delete_excel', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/delete/excel',methods=['POST'])
@check_session
def delete_excel():
    excel_name = request.form['excel_name']
    os.remove(''.join([os.getcwd().replace('\\app\\main\\view','') , '\\excel\\' , excel_name]))
    return jsonify({'msg': 'ok'})