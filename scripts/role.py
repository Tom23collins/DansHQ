from db import update, query, query_values

from .course import get_course
from .person import get_person

def get_role(app, role_id):
    data = query_values(app, 'SELECT * FROM roles WHERE role_id = %s', (role_id,))[0]

    courses = []
    personnel = []

    course_ids = query_values(app, 'SELECT course_id FROM roles_courses WHERE role_id = %s', (role_id,))[0]
    user_ids = query_values(app, 'SELECT user_id FROM users_roles WHERE role_id = %s', (role_id,))[0]

    for course_id in course_ids:
        courses.append(get_course(app, course_id))

    for user_id in user_ids:
        personnel.append(get_person(app, user_id))

    result = {
        "id": data[0],
        "name": data[1],
        "courses": courses,
        "personnel": personnel
    }
        
    return result

def set_role(app, request):
    role_id = request.form['role_id']

    sql = """
    UPDATE roles
    SET role_name = %s
    WHERE role_id = %s
    """

    values = (
        request.form['role_name'],
        request.form['role_id'],
    )

    update(app, sql, values)

    training_courses_ids = query(app, sql = "SELECT id FROM courses")

    sql = """
    DELETE FROM roles_courses
    WHERE role_id = %s
    """

    values = [role_id]

    update(app, sql, values)

    for training_course in training_courses_ids:
        training_course_id = training_course[0]
        training_course_mandatory = request.form.get(f'is_mandatory_{training_course_id}')
        
        if training_course_mandatory != None:
            sql = """
            INSERT INTO roles_courses (`role_id`, `course_id`)
            VALUES (%s, %s)
            """
            values = (
                role_id,
                training_course_id,
            )

            update(app, sql, values)