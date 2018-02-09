from flask import Blueprint,render_template,session
from app.main.view import check_session

blueprint = Blueprint('crawl_comments', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/crawl/comments')
@check_session
def manage_user():
    return render_template('crawl_comments.html', select_menu='crawl_comments', manager=session['user'])