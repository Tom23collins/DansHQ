from db import query, update
from datetime import datetime
from flask import Response
from werkzeug.security import generate_password_hash

from .person import get_person

def get_personnel(app):
    users = query(app, 'SELECT * FROM users')
    result = []

    for user in users:
        data = get_person(app, user[0])
        result.append(data)

    return result

def set_personnel(app, request):
    sql = """
    INSERT INTO users (`email`, `password`, `name`, `phone`, `date_start`, `date_leave`)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    password = generate_password_hash(request.form['password'])

    values = (
        request.form['email'],
        password,
        request.form['name'],
        request.form['phone'],
        request.form['date_start'],
        request.form['date_start'],
    )

    update(app, sql, values)

# def download_training_data(app):
#     training_data = get_personnel(app)
    
#     def generate():
#         yield 'User ID,User Name,Role ID,Role Name,Qualified,Course ID,Course Name,Course Description,Date Attended,Date Expires,Passed\n'  # CSV header
#         for user in training_data:
#             user_id = user['user_id']
#             user_name = user['user_name']
#             for role in user['training_data']:
#                 role_id = role['role_id'][0]
#                 role_name = role['role_name']
#                 qualified = role['qualified']
#                 for course in role['course_info']:
#                     course_id = course['course_id']
#                     course_name = course['course_name']
#                     course_desc = course['course_desc']
#                     date_attended = course['date_attended'] if course['date_attended'] else 'N/A'
#                     date_expires = course['date_expires'] if course['date_expires'] else 'N/A'
#                     passed = course['passed'] if course['passed'] is not None else 'N/A'
#                     yield f"{user_id},{user_name},{role_id},{role_name},{qualified},{course_id},{course_name},{course_desc},{date_attended},{date_expires},{passed}\n"
    
#     response = Response(generate(), mimetype='text/csv')
#     response.headers.set("Content-Disposition", "attachment", filename="training_data.csv")
#     return response