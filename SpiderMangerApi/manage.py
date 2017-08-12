from flask import request
from flask_script import Manager, Shell

__author__ = 'hezhisu'
import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
# manager.add_command('db', MigrateCommand)
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response
if __name__ == '__main__':
    # app.run(debug=False,host='0.0.0.0')
    app.run(debug=True)