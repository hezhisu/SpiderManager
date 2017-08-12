from mongoengine import EmbeddedDocument, StringField


class WeiboAccounts(EmbeddedDocument):
    account = StringField(required=True)
    password = StringField(required=True)