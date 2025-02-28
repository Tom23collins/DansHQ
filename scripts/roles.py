from db import query, update
from collections import Counter

def get_roles(app):
    # Fetch records
    roles = query(app, 'SELECT * FROM roles')
    courses_required = query(app, 'SELECT * FROM roles_courses')
    users_required = query(app, 'SELECT * FROM users_roles')

    # Count occurrences
    role_courses_count = Counter(req[1] for req in courses_required)
    role_users_count = Counter(user_role[2] for user_role in users_required)

    # Build the response
    role_data = []
    for role_id, role_name in roles:
        role_data.append({
            "status": "active" if role_id in role_users_count else "inactive",
            "id": role_id,
            "name": role_name.strip(),
            "courses": role_courses_count.get(role_id, 0),
            "personnel": role_users_count.get(role_id, 0)
        })

    return role_data

def set_role(app, request):

    sql = """
    INSERT INTO roles (`role_name`)
    VALUES (%s)
    """

    values = (
        request.form['name'],
    )

    update(app, sql, values)