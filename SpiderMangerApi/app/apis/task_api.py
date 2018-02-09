import json

from bson import ObjectId
from flask_restplus import Namespace,Resource

from app.model.TasksModel import Tasks
from app.model.WeiboAccountsModel import WeiboAccounts

api = Namespace('tasks','任务相关api(更新于2017年08月6日)')
add_weibo_user_account_parser = api.parser()
add_weibo_user_account_parser.add_argument('account',required=True,type=str,help='账号',location='form')
add_weibo_user_account_parser.add_argument('password',required=True,type=str,help='密码',location='form')
delete_weibo_user_account_parser = api.parser()
delete_weibo_user_account_parser.add_argument('account',required=True,type=str,help='账号',location='form')
get_task_parser = api.parser()
get_task_parser.add_argument('user_id',required=True,type=str,help='账号',location='args')
get_task_parser.add_argument('ignore_verify',required=False,type=int,help='是否忽略验证',location='args')
update_task_parser = api.parser()
update_task_parser.add_argument('spider_interval',required=True,type=str,help='爬取时间间隔',location='form')
update_task_parser.add_argument('switch_account_interval',required=True,type=str,help='切换账号时间间隔',location='form')

task_args = {'code':'状态码','cache':'缓存','account':'账号'}

def get_custom_api_doc(notice,code):
    return '{0}<br><br><pre>`{1}`</pre>'.format(notice,json.dumps(code, indent=4, ensure_ascii=False))
@api.route('')
class TasksResource(Resource):
    @api.expect(get_task_parser)
    @api.doc(description=get_custom_api_doc('字段说明',task_args))
    def get(self):
        '''
        获取任务
        '''
        args = get_task_parser.parse_args()
        task = Tasks.objects(belong_user_id=args['user_id']).first()
        if args['ignore_verify'] and args['ignore_verify'] == 1:
            return json.loads(task.to_json())
        else:
            if len(task.mail_list) == 0:
                return {'error':'至少填写一个邮箱'},400
            if len(task.spider_user_ids) == 0:
                return {'error':'至少填写一个爬取的微博用户id'},400
            if len(task.weibo_accounts) == 0:
                return {'error':'至少填写一个微博账号用于登录'},400
            return json.loads(task.to_json())
@api.route('/<string:task_id>')
class TaskResource(Resource):
    @api.expect(update_task_parser)
    @api.doc('更新任务')
    def put(self,task_id):
        '''
        更新任务
        '''
        args = update_task_parser.parse_args()
        Tasks.objects(id=task_id).update_one(set__spider_interval=args['spider_interval'])
        Tasks.objects(id=task_id).update_one(set__switch_account_interval=args['switch_account_interval'])
        return {'msg':'更新成功'}

@api.route('/<string:task_id>/weibo_accounts')
class WeiboAccountsResource(Resource):
    @api.expect(add_weibo_user_account_parser)
    @api.doc('添加微博账号')
    def post(self,task_id):
        '''
        添加微博账号
        '''
        args = add_weibo_user_account_parser.parse_args()
        weibo_account = WeiboAccounts()
        weibo_account.account = args['account']
        weibo_account.password = args['password']
        Tasks.objects(id=task_id).update_one(push__weibo_accounts=weibo_account)
        return {'msg':'添加成功'}

    @api.expect(delete_weibo_user_account_parser)
    @api.doc('删除微博账号')
    def delete(self, task_id):
        '''
        删除微博账号
        '''
        args = delete_weibo_user_account_parser.parse_args()
        task = Tasks.objects(id=task_id).first()
        weibo_accounts = []
        if task:
            for account in task.weibo_accounts:
                if not account.account == args['account']:
                    weibo_accounts.append(account)
            task.update(set__weibo_accounts=weibo_accounts)
            return {'msg': '删除成功'}
        else:
            return {'error':'任务不存在'},400

