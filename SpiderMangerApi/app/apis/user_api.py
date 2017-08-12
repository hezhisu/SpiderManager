import json
import time
from flask_restplus import Namespace,Resource

from app.model.DeviceCodeModel import DeviceCode
from app.model.TasksModel import Tasks
from app.model.UsersModel import Users
from app.model.WeiboAccountsModel import WeiboAccounts

api = Namespace('users','用户相关api(更新于2017年08月5日)')
add_user_api_parser = api.parser()
add_user_api_parser.add_argument('account',required=True,type=str,help='账号',location='form')
add_user_api_parser.add_argument('password',required=True,type=str,help='密码',location='form')
add_user_api_parser.add_argument('is_manager',required=True,type=str,help='是否是管理员',location='form')
add_user_api_parser.add_argument('phone',required=False,type=str,help='手机号码',location='form')
add_user_api_parser.add_argument('email',required=False,type=str,help='邮箱',location='form')
add_user_api_parser.add_argument('device_code',required=False,type=str,help='机器码',location='form')

@api.route('')
class UsersResource(Resource):
    @api.expect(add_user_api_parser)
    @api.doc('添加用户')
    def post(self):
        '''
        添加用户
        '''
        args = add_user_api_parser.parse_args()
        user = Users.objects(account = args['account']).first()
        device_code = DeviceCode.objects(code=args['device_code']).first()
        if not device_code:
            return {'error': '机器码不存在'},404
        if device_code.bind_user:
            return {'error': '机器码已绑定'},400
        if user:
            return {'msg':'用户已存在'}
        else:
            user = Users()
            user.account = args['account']
            user.password = args['password']
            user.is_manager = (args['is_manager'] == 'true')
            user.phone = args['phone']
            user.email = args['email']
            user.device_code = args['device_code']
            user.create_at = time.time() * 1000
            user.save()
            DeviceCode.objects(code=args['device_code']).update_one(set__bind_user=str(user.id))
            make_default_task(str(user.id))
            return {'msg':'添加用户成功'}
    def get(self):
        '''
        获取用户列表
        '''
        users = Users.objects()
        users_list = []

        response_data = {}
        for user in users:
            user_json = {}
            user_json['user_id'] = str(user.id)
            user_json['phone'] = user.phone
            user_json['account'] = user.account
            user_json['create_at'] = user.create_at
            user_json['email'] = user.email
            user_json['device_code'] = user.device_code
            user_json['is_manager'] = user.is_manager
            user_json['task_id'] = user.task_id
            user_json['task'] = json.loads(Tasks.objects(id=user.task_id).first().to_json())
            users_list.append(user_json)
        response_data['draw'] = 1
        response_data['data'] = users_list
        return response_data
def make_default_task(user_id):
    task = Tasks()
    task.belong_user_id = user_id
    account = WeiboAccounts()
    account.account = '18855408432'
    account.password = 'a00000000'
    task.weibo_accounts = []
    task.weibo_accounts.append(account)
    task.spider_user_ids = ['5538536107','1723931634']
    task.spider_keywords = ['无人','自动无人']
    task.spider_extra_keywords = ['@','还没','网友']
    task.spider_interval = 13
    task.switch_account_interval = 7
    task.mail_list = ['379129087@qq.com']
    task.save()
    Users.objects(id=task.belong_user_id).update_one(set__task_id=str(task.id))
    return task