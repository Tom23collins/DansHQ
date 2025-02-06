from db import db_update, db_query
from datetime import datetime

def update_user_roles(app, request):
    user_id = request.form['user_id']
    role_ids = db_query(app, sql = "SELECT role_id FROM roles")

    sql = """
    DELETE FROM user_roles
    WHERE user_id = %s
    """

    values = [user_id]

    db_update(app, sql, values)

    for role in role_ids:
        role_id = role[0]
        role_assigned = request.form.get(f'is_mandatory_{role_id}')
        if role_assigned != None:
            sql = """
            INSERT INTO user_roles (`user_id`, `role_id`)
            VALUES (%s, %s)
            """
            values = (
                user_id,
                role_id,
            )

            db_update(app, sql, values)