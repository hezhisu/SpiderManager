from flask import Blueprint,render_template,session
from app.main.view import check_session

blueprint = Blueprint('user', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/manage/user')
@check_session
def manage_user():
    return render_template('manage_user.html', select_menu='manage_user', manager=session['user'])