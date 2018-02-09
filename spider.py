import getopt
import json
import threading

import sys
import uuid

import xlrd,xlsxwriter
import time
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import rsa
import math
import random
import binascii
import requests
import re
from urllib.parse import quote_plus
import base64
import binascii
import json
import os
import random
import re
import time
from collections import OrderedDict

import math
import requests
import rsa
from bs4 import BeautifulSoup
import redis
from mongoengine import connect, Document, StringField, IntField

connect('spider_log')
my_redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
mail_user = 'pa1@21v.net'
mail_password = 'Aa00000000'
agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
headers = {
    'User-Agent': agent
}
profile_request_params = {"profile_ftype":"1","is_all":"1"}
profile_request_params_hot = {"profile_ftype":"1","is_hot":"1"}
session = requests.session()
# 访问 初始页面带上 cookie
index_url = "http://weibo.com/login.php"
yundama_username = '526510100'
yundama_password = 'a00000000'
verify_code_path = './pincode.png'
class Config:
    def __init__(self):
        path = sys.path[0] + "/config.json"
        configFile = open(path, 'r',encoding='utf-8')
        try:
            configJson = json.load(configFile)
            self.weibo_accounts = configJson["weibo_accounts"]
            self.spider_user_ids = configJson["spider_user_ids"]
            self.spider_keywords = configJson["spider_keywords"]
            self.spider_extra_keywords = configJson["spider_extra_keywords"]
            self.mail_list = configJson["mail_list"]
            self.spider_interval = configJson["spider_interval"]
            self.switch_account_interval = configJson["switch_account_interval"]
            self.private_message = configJson["private_message"]
        except Exception as e:
            print(e.args)
        finally:
            configFile.close()


config = Config()


class Comment(Document):
    host_id = StringField(required=True)
    host_nickname = StringField(required=True)
    weibo_content = StringField(required=True)
    weibo_link = StringField(required=True)
    comment_user = StringField(required=True)
    comment_content = StringField(required=True)
    comment_time = StringField(required=True)
    create_at = IntField(required=True)

class Fans(Document):
    host_id = StringField(required=True)
    host_nickname = StringField(required=True)
    fans_id = StringField(required=True)
    nickname = StringField(required=True)
    gender = StringField(required=True)
    create_at = IntField(required=True)


def filter_tags(htmlstr):
    # 先过滤CDATA
    re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
    re_br = re.compile('<br\s*?/?>')  # 处理换行
    re_h = re.compile('</?\w+[^>]*>')  # HTML标签
    re_comment = re.compile('<!--[^>]*-->')  # HTML注释
    s = re_cdata.sub('', htmlstr)  # 去掉CDATA
    s = re_script.sub('', s)  # 去掉SCRIPT
    s = re_style.sub('', s)  # 去掉style
    s = re_br.sub('\n', s)  # 将br转换为换行
    s = re_h.sub('', s)  # 去掉HTML 标签
    s = re_comment.sub('', s)  # 去掉HTML注释
    # 去掉多余的空行
    blank_line = re.compile('\n+')
    s = blank_line.sub('\n', s)
    s = replaceCharEntity(s)  # 替换实体
    return s


def replaceCharEntity(htmlstr):
    CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                     'lt': '<', '60': '<',
                     'gt': '>', '62': '>',
                     'amp': '&', '38': '&',
                     'quot': '"', '34': '"', }

    re_charEntity = re.compile(r'&#?(?P<name>\w+);')
    sz = re_charEntity.search(htmlstr)
    while sz:
        entity = sz.group()  # entity全称，如&gt;
        key = sz.group('name')  # 去除&;后entity,如&gt;为gt
        try:
            htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
            sz = re_charEntity.search(htmlstr)
        except KeyError:
            # 以空串代替
            htmlstr = re_charEntity.sub('', htmlstr, 1)
            sz = re_charEntity.search(htmlstr)
    return htmlstr


