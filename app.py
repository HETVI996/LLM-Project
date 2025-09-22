import os
from flask import Flask, render_template, request, session, redirect, url_for, Response
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from io import StringIO
import csv

# -------------------- LOAD ENV VARIABLES --------------------
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')

# -------------------- APP CONFIG --------------------
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-strong-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://pathuser:SIH123@localhost:5432/pathdb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db = SQLAlchemy(app)

# -------------------- DATABASE MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    responses = db.relationship('Answer', backref='user', lazy=True)

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# -------------------- CREATE TABLES --------------------
with app.app_context():
    db.create_all()

# -------------------- ROUTES --------------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user_details'] = {
            "name": request.form.get('name'),
            "age": request.form.get('age'),
            "gender": request.form.get('gender')
        }
        return redirect(url_for('questionnaire'))
    return render_template('login.html')

@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    if 'user_details' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if 'user_details' not in session:
        return redirect(url_for('login'))

    user_details = session.pop('user_details', {})

    new_user = User(
        name=user_details.get('name'),
        age=int(user_details.get('age', 0)),
        gender=user_details.get('gender')
    )
    db.session.add(new_user)
    db.session.commit()  # commit to generate new_user.id

    for i in range(1, 24):
        question = f"Question {i}"

        if i == 9:
            keys = ['mathematics', 'any_language', 'creativity', 'management']
            ratings = {key: request.form.get(f'q9_{key}', '0') for key in keys}
            answer = (
                f"Math: {ratings['mathematics']}/10, "
                f"Language: {ratings['any_language']}/10, "
                f"Creativity: {ratings['creativity']}/10, "
                f"Management: {ratings['management']}/10"
            )
        else:
            answer = request.form.get(f'q{i}_answer', '')

        if answer.strip():
            response = Answer(question=question, answer=answer, user_id=new_user.id)
            db.session.add(response)

    db.session.commit()
    return render_template('thank_you.html')

# -------------------- ADMIN LOGIN --------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    admin_key = os.environ.get('ADMIN_KEY', 'supersecret123')
    if request.method == 'POST':
        password = request.form.get('password')
        if password == admin_key:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Incorrect password"
    return render_template('admin_login.html', error=error)

# -------------------- ADMIN DASHBOARD --------------------
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    users = User.query.all()
    for user in users:
        user.responses = Answer.query.filter_by(user_id=user.id).order_by(Answer.id).all()
    return render_template('admin.html', users=users)

# -------------------- CSV DOWNLOAD --------------------
@app.route("/download_csv")
def download_csv():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    output = StringIO()
    writer = csv.writer(output)
    header = ["User ID", "Name", "Age", "Gender"] + [f"Q{i}" for i in range(1, 24)]
    writer.writerow(header)

    users = User.query.all()
    for user in users:
        row = [user.id, user.name, user.age, user.gender]
        responses = Answer.query.filter_by(user_id=user.id).order_by(Answer.id).all()
        answers = [r.answer for r in responses]
        while len(answers) < 23:
            answers.append("")
        row.extend(answers)
        writer.writerow(row)

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=responses.csv"
    return response

# -------------------- LOGOUT --------------------
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)
