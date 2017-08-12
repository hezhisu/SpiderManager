from mongoengine import Document, BooleanField, IntField, StringField


class Users(Document):
    is_manager = BooleanField(required=True,default=False)
    create_at = IntField(required=True)
    latest_login_time = IntField(required=False)
    account = StringField(required=True)
    password = StringField(required=True)
    phone = StringField(required=False)
    email = StringField(required=False)
    device_code = StringField(required=False)
    task_id = StringField(required=False)