def task(uid, keyword, extra_keyword, interval,private_message):
    if not os.path.exists(os.getcwd() + '/excel'):
        os.makedirs(os.getcwd() + '/excel')
    if not os.path.exists(os.getcwd() + '/fansexcel'):
        os.makedirs(os.getcwd() + '/fansexcel')
    for item in uid:
        time.sleep(interval)
        spider_task(item, keyword, extra_keyword, True,private_message)
        time.sleep(interval)
        spider_task(item, keyword, extra_keyword, False,private_message)


def spider_fans(uid,nickname,last_fans_id,private_message):
    if last_fans_id:
        print('last_fans_id : ' + last_fans_id)
    else:
        print('last_fans_id : ')
    fans_ids = []
    fans_items = []
    fans_objects = []
    for i in range(5):
        try:
            url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{0}&type=all&since_id={1}'.format(uid,i + 1)
            response = requests.get(url)
            fans = json.loads(response.text)['data']['cards']
            if len(fans) > 0:
                for fan in fans[0]['card_group']:
                    fans_item = OrderedDict({})
                    fans_object = Fans()
                    if last_fans_id == str(fan['user']['id']):
                        print(fans_items)
                        return fans_items
                    fans_object.host_id = uid
                    fans_object.host_nickname = nickname
                    fans_item['id'] = str(fan['user']['id'])
                    fans_object.fans_id = fans_item['id']
                    fans_item['nickname'] = fan['user']['screen_name']
                    fans_object.nickname = fans_item['nickname']
                    if fan['user']['gender'] == 'm':
                        fans_item['gender'] = '男'
                    else:
                        fans_item['gender'] = '女'
                    fans_object.gender = fans_item['gender']

                    fans_item['host_id'] = uid
                    fans_item['host_nickname'] = nickname
                    fans_object.create_at = time.time() * 1000
                    if fan['user']['id'] in fans_ids:
                        continue
                    fans_items.append(fans_item)
                    fans_objects.append(fans_object)
                    fans_ids.append(fan['user']['id'])
        except Exception as e:
            continue
    print(fans_items)

    for item in fans_objects:
        if Fans.objects(fans_id = item.fans_id).first() is None:
            item.save()
            send_message(private_message,item.fans_id)
    return fans_items


def send_message(text,to):
    requestUrl = 'https://api.weibo.com/webim/2/direct_messages/new.json?source=209678993'
    request_params = {}

    request_params["uid"] = to
    request_params["text"] = text
    session.headers['Referer'] = 'https://api.weibo.com/chat/'
    response = session.post(requestUrl,data=request_params)
    print(response.text)

