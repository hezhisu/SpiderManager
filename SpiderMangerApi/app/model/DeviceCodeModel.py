from mongoengine import Document, StringField


class DeviceCode(Document):
    code = StringField(required=True)
    bind_user = StringField(required=False,default='')