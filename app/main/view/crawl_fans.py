from flask import Blueprint,render_template,session
from app.main.view import check_session

blueprint = Blueprint('crawl_fans', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/crawl/fans')
@check_session
def manage_user():
    return render_template('crawl_fans.html', select_menu='crawl_fans', manager=session['user'])