def spider_task(uid, keyword, extra_keyword, is_hot, private_message):
    print('do task')
    comments_ids = []
    try:
        profile_url = 'http://weibo.com/u/{0}?'.format(uid)
        profile_request_params["page"] = 1
        response = session.get(profile_url, params=profile_request_params_hot if is_hot else profile_request_params)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        script_list = soup.find_all("script")
        script_size = len(script_list)
        tag = 0
        for x in range(script_size):
            if "WB_feed WB_feed_v3 WB_feed_v4" in str(script_list[x]):
                tag = x
        # print script_list[script_size-1]
        html_start = str(script_list[tag]).find("<div")
        html_end = str(script_list[tag]).rfind("div>")
        soup_child = BeautifulSoup(str(str(script_list[tag])[html_start:html_end + 4]).replace("\\", "")
                                   .replace("n", "").replace("r", ""), 'html.parser')
        weibo_items = []
        nickname = soup_child.find('a',class_='W_f14 W_fb S_txt1').string
        for item in soup_child.findAll('a', class_='S_txt2'):
            weibo_item = {}
            s = eval(str(item.attrs)).get('suda-uatack')
            if s:
                if s.find('commet') > -1 and s.find('feed_tas_weibo') == -1:
                    weibo_item['id'] = s.split(':')[1]
                    weibo_items.append(weibo_item)
        for index, item in enumerate(soup_child.find_all('div', class_='WB_text W_f14')):
            if (index < len(weibo_items)):
                weibo_items[index]['content'] = filter_tags(str(item)).replace(' ', '')
        index = -1
        for item in soup_child.find_all('a', class_='S_txt2'):
            s = eval(str(item.attrs)).get('suda-data')
            if s:
                if index < len(weibo_items):
                    id_char = eval(str(item.attrs)).get('hef').split('?')[0].replace('/' + uid + '/', '')
                    index = index + 1
                    weibo_items[index]['link'] = 'http://weibo.com/' + uid + '/' + id_char
        print(weibo_items)

        weibo_comments = []
        last_fans_id = my_redis.get('fans_' + uid)
        fans_items = spider_fans(uid,nickname,last_fans_id,private_message)
        if len(fans_items) > 0:
            my_redis.set('fans_' + uid, fans_items[0]['id'])
            json_list_to_excel(fans_items,
                               ['粉丝ID', '粉丝昵称', '粉丝性别','同行ID','同行昵称']
                               , os.getcwd() + '/fansexcel/fans_{0}_{1}_{2}.xlsx'.format(uid, nickname, str(int(time.time()))))
        comment_objects = []
        for weibo_item in weibo_items:
            this_weibo_last_comment_content = my_redis.get(weibo_item['id'])
            response =requests.get ('https://m.weibo.cn/api/comments/show?id={0}'.format(weibo_item['id']))
            comments = []
            if 'data' in json.loads(response.text):
                print('has data')
                comments = json.loads(response.text)['data']['data']
                print(comments)
            for comment in comments:
                is_add = False
                comment_object = Comment()
                comment_object.host_nickname = nickname
                weibo_comment = OrderedDict({})
                comment_object.host_id = uid
                weibo_comment['comment_user'] = str(comment['user']['id'])
                weibo_comment['comment_user_link'] = 'https://weibo.com/u/' + str(comment['user']['id'])
                weibo_comment['weibo_content'] = weibo_item['content']
                comment_object.weibo_content = weibo_comment['weibo_content']
                weibo_comment['weibo_link'] = weibo_item['link']
                comment_object.weibo_link = weibo_comment['weibo_link']
                comment_object.comment_user = str(comment['user']['id'])
                comment_content = filter_tags(comment['text'])
                weibo_comment['comment_content'] = comment_content
                comment_object.comment_content = weibo_comment['comment_content']
                weibo_comment['comment_time'] = comment['created_at']
                comment_object.comment_time = weibo_comment['comment_time']

                weibo_comment['host_id'] = uid
                weibo_comment['host_nickname'] = nickname
                comment_object.create_at = time.time() * 1000
                if this_weibo_last_comment_content == str(comment['id']):
                    break
                print(keyword)
                if len(keyword) == 0 and weibo_comment['comment_user'] not in comments_ids:
                    print("append")
                    weibo_comments.append(weibo_comment)
                    comment_objects.append(comment_object)
                    comments_ids.append(weibo_comment['comment_user'])
                    continue
                is_in_key = False
                for k in keyword:
                    if comment_content.find(k) > -1:
                        is_in_key = True
                        break
                is_in_extra_key = False
                for e in extra_keyword:
                    if comment_content.find(e) > -1:
                        is_in_extra_key = True
                        break
                if is_in_key and not is_in_extra_key and weibo_comment['comment_user'] not in comments_ids:
                    weibo_comments.append(weibo_comment)
                    comment_objects.append(comment_object)
                    comments_ids.append(weibo_comment['comment_user'])
            if len(comments) > 0:
                my_redis.set(weibo_item['id'], str(comments[0]['id']))
        if len(weibo_comments) > 0:
            Comment.objects.insert(comment_objects)
            json_list_to_excel(weibo_comments,
                               ['评论人ID', '评论人主页', '当前微博内容', '当前微博链接', '客户回复内容', '咨询回复时间','同行ID','同行昵称']
                               , os.getcwd() + '/excel/comments_{0}_{1}_{2}.xlsx'.format(uid,nickname,str(int(time.time()))))
            send_mail("pa1@21v.net", weibo_comments[0]['comment_content'], weibo_comments[0]['weibo_content'],
                      [os.getcwd() + '/excel/comments_{0}_{1}_{2}.xlsx'.format(uid,nickname,str(int(time.time())))])
        print(weibo_comments)
    except Exception as e:
        print(e.args)
    finally:
        pass
