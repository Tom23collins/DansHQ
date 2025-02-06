from db import db_query
from datetime import datetime
from .user_role_data import get_role_data_for_user

def get_training_data(app):
    training_data = []
    users = db_query(app, 'SELECT * FROM users')

    for user in users:
        user_training_data = get_role_data_for_user(app, user[0])

        training_data.append({
                "user_id": user[0],
                "user_name": user[3],
                "training_data": user_training_data,
            })
        
    return training_data