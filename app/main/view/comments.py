import os
from flask import Blueprint, render_template, session, request, jsonify
from app.main.view import check_session
from app.main.view.CommentsModel import Comment
from app.main.view.FansModel import Fans

blueprint = Blueprint('comments', __name__,
                    template_folder='templates',
                    static_folder='static')
@blueprint.route('/comments',methods=['GET'])
@check_session
def query_comments():
    comments = Comment.objects()
    comments_list = []

    response_data = {}
    for comment in comments:
        comments_json = {}
        comments_json['host_id'] = comment.host_id
        comments_json['host_nickname'] = comment.host_nickname
        comments_json['weibo_content'] = comment.weibo_content
        comments_json['weibo_link'] = comment.weibo_link
        comments_json['comment_user'] = comment.comment_user
        comments_json['comment_content'] = comment.comment_content
        comments_json['comment_time'] = comment.comment_time
        comments_json['create_at'] = comment.create_at
        comments_list.append(comments_json)
    response_data['draw'] = 1
    response_data['data'] = comments_list
    return jsonify(response_data)