import os
from peewee import *
from datetime import datetime

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

# Create PostgreSQL database instance
db = PostgresqlDatabase(None)

# Parse the DATABASE_URL and connect
if DATABASE_URL:
    from urllib.parse import urlparse
    url = urlparse(DATABASE_URL)
    db.init(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )


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
    indexed_at = peewee.DateTimeField(default=datetime.utcnow)


class SubscriptionState(BaseModel):
    service = peewee.CharField(unique=True)
    cursor = peewee.BigIntegerField()


if db.is_closed():
    db.connect()
    db.create_tables([Post, SubscriptionState, Subscriber])