def perfirm(uid,keyword,extra_keyword,interval,private_message):
    task(uid=uid,keyword=keyword,extra_keyword=extra_keyword,interval=interval,private_message=private_message)
def getAccount(index):
    return config.weibo_accounts[index]
def json_list_to_excel(json_list,excel_title,out_excel_file):
    """
    将字典写入excel中
    :type dict_content: object dict
    excel_title 列标题
    """
    excel_init_file = xlsxwriter.Workbook(out_excel_file)
    table = excel_init_file.add_worksheet('bas_info')
    title_bold = excel_init_file.add_format({'bold': True, 'border': 2, 'bg_color':'gray'})
    border = excel_init_file.add_format({ 'border': 1})
    for i,j in enumerate(excel_title):
        table.set_column(i,i,len(j)+1)
        table.write_string(0,i,j,title_bold)
    for i, json_item in enumerate(json_list):
        j = 0
        for k,v in json_item.items():
            table.write_string(i + 1,j,v,border)
            j = j + 1

    excel_init_file.close()
    print('save excel success')
#发送邮件
def send_mail(mail_from, subject, msg_txt, files=[]):
    print('send email begin')
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = ','.join(config.mail_list)

    # Create the body of the message (a plain-text and an HTML version).
    #text = msg
    content = msg_txt

    # Record the MIME types of both parts - text/plain and text/html.

    # part1 = MIMEText(content, 'plain')
    part2 = MIMEText(content, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    #msg.attach(part1)
    msg.attach(part2)

    #attachment
    for f in files:
        #octet-stream:binary data
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    # Send the message via local SMTP server.
    s = smtplib.SMTP_SSL(host = 'smtp.mxhichina.com', port=465)
    s.login(mail_user,mail_password)
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(mail_from, config.mail_list, msg.as_string())

    s.quit()
    print('send email success')
    return True

def get_pincode_url(pcid):
    size = 0
    url = "http://login.sina.com.cn/cgi/pin.php"
    pincode_url = '{}?r={}&s={}&p={}'.format(url, math.floor(random.random() * 100000000), size, pcid)
    return pincode_url


def get_img(url):
    resp = requests.get(url, headers=headers, stream=True)
    with open(verify_code_path, 'wb') as f:
        for chunk in resp.iter_content(1000):
            f.write(chunk)


def get_su(username):
    """
    对 email 地址和手机号码 先 javascript 中 encodeURIComponent
    对应 Python 3 中的是 urllib.parse.quote_plus
    然后在 base64 加密后decode
    """
    username_quote = quote_plus(username)
    username_base64 = base64.b64encode(username_quote.encode("utf-8"))
    return username_base64.decode("utf-8")


# 预登陆获得 servertime, nonce, pubkey, rsakv
def get_server_data(su):
    pre_url = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su="
    pre_url = pre_url + su + "&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_="
    prelogin_url = pre_url + str(int(time.time() * 1000))
    pre_data_res = session.get(prelogin_url, headers=headers)

    sever_data = eval(pre_data_res.content.decode("utf-8").replace("sinaSSOController.preloginCallBack", ''))

    return sever_data


# 这一段用户加密密码，需要参考加密文件
def get_password(password, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)  # 创建公钥,
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)  # 拼接明文js加密文件中得到
    message = message.encode("utf-8")
    passwd = rsa.encrypt(message, key)  # 加密
    passwd = binascii.b2a_hex(passwd)  # 将加密信息转换为16进制。
    return passwd

class YDMHttp:
    apiurl = 'http://api.yundama.com/api.php'
    username = ''
    password = ''
    appid = ''
    appkey = ''

    def __init__(self, name, passwd, app_id, app_key):
        self.username = name
        self.password = passwd
        self.appid = str(app_id)
        self.appkey = app_key

    def request(self, fields, files=[]):
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response

    def balance(self):
        data = {
            'method': 'balance',
            'username': self.username,
            'password': self.password,
            'appid': self.appid,
            'appkey': self.appkey
        }
        response = self.request(data)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if response:
            if response['ret'] and response['ret'] < 0:
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, file_name, code_type, time_out):
        cid = self.upload(file_name, code_type, time_out)
        if cid > 0:
            for i in range(0, time_out):
                result = self.result(cid)
                if result != '':
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def post_url(self, url, fields, files=[]):
        for key in files:
            files[key] = open(files[key], 'rb')
        res = requests.post(url, files=files, data=fields)
        return res.text
