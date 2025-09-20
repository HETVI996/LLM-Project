import os
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import io
import csv

# ----------------- LOAD ENV -----------------
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY', 'mysecret123')
CSV_DOWNLOAD_PASSWORD = os.environ.get('CSV_DOWNLOAD_PASSWORD', 'mysecret123')

# ----------------- FLASK APP -----------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)

# ----------------- MODELS -----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    responses = db.relationship('Answer', backref='user', lazy=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    answer = db.Column(db.String(500))

# ----------------- ROUTES -----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    answers = [request.form.get(f'q{i}') for i in range(1, 24)]

    user = User(name=name, age=age, gender=gender)
    db.session.add(user)
    db.session.commit()

    for ans in answers:
        answer = Answer(user_id=user.id, answer=ans)
        db.session.add(answer)
    db.session.commit()

    return render_template('thank_you.html')

# ----------------- ADMIN CSV DOWNLOAD -----------------
@app.route('/admin/download_csv')
def download_csv():
    password = request.args.get('password')
    if password != CSV_DOWNLOAD_PASSWORD:
        return "Unauthorized: wrong password", 401

    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV header
    header = ["User ID", "Name", "Age", "Gender"] + [f"Q{i}" for i in range(1, 24)]
    writer.writerow(header)

    users = User.query.all()
    for user in users:
        row = [user.id, user.name, user.age, user.gender]
        answers = [a.answer for a in user.responses]
        while len(answers) < 23:
            answers.append("")
        row.extend(answers)
        writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name="responses.csv")

# ----------------- ADMIN PANEL -----------------
@app.route('/admin')
def admin_panel():
    users = User.query.all()
    return render_template('admin.html', users=users)

# ----------------- RUN APP -----------------
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
