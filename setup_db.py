from server.database import db, Post, SubscriptionState, Subscriber

def create_tables():
    try:
        # Create tables if they don't exist
        db.create_tables([Post, SubscriptionState, Subscriber], safe=True)
        print("Database check complete - tables exist or were created")
    except Exception as e:
        print(f"Error checking/creating tables: {e}")

if __name__ == "__main__":
    create_tables()