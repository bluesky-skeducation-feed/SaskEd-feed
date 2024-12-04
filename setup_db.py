from server.database import db, Post, SubscriptionState

def create_tables():
    with db:
        db.create_tables([Post, SubscriptionState])
        print("Tables created successfully")

if __name__ == "__main__":
    create_tables()