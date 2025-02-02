from app import app, db

def create_database():
    with app.app_context():
        db.create_all()
        print("Database and tables created successfully.")

if __name__ == '__main__':
    create_database()
