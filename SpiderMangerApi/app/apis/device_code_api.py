import random
import string

from flask_restplus import Namespace,Resource

from app.model.DeviceCodeModel import DeviceCode
from app.model.UsersModel import Users


def GenCode(length):
    #随机出数字的个数
    numOfNum = random.randint(1,length-1)
    numOfLetter = length - numOfNum
    #选中numOfNum个数字
    slcNum = [random.choice(string.digits) for i in range(numOfNum)]
    #选中numOfLetter个字母
    slcLetter = [random.choice(string.ascii_letters) for i in range(numOfLetter)]
    #打乱这个组合
    slcChar = slcNum + slcLetter
    random.shuffle(slcChar)
    #生成密码
    genCode = ''.join([i for i in slcChar])
    return genCode

api = Namespace('device_codes','机器码api(更新于2017年08月8日)')
@api.route('')
class DeviceCodesResource(Resource):
    @api.doc('添加机器码')
    def post(self):
        '''
        添加机器码
        '''
        device_code = DeviceCode()
        device_code.code = GenCode(6)
        device_code.save()
        return {'msg':'添加成功'}
    def get(self):
        '''
        获取机器码
        '''
        response_data={}
        device_codes = DeviceCode.objects()
        device_code_list = []
        for device_code in device_codes:
            device_code_json = {}
            device_code_json['id'] = str(device_code.id)
            device_code_json['code'] = device_code.code
            device_code_json['bind_user'] = device_code.bind_user
            try:
                user = Users.objects(id=device_code.bind_user).first()
                if not user:
                    device_code_json['bind_user'] = ''
                else:
                    device_code_json['bind_user_account'] = user.account
            except Exception as e:
                device_code_json['bind_user'] = ''
                device_code_json['bind_user_account'] = ''
            device_code_list.append(device_code_json)
        response_data['draw'] = 1
        response_data['data'] = device_code_list
        return response_data

bind_user_parser = api.parser()
bind_user_parser.add_argument('user_id',required=True,type=str,help='用户ID',location='form')
@api.route('/<string:code_id>')
class DeviceCodeResource(Resource):
    @api.doc('删除机器码')
    def delete(self,code_id):
        '''
        删除机器码
        '''
        DeviceCode.objects(id=code_id).delete()
        return {'msg':'删除成功'}

    @api.expect(bind_user_parser)
    def put(self,code_id):
        '''
        解绑用户
        '''
        args = bind_user_parser.parse_args()
        DeviceCode.objects(id=code_id).update_one(set__bind_user='')
        Users.objects(id=args['user_id']).update_one(set__device_code='')
        return {'msg':'解绑成功'}
    @api.expect(bind_user_parser)
    def post(self,code_id):
        '''
        绑定用户
        '''
        args = bind_user_parser.parse_args()
        try:
            user = Users.objects(id=args['user_id']).first()
            if not user:
                return {'error':'用户不存在'},404
            else:
                if not user.device_code == '':
                    return {'error': '用户已绑定'}, 400
                else:
                    device_code = DeviceCode.objects(id=code_id).first()
                    device_code.update(set__bind_user=args['user_id'])
                    Users.objects(id=args['user_id']).update_one(set__device_code=device_code.code)
                    return {'msg':'绑定成功'}
        except Exception as e:
            return {'error': '用户不存在'}, 404


