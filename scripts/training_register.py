from db import db_query
from datetime import datetime
from .user_role_data import get_role_data_for_user


# def get_training_data(app, course_id, user_id):

#     sql = """
#         SELECT * FROM training_log
#         WHERE user_id = %s AND training_id = %s
#         """

#     values = (
#         user_id,
#         course_id,
#         )
    
#     training_data = db_query_values(app, sql, values)

#     return training_data

def has_user_passed_course(training_data):
    date_expires = training_data[0][5]
    passed = training_data[0][6]
    
    if passed and date_expires > datetime.today().date():  
        return True  
    
    return False

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