def code_verificate(name, passwd, file_name, app_id=3625, app_key='3990a3735d1d3fe0868a3dfc985d9f23',
                    code_type=1005, time_out=60):
    """
    :param name: 云打码注册用户名，这是普通用户注册，而非开发者用户注册名
    :param passwd: 用户密码
    :param file_name: 需要识别的图片名
    :param app_id: 软件ID，这里默认是填的我的，如果需要，可以自行注册一个开发者账号，填自己的。
    软件开发者会有少额提成，希望大家支持weibospider的发展（提成的20%会给celery项目以支持其发展）
    :param app_key: 软件key，这里默认是填的我的，如果需要，可以自行注册一个开发者账号，填自己的
    :param code_type: 1005表示五位字符验证码。价格和验证码类别，详细请看http://www.yundama.com/price.html
    :param time_out: 超时时间
    :return: 验证码结果
    """
    yundama_obj = YDMHttp(name, passwd, app_id, app_key)
    cur_uid = yundama_obj.login()
    print('uid: %s' % cur_uid)
    rest = yundama_obj.balance()
    print('balance: %s' % rest)

    # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
    cid, result = yundama_obj.decode(file_name, code_type, time_out)
    print('cid: %s, result: %s' % (cid, result))
    return result

def login(username, password):
    # su 是加密后的用户名
    su = get_su(username)
    sever_data = get_server_data(su)
    servertime = sever_data["servertime"]
    nonce = sever_data['nonce']
    rsakv = sever_data["rsakv"]
    pubkey = sever_data["pubkey"]
    password_secret = get_password(password, servertime, nonce, pubkey)

    postdata = {
        'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'useticket': '1',
        'pagerefer': "http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl",
        'vsnf': '1',
        'su': su,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'rsakv': rsakv,
        'sp': password_secret,
        'sr': '1366*768',
        'encoding': 'UTF-8',
        'prelt': '115',
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
        }

    need_pin = sever_data['showpin']
    if need_pin == 1:
        # 你也可以改为手动填写验证码
        if not yundama_username:
            raise Exception('由于本次登录需要验证码，请配置顶部位置云打码的用户名{}和及相关密码'.format(yundama_username))
        pcid = sever_data['pcid']
        postdata['pcid'] = pcid
        img_url = get_pincode_url(pcid)
        get_img(img_url)
        verify_code = code_verificate(yundama_username, yundama_password, verify_code_path)
        print(verify_code)
        postdata['door'] = verify_code

    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
    login_page = session.post(login_url, data=postdata, headers=headers)
    login_loop = (login_page.content.decode("GBK"))
    pa = r'location\.replace\([\'"](.*?)[\'"]\)'
    loop_url = re.findall(pa, login_loop)[0]
    login_index = session.get(loop_url, headers=headers)
    uuid = login_index.text
    print('登陆成功' + uuid)

def get_mac_address():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])
if __name__ == '__main__':

    account = input("账号: ")
    password = input("密码: ")
    payload = {'account': account, 'password': password, 'device_code': get_mac_address()}
    r = requests.post('http://59.110.160.234:5000/spider/api/v1/users/login', data=payload)
    if 'error' in eval(r.text):
        print(eval(r.text)['error'])
    else:
        index = 0
        spider_times = 0
        account = getAccount(0)
        login(account['account'], account['password'])
        while True:
            print('Loop')
            if spider_times != 0 and spider_times % config.switch_account_interval == 0:
                index = index + 1
                if index >= len(config.weibo_accounts):
                    index = 0
                account = getAccount(index)
                try:
                    login(account['account'], account['password'])
                except Exception as e:
                    print(e.args)
            t = threading.Thread(target=perfirm, args=(
            config.spider_user_ids, config.spider_keywords, config.spider_extra_keywords, config.spider_interval, config.private_message))
            t.start()
            spider_times = spider_times + 1
            time.sleep(180)

