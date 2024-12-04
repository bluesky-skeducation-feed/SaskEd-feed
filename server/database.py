from datetime import datetime, timezone
import os
from peewee import *

# Debug prints
print("Starting database initialization...")
DATABASE_URL = os.getenv('DATABASE_URL')
print(f"DATABASE_URL found: {'Yes' if DATABASE_URL else 'No'}")

# Initialize database using direct connection string
if DATABASE_URL:
    print("Found DATABASE_URL, initializing PostgreSQL...")
    try:
        # Replace postgres:// with postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            
        db = PostgresqlDatabase(None)
        db.init(DATABASE_URL)
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

class Subscriber(BaseModel):
    did = CharField(unique=True)
    subscribed_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

class Post(BaseModel):
    uri = CharField(index=True)
    cid = CharField()
    reply_parent = CharField(null=True, default=None)
    reply_root = CharField(null=True, default=None)
    indexed_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

class SubscriptionState(BaseModel):
    service = CharField(unique=True)
    cursor = BigIntegerField()