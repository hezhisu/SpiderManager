import os

from flask import Flask
from app.main.view.login import blueprint as login_blueprint
from app.main.view.index import blueprint as index_blueprint
from app.main.view.manage_user import blueprint as manage_user_blueprint
from app.main.view.manage_device_code import blueprint as manage_device_code_blueprint
from app.main.view.manage_excel import blueprint as manage_excel_blueprint
from app.main.view.start_task import blueprint as start_task_blueprint
from app.main.view.delete_excel import blueprint as delete_excel_blueprint
from app.main.view.view_excel import blueprint as view_excel_blueprint
from app.main.view.logout import blueprint as logout_blueprint
from app.main.view.file_watcher import blueprint as file_watcher_blueprint
__author__ = 'hezhisu'
def getcwd():
    return os.getcwd()
def create_app(config_name):
    app = Flask(__name__,static_url_path='')

    app.register_blueprint(login_blueprint)
    app.register_blueprint(index_blueprint)
    app.register_blueprint(manage_user_blueprint)
    app.register_blueprint(manage_device_code_blueprint)
    app.register_blueprint(manage_excel_blueprint)
    app.register_blueprint(start_task_blueprint)
    app.register_blueprint(delete_excel_blueprint)
    app.register_blueprint(view_excel_blueprint)
    app.register_blueprint(logout_blueprint)
    app.register_blueprint(file_watcher_blueprint)
    app.jinja_env.globals.update(getcwd=getcwd)

    # attach routes and custom error pages here
    return app