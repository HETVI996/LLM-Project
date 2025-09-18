import os
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
from models import db, User, Response # We now import from models.py

load_dotenv()

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
# Configure the secret key and the database URI
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-strong-secret-key-you-should-change')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questionnaire.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with our app
db.init_app(app)

# A command to create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    """The homepage now redirects to the login page."""
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

@app.route('/questionnaire')
def questionnaire():
    """Serves the main questionnaire page."""
    if 'user_details' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """Processes the questionnaire and saves all data to the database."""
    if 'user_details' not in session:
        return redirect(url_for('login'))

    user_details = session.pop('user_details', {})
    
    # Create a new user record
    new_user = User(
        name=user_details.get('name'),
        age=user_details.get('age'),
        gender=user_details.get('gender')
    )
    db.session.add(new_user)
    db.session.commit() # Save the user to get their ID
    
    # Loop through all questions and save each response
    for i in range(1, 24):
        question = f"Question {i}"
        answer = ""
        if i == 9: 
            keys = ['mathematics', 'any_language', 'creativity', 'management']
            ratings = {key: request.form.get(f'q9_{key}', '0') for key in keys}
            answer = f"Math: {ratings['mathematics']}/10, Language: {ratings['any_language']}/10, Creativity: {ratings['creativity']}/10, Management: {ratings['management']}/10"
        else:
            answer = request.form.get(f'q{i}_answer')
        
        if answer:
            # Create a new response record linked to the user
            new_response = Response(question=question, answer=answer, user_id=new_user.id)
            db.session.add(new_response)

    db.session.commit() # Save all the responses
    
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)