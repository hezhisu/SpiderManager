from flask import Blueprint,render_template,session,redirect

from app.main.model.TasksModel import Tasks
from app.main.model.UsersModel import Users
from app.main.model.WeiboAccountsModel import WeiboAccounts
from app.main.view import check_session

blueprint = Blueprint('index', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/manage/task')
@check_session
def index():
    task = Tasks.objects(belong_user_id = session['user']['_id']['$oid']).first()
    return render_template('index.html',manager = session['user'],select_menu='manage_task',task=task)


