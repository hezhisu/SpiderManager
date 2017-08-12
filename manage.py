import time
from datetime import timedelta

import sys
from flask.ext.script import Manager
__author__ = 'hezhisu'
import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
# manager.add_command('db', MigrateCommand)


@app.template_filter('format_datetime')
def format_datetime(value):
    x = time.localtime(value / 1000)
    return time.strftime('%Y年%m月%d日', x)

@app.template_filter('format_datetime_with_time')
def format_datetime_with_time(value):
    x = time.localtime(value / 1000)
    return time.strftime('%Y-%m-%d %H:%M:%S', x)

@app.template_filter('abosulte_path')
def abosulte_path(path):
    return os.getcwd() + path
#设置session过期时间
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.permanent_session_lifetime = timedelta(minutes=60)

if __name__ == '__main__':
    app.run(debug=True,port=8000)
    # app.run(debug=True)