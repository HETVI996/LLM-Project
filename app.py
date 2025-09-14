import os
import json
from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
# A secret key is required to use sessions for the login
app.config['SECRET_KEY'] = 'a-strong-secret-key-you-should-change'

def save_prompt_for_training(full_data_string):
    """Saves the complete data (user info + answers) in JSONL format."""
    try:
        system_prompt = "You are Path, an expert career coach. A user has provided their details and answered a detailed questionnaire. Analyze their complete set of answers and provide a detailed career analysis."
        training_data = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_data_string}
            ]
        }
        with open("path_training_prompts.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(training_data) + "\n")
        print("✅ Prompt data saved to path_training_prompts.jsonl")
    except Exception as e:
        print(f"❌ Error saving training data: {e}")

@app.route('/')
def home():
    """The homepage now redirects to the login page."""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Save user details into a session cookie
        session['user_details'] = {
            "name": request.form.get('name'),
            "age": request.form.get('age'),
            "gender": request.form.get('gender')
        }
        # Redirect to the main questionnaire
        return redirect(url_for('questionnaire'))
    return render_template('login.html')

@app.route('/questionnaire')
def questionnaire():
    """Serves the main questionnaire page."""
    # If a user tries to go here directly, send them back to login
    if 'user_details' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """Processes the questionnaire and saves all data to a file."""
    if 'user_details' not in session:
        return redirect(url_for('login'))

    # Retrieve user details from the session
    user_details = session.pop('user_details', {})
    
    # Start building the final data string with user details
    user_data_parts = [
        f"Name: {user_details.get('name')}",
        f"Age: {user_details.get('age')}",
        f"Gender: {user_details.get('gender')}"
    ]
    
    # Loop for the original 23 questions from the form
    for i in range(1, 24):
        if i == 9: 
            keys = ['mathematics', 'any_language', 'creativity', 'management']
            ratings = {key: request.form.get(f'q9_{key}', '0') for key in keys}
            answer = f"Math: {ratings['mathematics']}/10, Language: {ratings['any_language']}/10, Creativity: {ratings['creativity']}/10, Management: {ratings['management']}/10"
        else:
            answer = request.form.get(f'q{i}_answer')
        
        if answer:
            user_data_parts.append(f"Question {i}: {answer}")

    final_data_string = "\n".join(user_data_parts)
    
    save_prompt_for_training(final_data_string)
    
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

