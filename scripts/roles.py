from db import db_query, db_update

def add_role(app, request):

    sql = """
    INSERT INTO roles (`role_name`)
    VALUES (%s)
    """

    values = (
        request.form['name'],
    )

    db_update(app, sql, values)

def get_roles(app):
    role_data = []
    roles = db_query(app, 'SELECT * FROM roles')
    courses_required = db_query(app, 'SELECT * FROM roles_courses')
    users_required = db_query(app, 'SELECT * FROM users_roles')

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


