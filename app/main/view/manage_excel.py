import os

from flask import Blueprint,render_template,session
from app.main.view import check_session

blueprint = Blueprint('manage_excel', __name__,
                    template_folder='templates',
                    static_folder='static')

def get_excel(base_dir):
    excel_list = []
    file_list = os.listdir(base_dir)
    print(file_list)
    for file in file_list:
        excel_item = {}
        path = os.path.join(base_dir, file)
        excel_item['name'] = file
        excel_item['size'] = (str)(os.path.getsize(path) / 1000.0) + 'kb'
        excel_item['create_time'] = (int)(os.path.getctime(path) * 1000)
        excel_list.append(excel_item)
    return excel_list
@blueprint.route('/manage/excel')
@check_session
def manage_excel():
    excel_list = get_excel((os.getcwd().replace('\\app\\main\\view','') + "\\excel\\"))
    return render_template('manage_excel.html', select_menu='manage_excel', manager=session['user'],excel_list=excel_list)