from app import app, db

with app.app_context():
    db.drop_all()    # removes old tables
    db.create_all()  # creates fresh tables

print("Database reset complete!")
