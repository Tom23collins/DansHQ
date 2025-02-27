from db import update

def set_user_access(app, request):
    sql = """
        UPDATE users
        SET user_role = %s
        WHERE id = %s
        """
    values = (
        request.form['role'],
        request.form['user_id'],
    )

    update(app, sql, values)