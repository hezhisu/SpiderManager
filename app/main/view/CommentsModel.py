from mongoengine import StringField, Document, IntField


class Comment(Document):
    host_id = StringField(required=True)
    host_nickname = StringField(required=True)
    weibo_content = StringField(required=True)
    weibo_link = StringField(required=True)
    comment_user = StringField(required=True)
    comment_content = StringField(required=True)
    comment_time = StringField(required=True)
    create_at = IntField(required=True)