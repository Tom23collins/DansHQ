from db import db_update

def update_user_role(app, request):
    sql = """
        UPDATE users
        SET user_role = %s
        WHERE id = %s
        """
    values = (
        request.form['role'],
        request.form['user_id'],
    )

    db_update(app, sql, values)