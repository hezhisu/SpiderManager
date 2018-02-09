import os
from flask import Blueprint, render_template, session, request, jsonify
from app.main.view import check_session
from app.main.view.FansModel import Fans

blueprint = Blueprint('fans', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/fans',methods=['GET'])
@check_session
def query_fans():
    fans = Fans.objects()
    fans_list = []

    response_data = {}
    for fan in fans:
        fans_json = {}
        fans_json['host_id'] = fan.host_id
        fans_json['host_nickname'] = fan.host_nickname
        fans_json['fans_id'] = fan.fans_id
        fans_json['nickname'] = fan.nickname
        fans_json['gender'] = fan.gender
        fans_json['create_at'] = fan.create_at
        fans_list.append(fans_json)
    response_data['draw'] = 1
    response_data['data'] = fans_list
    return jsonify(response_data)