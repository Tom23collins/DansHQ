from db import db_update
from datetime import datetime

def get_person_status(id):
    pass

def add_person():
    pass

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

    db_update(app, sql, values)