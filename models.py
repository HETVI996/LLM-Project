from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
<<<<<<< HEAD
    responses = db.relationship('Response', backref='user', lazy=True)
=======
>>>>>>> backend_postgres

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
<<<<<<< HEAD
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
=======
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
>>>>>>> backend_postgres