spider_user_parser = api.parser()
spider_user_parser.add_argument('user_id',required=True,type=str,help='微博用户ID',location='form')
@api.route('/<string:task_id>/spider_users')
class SpiderUsersResource(Resource):
    @api.expect(spider_user_parser)
    @api.doc('添加爬取用户')
    def post(self,task_id):
        '''
        添加爬取用户
        '''
        args = spider_user_parser.parse_args()
        Tasks.objects(id=task_id).update_one(push__spider_user_ids=args['user_id'])
        return {'msg':'添加成功'}

    @api.expect(spider_user_parser)
    def delete(self,task_id):
        '''
        删除爬取用户
        '''
        args = spider_user_parser.parse_args()
        task = Tasks.objects(id=task_id).first()
        if task:
            task.spider_user_ids.remove(args['user_id'])
            task.update(set__spider_user_ids=task.spider_user_ids)
            return {'msg': '删除成功'}
        else:
            return {'error': '任务不存在'}, 400

spider_keyword_parser = api.parser()
spider_keyword_parser.add_argument('keyword',required=True,type=str,help='爬取关键字',location='form')
@api.route('/<string:task_id>/spider_keywords')
class KeywordsResource(Resource):
    @api.expect(spider_keyword_parser)
    @api.doc('添加爬取关键字')
    def post(self,task_id):
        '''
        添加爬取关键字
        '''
        args = spider_keyword_parser.parse_args()
        Tasks.objects(id=task_id).update_one(push__spider_keywords=args['keyword'])
        return {'msg':'添加成功'}

    @api.expect(spider_keyword_parser)
    def delete(self,task_id):
        '''
        删除爬取关键字
        '''
        args = spider_keyword_parser.parse_args()
        task = Tasks.objects(id=task_id).first()
        if task:
            task.spider_keywords.remove(args['keyword'])
            task.update(set__spider_keywords=task.spider_keywords)
            return {'msg': '删除成功'}
        else:
            return {'error': '任务不存在'}, 400

spider_extra_keyword_parser = api.parser()
spider_extra_keyword_parser.add_argument('extra_keyword',required=True,type=str,help='爬取否定关键字',location='form')
@api.route('/<string:task_id>/spider_extra_keywords')
class ExtraKeywordsResource(Resource):
    @api.expect(spider_extra_keyword_parser)
    @api.doc('添加爬取否定关键字')
    def post(self,task_id):
        '''
        添加爬取否定关键字
        '''
        args = spider_extra_keyword_parser.parse_args()
        Tasks.objects(id=task_id).update_one(push__spider_extra_keywords=args['extra_keyword'])
        return {'msg':'添加成功'}

    @api.expect(spider_extra_keyword_parser)
    def delete(self,task_id):
        '''
        删除爬取否定关键字
        '''
        args = spider_extra_keyword_parser.parse_args()
        task = Tasks.objects(id=task_id).first()
        if task:
            task.spider_extra_keywords.remove(args['extra_keyword'])
            task.update(set__spider_extra_keywords=task.spider_extra_keywords)
            return {'msg': '删除成功'}
        else:
            return {'error': '任务不存在'}, 400

add_mail_parser = api.parser()
add_mail_parser.add_argument('mail',required=True,type=str,help='邮箱',location='form')
@api.route('/<string:task_id>/mails')
class KeywordsResource(Resource):
    @api.expect(add_mail_parser)
    @api.doc('添加邮箱')
    def post(self,task_id):
        '''
        添加邮箱
        '''
        args = add_mail_parser.parse_args()
        Tasks.objects(id=task_id).update_one(push__mail_list=args['mail'])
        return {'msg':'添加成功'}

    @api.expect(add_mail_parser)
    def delete(self,task_id):
        '''
        删除邮箱
        '''
        args = add_mail_parser.parse_args()
        task = Tasks.objects(id=task_id).first()
        if task:
            task.mail_list.remove(args['mail'])
            task.update(set__mail_list=task.mail_list)
            return {'msg': '删除成功'}
        else:
            return {'error': '任务不存在'}, 400



set_private_message_parser = api.parser()
set_private_message_parser.add_argument('private_message',required=True,type=str,help='邮箱',location='form')
@api.route('/<string:task_id>/private_message')
class PrivateMessageResource(Resource):
    @api.expect(set_private_message_parser)
    @api.doc('设置私信')
    def put(self,task_id):
        '''
        设置私信
        '''
        args = set_private_message_parser.parse_args()
        Tasks.objects(id=task_id).update(set__private_message=args['private_message'])
        return {'msg':'设置成功'}

