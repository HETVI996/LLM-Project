import pandas as pd
from sqlalchemy import select
from app import app, db, User, Response

def create_dataset():
    """
    Connects to the database and pulls all user and response data 
    into a structured Pandas DataFrame.
    """
    with app.app_context():
        # The correct, modern way to query all users
        result = db.session.execute(select(User))
        users = result.scalars().all()
        
        # If there are no users, return an empty DataFrame right away
        if not users:
            return pd.DataFrame()
            
        all_data = []
        
        # Loop through each user to process their data
        for user in users:
            user_data = {
                'user_id': user.id,
                'name': user.name,
                'age': user.age,
                'gender': user.gender
            }
            
            # Pivot the responses so each question is a column
            for response in user.responses:
                user_data[response.question] = response.answer
            
            all_data.append(user_data)
            
        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(all_data)
        
        return df

if __name__ == '__main__':
    # Generate the DataFrame
    dataset = create_dataset()
    
    # --- THIS IS THE NEW, SMARTER CHECK ---
    # Check if the DataFrame is empty
    if dataset.empty:
        print("⚠️  Warning: The database is empty.")
        print("Please run the Flask app and submit at least one questionnaire.")
    else:
        # Save the prepared data to a CSV file for analysis
        dataset.to_csv('training_dataset.csv', index=False)
        
        print("✅ Successfully created dataset!")
        print("💾 Saved to training_dataset.csv")
        print("\nFirst 5 rows of the dataset:")
        print(dataset.head())