from db import db_query_values
from datetime import datetime, timedelta

def get_training_data(app, course_id, user_id):

    sql = """
        SELECT * FROM training
        WHERE user_id = %s AND training_id = %s
        """

    values = (
        user_id,
        course_id,
        )
    
    training_data = db_query_values(app, sql, values)

    return training_data

def get_course_status(training_data):
    date_expires = training_data[0][5]
    passed = training_data[0][6]
    
    if not passed:
        return False
    
    today = datetime.today().date()
    
    if date_expires > today:
        if date_expires <= today + timedelta(days=180):  # 6 months = 180 days
            return "Expiring Soon"
        return True
    
    return False

def get_role_data_for_user(app, user_id):
    role_data = []
    user_roles = db_query_values(app, 'SELECT role_id FROM users_roles WHERE user_id = %s', (user_id,))

    for role_id in user_roles:

        qualified = True

        role_info = db_query_values(app, 'SELECT * FROM roles WHERE role_id = %s', (role_id[0],))[0]
        required_course_ids = db_query_values(app, 'SELECT * FROM roles_courses WHERE role_id = %s', (role_id[0],))

        required_course_data = []

        for required_course in required_course_ids:
            course_id = required_course[2]
            course_data = db_query_values(app, 'SELECT * FROM courses WHERE id = %s', (course_id,))[0]

            training_data = get_training_data(app, course_id, user_id)

            if training_data == []:
                qualified = False
                required_course_data.append({
                    "course_id": course_data[0],
                    "course_status": False,
                    "course_name": course_data[1],
                    "course_desc": course_data[2],
                    "date_attended": None,
                    "date_expires": None,
                    "passed": None,
                })
            else:  
                required_course_data.append({
                    "course_id": course_data[0],
                    "course_status": get_course_status(training_data),
                    "course_name": course_data[1],
                    "course_desc": course_data[2],
                    "date_attended": training_data[0][4],
                    "date_expires": training_data[0][5],
                    "passed": training_data[0][6],
                })

        role_data.append({
                "role_id": role_id,
                "qualified": qualified,
                "role_name": role_info[1],
                "course_info": required_course_data,
            })
        
    return role_data
