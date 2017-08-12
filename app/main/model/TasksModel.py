from mongoengine import Document, ListField, EmbeddedDocumentField, StringField, IntField

from app.main.model.WeiboAccountsModel import WeiboAccounts


class Tasks(Document):
    weibo_accounts = ListField(EmbeddedDocumentField(WeiboAccounts,required=True),required=False)
    spider_user_ids = ListField(StringField(),required=True)
    spider_keywords = ListField(StringField(),required=True)
    spider_extra_keywords = ListField(StringField(), required=True)
    mail_list = ListField(StringField(), required=True)
    spider_interval =IntField(required=True)
    switch_account_interval = IntField(required=True)
    belong_user_id = StringField(required=True)