import json
import time
import uuid

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
user_login_parser = api.parser()
user_login_parser.add_argument('account',required=True,type=str,help='账号',location='form')
user_login_parser.add_argument('password',required=True,type=str,help='密码',location='form')
user_login_parser.add_argument('device_code',required=False,type=str,help='机器码',location='form')
update_use_time_parser = api.parser()
update_use_time_parser.add_argument('use_time',required=True,type=str,help='使用时间',location='form')
update_use_time_parser.add_argument('user_id',required=True,type=str,help='用户ID',location='form')

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

        if user:
            return {'msg':'用户已存在'}
        else:
            user = Users()
            user.account = args['account']
            user.password = args['password']
            user.is_manager = (args['is_manager'] == 'true')
            user.phone = args['phone']
            user.email = args['email']
            user.create_at = time.time() * 1000
            user.save()
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
            if user.use_time == 0:
                user_json['use_time'] = ''
            else:
                user_json['use_time'] = time.strftime('%m/%d/%Y',time.localtime(user.use_time / 1000))
            users_list.append(user_json)
        response_data['draw'] = 1
        response_data['data'] = users_list
        return response_data
    @api.expect(update_use_time_parser)
    def put(self):
        '''
        修改使用时间
        '''
        args = update_use_time_parser.parse_args()
        try:

            use_time = (int)(time.mktime(time.strptime(args['use_time'], '%m/%d/%Y')) * 1000)
            Users.objects(id=args['user_id']).update_one(set__use_time=use_time)
            return {'msg':'修改成功'}
        except Exception as e:
            return {'error': '日期格式错误'}, 400

@api.route('/login')
class UserLoginResource(Resource):
    @api.expect(user_login_parser)
    def post(self):
        '''
        登录
        '''
        args = user_login_parser.parse_args()
        user = Users.objects(account=args['account']).first()
        if not user:
            return {'error': '用户不存在'}
        else:
            if user.password == args['password']:
                if user.device_code :
                    if user.device_code == args['device_code']:
                        if user.use_time == 0 or user.use_time > time.time() * 1000:
                            return {'msg': '登录成功'}
                        else:
                            return {'error': '超过使用时间'}
                    else:
                        return {'error': '机器码授权失败'}
                else:
                    if user.use_time == 0 or user.use_time > time.time() * 1000:
                        user.update(set__device_code=args['device_code'])
                        return {'msg': '登录成功'}
                    else:
                        return {'error': '超过使用时间'}
            else:
                return {'error': '密码错误'}
@api.route('/manage/login')
class ManagerLoginResource(Resource):
    @api.expect(user_login_parser)
    def post(self):
        '''
        后台登录
        '''
        args = user_login_parser.parse_args()
        user = Users.objects(account=args['account']).first()
        if not user:
            return {'error': '用户名错误!'}
        else:
            if user.password == args['password']:
                user.update(set__latest_login_time=time.time() * 1000)
                return json.loads(user.to_json())
            else:
                return {'error': '密码错误!'}


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
    task.private_message = '测试私信发送功能'
    task.save()
    Users.objects(id=task.belong_user_id).update_one(set__task_id=str(task.id))
    return task
