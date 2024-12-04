import os
import peewee
from datetime import datetime
from urllib.parse import urlparse

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
db = None


# Parse the DATABASE_URL and connect
if DATABASE_URL:
    url = urlparse(DATABASE_URL)
    db.init(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
else:
    db = peewee.SqliteDatabase('feed_database.db')


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Subscriber(BaseModel):
    did = peewee.CharField(unique=True)  # The user's DID
    subscribed_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db


class Post(BaseModel):
    uri = peewee.CharField(index=True)
    cid = peewee.CharField()
    reply_parent = peewee.CharField(null=True, default=None)
    reply_root = peewee.CharField(null=True, default=None)
    indexed_at = peewee.DateTimeField(default=datetime.timezone.utc)


class SubscriptionState(BaseModel):
    service = peewee.CharField(unique=True)
    cursor = peewee.BigIntegerField()
