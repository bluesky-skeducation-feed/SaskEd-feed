from server.database import db, Post, SubscriptionState

def create_tables():
    try:
        db.connect()
        # Only create tables if they don't exist
        db.create_tables([Post, SubscriptionState], safe=True)
        print("Database check complete - tables exist or were created")
        db.close()
    except Exception as e:
        print(f"Error checking/creating tables: {e}")

if __name__ == "__main__":
    create_tables()