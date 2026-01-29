from mongoengine import Document, StringField, IntField, DateTimeField

class pastes(Document):
    paste_id = StringField(required=True)
    content = StringField(required=True)
    created_at = DateTimeField(required=True)
    expires_at = DateTimeField()
    max_views = IntField()
    views = IntField(default=0) 

    meta = {
        "auto_create_index": False,
        "collection": "pastes"
    }