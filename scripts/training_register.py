from db import db_query
from datetime import datetime
from .user_role_data import get_role_data_for_user, get_course_status
from flask import Response

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

def download_training_data(app):
    training_data = get_training_data(app)
    
    def generate():
        yield 'User ID,User Name,Role ID,Role Name,Qualified,Course ID,Course Name,Course Description,Date Attended,Date Expires,Passed\n'  # CSV header
        for user in training_data:
            user_id = user['user_id']
            user_name = user['user_name']
            for role in user['training_data']:
                role_id = role['role_id'][0]
                role_name = role['role_name']
                qualified = role['qualified']
                for course in role['course_info']:
                    course_id = course['course_id']
                    course_name = course['course_name']
                    course_desc = course['course_desc']
                    date_attended = course['date_attended'] if course['date_attended'] else 'N/A'
                    date_expires = course['date_expires'] if course['date_expires'] else 'N/A'
                    passed = course['passed'] if course['passed'] is not None else 'N/A'
                    yield f"{user_id},{user_name},{role_id},{role_name},{qualified},{course_id},{course_name},{course_desc},{date_attended},{date_expires},{passed}\n"
    
    response = Response(generate(), mimetype='text/csv')
    response.headers.set("Content-Disposition", "attachment", filename="training_data.csv")
    return response

def get_fully_qualified(app):
    training_data = []
    users = db_query(app, 'SELECT * FROM users')

    for user in users:
        user_training_data = get_role_data_for_user(app, user[0])

        # Determine if the user is qualified for all roles
        qualified_for_all_roles = all(role['qualified'] for role in user_training_data)

        # Determine the status based on qualification and expiration
        expiring_soon = any(
            get_course_status([(
                None, None, None, None, None, 
                course['date_expires'], course['passed']
            )]) == "Expiring Soon"
            for role in user_training_data for course in role['course_info']
        )

        if not qualified_for_all_roles:
            status = "danger"
        elif expiring_soon:
            status = "warning"
        else:
            status = "success"

        # Concatenate role names
        roles = ' + '.join(role['role_name'] for role in user_training_data)

        training_data.append({
            "status": status,
            "id": user[0],
            "name": user[3],
            "roles": roles,
            "actions": len(user_training_data)  # Number of roles
        })

    return training_data