from db import query_values


def get_role_courses(app, role_id):
    return query_values(app, 'SELECT * FROM roles_courses WHERE role_id = %s', (role_id,))