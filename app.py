import os
from flask import Flask, render_template, request, session, redirect, url_for, Response
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from io import StringIO
import csv

# -------------------- LOAD ENV VARIABLES --------------------
# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-strong-secret-key')

# -------------------- DATABASE CONFIG --------------------
# Get the database URL from environment variables for better security
# Fallback to a default SQLite DB if not set (for local development)
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///instance/questionnaire.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db = SQLAlchemy(app)

# -------------------- DATABASE MODELS --------------------
# These models define the structure of your database tables.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    # This relationship automatically links a User to all their Answers.
    responses = db.relationship('Answer', backref='user', lazy=True, cascade="all, delete-orphan")

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


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

    # Save user
    # FIX: Handle empty age string to prevent ValueError
    age_str = user_details.get('age')
    age = int(age_str) if age_str and age_str.isdigit() else 0
    
    new_user = User(
        name=user_details.get('name'),
        age=age,
        gender=user_details.get('gender')
    )
    db.session.add(new_user)
    db.session.commit()  # commit to generate new_user.id

    # Save responses
    for i in range(1, 24):
        question = f"Question {i}"

        if i == 9:  # Special handling for Q9
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

        # Only save if there is an actual answer
        if answer and answer.strip():
            response = Answer(question=question, answer=answer, user_id=new_user.id)
            db.session.add(response)

    db.session.commit()
    return render_template('thank_you.html')

# -------------------- ADMIN DASHBOARD --------------------
@app.route('/admin')
def admin():
    # Fetch all users. The 'responses' for each user will be loaded automatically
    # by SQLAlchemy when accessed in the template thanks to the relationship.
    users = User.query.order_by(User.id).all()
    return render_template('admin.html', users=users)


# -------------------- CSV DOWNLOAD --------------------
@app.route("/download_csv")
def download_csv():
    output = StringIO()
    writer = csv.writer(output)

    # CSV Header
    header = ["User ID", "Name", "Age", "Gender"] + [f"Q{i}" for i in range(1, 24)]
    writer.writerow(header)

    # Fetch users and their responses more efficiently
    users = User.query.order_by(User.id).all()
    for user in users:
        # The 'user.responses' are loaded automatically by SQLAlchemy
        answers_dict = {r.question: r.answer for r in user.responses}
        
        row = [user.id, user.name, user.age, user.gender]
        
        # Add answers in the correct order
        for i in range(1, 24):
            question = f"Question {i}"
            row.append(answers_dict.get(question, ""))
            
        writer.writerow(row)

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=responses.csv"
    return response

# -------------------- RUN APP --------------------
if __name__ == '__main__':
    app.run(debug=True)

