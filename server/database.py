from datetime import datetime
import os
from peewee import *
from urllib.parse import urlparse

# Debug prints
print("Starting database initialization...")
print(f"Environment variables: {list(os.environ.keys())}")
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"DATABASE_URL found: {'Yes' if DATABASE_URL else 'No'}")

# Initialize database
if DATABASE_URL:
    print("Found DATABASE_URL, initializing PostgreSQL...")
    try:
        url = urlparse(DATABASE_URL)
        print(f"Parsed URL - host: {url.hostname}")
        db = PostgresqlDatabase(
            database=url.path[1:],
            user=url.username,
            password='[HIDDEN]',  # Don't log the actual password
            host=url.hostname,
            port=url.port,
            autorollback=True
        )
        print("PostgreSQL database initialized")
    except Exception as e:
        print(f"Error initializing PostgreSQL: {e}")
        raise e
else:
    print("No DATABASE_URL found, using SQLite")
    db = SqliteDatabase('feed_database.db')

class BaseModel(Model):
    class Meta:
        database = db

class Post(BaseModel):
    uri = CharField(index=True)
    cid = CharField()
    reply_parent = CharField(null=True, default=None)
    reply_root = CharField(null=True, default=None)
    indexed_at = DateTimeField(default=datetime.timezone.utc)

class SubscriptionState(BaseModel):
    service = CharField(unique=True)
    cursor = BigIntegerField()