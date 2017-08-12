from flask import Blueprint
from flask_restplus import Api
from app.apis.user_api import api as user_namespace
from app.apis.task_api import api as task_namespace
from app.apis.device_code_api import api as device_namespace
__author__ = 'hezhisu'
api_v1 = Blueprint('api_v1', __name__,url_prefix='/spider/api/v1')
api1 = Api(api_v1,
    title='微博云控API',
    version='1.0',
    description='API文档',
    doc='/doc/'
    # All API metadatas
)

api1.add_namespace(user_namespace)
api1.add_namespace(task_namespace)
api1.add_namespace(device_namespace)