from mongoengine import Document, StringField, IntField


class Fans(Document):
    host_id = StringField(required=True)
    host_nickname = StringField(required=True)
    fans_id = StringField(required=True)
    nickname = StringField(required=True)
    gender = StringField(required=True)
    create_at = IntField(required=True)