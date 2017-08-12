from flask import Blueprint,render_template,session
from app.main.view import check_session

blueprint = Blueprint('device_code', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/manage/device_code')
@check_session
def manage_user():
    return render_template('manage_device_code.html', select_menu='manage_device_code', manager=session['user'])