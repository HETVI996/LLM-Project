import csv
from app import app
from models import User

with app.app_context():
    users = User.query.all()
    with open('responses.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['User ID', 'Name', 'Age', 'Gender'] + [f'Q{i}' for i in range(1, 24)]
        writer.writerow(header)
        
        for user in users:
            answers = ['']*23
            for r in user.responses:
                q_num = int(r.question.split(' ')[1])
                answers[q_num - 1] = r.answer
            writer.writerow([user.id, user.name, user.age, user.gender] + answers)
