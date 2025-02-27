from db import update, query_values
from datetime import datetime, timedelta

from .course import get_course_status

def get_person(app, user_id):
    sql = """
        SELECT 
            u.id, u.email, u.name, u.phone, u.date_start, u.date_leave,
            r.role_id, r.role_name, 
            c.id, c.name, 
            t.date_attended, t.date_expires
        FROM users u
        LEFT JOIN users_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.role_id
        LEFT JOIN roles_courses rc ON r.role_id = rc.role_id
        LEFT JOIN courses c ON rc.course_id = c.id
        LEFT JOIN training t ON u.id = t.user_id AND c.id = t.course_id
        WHERE u.id = %s
    """
    
    data = query_values(app, sql, (user_id,))
    
    if not data:
        return None  # Handle missing users gracefully

    # User Info
    user_data = data[0]  
    result = {
        "id": user_data[0],
        "email": user_data[1],
        "name": user_data[2],
        "phone": user_data[3],
        "date_start": user_data[4],
        "date_leave": user_data[5],
        "roles": {}
    }

    for row in data:
        role_id = row[6]
        if role_id:
            if role_id not in result["roles"]:
                result["roles"][role_id] = {
                    "id": role_id,
                    "name": row[7],
                    "courses": []
                }
            result["roles"][role_id]["courses"].append({
                "id": row[8],
                "name": row[9],
                "status": get_course_status(row[11]),
                "date_attended": row[10],
                "date_expires": row[11],
            })

    result["roles"] = list(result["roles"].values())
    
    return result


def get_person_roles(app, user_id):
    result = []
    sql = """
        SELECT roles.*
        FROM roles
        JOIN users_roles ON roles.role_id = users_roles.role_id
        WHERE users_roles.user_id = %s
    """
    roles = query_values(app, sql, (user_id,))
    for role in roles:
        result.append({
            "id": role[0],
            "name": role[1],
            "courses": get_role_courses(app, role[0], user_id)
        })
    return result

def get_role_courses(app, role_id, user_id):
    result = []
    sql = """
        SELECT courses.*
        FROM courses
        JOIN roles_courses ON courses.id = roles_courses.course_id
        WHERE roles_courses.role_id = %s
    """
    courses = query_values(app, sql, (role_id,))
    for course in courses:
        training = get_course_training(app, user_id, course[0])
        result.append({
            "id": course[0],
            "name": course[1],
            "status": training["status"],
            "date_attended": training["date_attended"],
            "date_expires": training["date_expires"],
        })
    return result

def get_course_training(app, user_id, course_id):
    training = query_values(app, 'SELECT * FROM training WHERE user_id = %s AND course_id = %s', (user_id, course_id))[0]
    result = {
        "status": get_course_status(training[4]),
        "date_attended": training[3],
        "date_expires": training[4],
    }
    return result

# def get_course_status(date_expires):
#     today = datetime.today().date()
    
#     if date_expires > today:
#         if date_expires <= today + timedelta(days=180):  # 6 months = 180 days
#             return "warning"
#         return "success"
    
#     return "danger"

# def get_person_role(app, user_id, role_id):
#     # Get required courses
#     role_courses = query_values(app, 'SELECT * FROM roles_courses WHERE role_id = %s', (role_id[0],))
#     # return info on them
#     print()


# def get_person_status(id):
#     pass

# def get_person_roles(app, id):
#     role_data = []
#     user_roles = query_values(app, 'SELECT role_id FROM users_roles WHERE user_id = %s', (id,))

#     for role_id in user_roles:

#         qualified = True

#         role_info = query_values(app, 'SELECT * FROM roles WHERE role_id = %s', (role_id[0],))[0]
#         required_course_ids = query_values(app, 'SELECT * FROM roles_courses WHERE role_id = %s', (role_id[0],))

#         required_course_data = []

#         for required_course in required_course_ids:
#             course_id = required_course[2]
#             course_data = query_values(app, 'SELECT * FROM courses WHERE id = %s', (course_id,))[0]

#             training_data = query_values(app, course_id, id)

#             if training_data == []:
#                 qualified = False
#                 required_course_data.append({
#                     "course_id": course_data[0],
#                     "course_status": False,
#                     "course_name": course_data[1],
#                     "course_desc": course_data[2],
#                     "date_attended": None,
#                     "date_expires": None,
#                     "passed": None,
#                 })
#             else:  
#                 required_course_data.append({
#                     "course_id": course_data[0],
#                     "course_status": get_course_status(training_data),
#                     "course_name": course_data[1],
#                     "course_desc": course_data[2],
#                     "date_attended": training_data[0][4],
#                     "date_expires": training_data[0][5],
#                     "passed": training_data[0][6],
#                 })

#         role_data.append({
#                 "role_id": role_id,
#                 "qualified": qualified,
#                 "role_name": role_info[1],
#                 "course_info": required_course_data,
#             })
        
#     return role_data


def set_person_details(app, request):
    date_start = (datetime.strptime(request.form.get('date_start'), '%Y-%m-%d').strftime('%Y-%m-%d') if request.form.get('date_start') else None)
    date_leave = (datetime.strptime(request.form.get('date_leave'), '%Y-%m-%d').strftime('%Y-%m-%d') if request.form.get('date_leave') else None)

    user_id = request.form['user_id']

    sql = """
    UPDATE users
    SET email = %s, name = %s, phone = %s, date_start = %s, date_leave = %s
    WHERE id = %s
    """

    values = (
        request.form.get('email'),
        request.form.get('name'),
        request.form.get('phone'),
        date_start,
        date_leave,
        user_id,
    )

    update(app, sql, values)