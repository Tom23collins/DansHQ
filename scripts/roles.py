from db import query, query_values, update

from .person import get_person_roles
from .role import get_role_courses

def add_role(app, request):

    sql = """
    INSERT INTO roles (`role_name`)
    VALUES (%s)
    """

    values = (
        request.form['name'],
    )

    update(app, sql, values)

def get_roles_user(app, user_id):
    roles = []
    person_roles = get_person_roles(app, user_id)

    for role in person_roles:
        courses = get_role_courses(app, role_id)

        for course in courses:
            get_course(app, course_id)
            course_data = query_values(app, 'SELECT * FROM courses WHERE id = %s', (course_id,))[0]

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
                    "date_attended": training_data[0][3],
                    "date_expires": training_data[0][4],
                })

        role_data.append({
                "role_id": role_id,
                "qualified": qualified,
                "role_name": role_info[1],
                "course_info": required_course_data,
            })
        
    return role_data

def get_roles(app):
    role_data = []
    roles = query(app, 'SELECT * FROM roles')
    courses_required = query(app, 'SELECT * FROM roles_courses')
    users_required = query(app, 'SELECT * FROM users_roles')

    role_courses_count = {}
    for req in courses_required:
        role_id = req[1]
        role_courses_count[role_id] = role_courses_count.get(role_id, 0) + 1

    role_users_count = {}
    for user_role in users_required:
        role_id = user_role[2]
        role_users_count[role_id] = role_users_count.get(role_id, 0) + 1

    for role in roles:
        role_id = role[0]
        role_data.append({
            "status": "active" if role_id in role_users_count else "inactive",
            "id": role_id,
            "name": role[1].strip(),
            "courses": role_courses_count.get(role_id, 0),
            "personnel": role_users_count.get(role_id, 0)
        })

    return role_data


