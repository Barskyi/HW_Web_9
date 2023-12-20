from mongoengine import connect, Document, StringField, ListField
from mystery_password import PASSWORD, NAME
import certifi

connect(db="HW_Web_9",
        host=f"mongodb+srv://{NAME}:{PASSWORD}@barskyidb.hgjpvmn.mongodb.net/?retryWrites=true&w=majority",
        tlsCAFile=certifi.where())


class Quote(Document):
    author = StringField(required=True)
    quote = StringField()
    tags = ListField(StringField())
    meta = {"collection": "Quote"}


class Author(Document):
    fullname = StringField()
    born_date = StringField()
    born_location = StringField()
    description = StringField()
    meta = {"collection": "Author"}

