from db import query_values
from datetime import datetime, timedelta

def get_course(app, course_id):
    return query_values(app, 'SELECT * FROM courses WHERE id = %s', (course_id,))

def get_course_status(date_expires, expires):
    today = datetime.today().date()

    if expires == "0":
        return "success"
    
    if not date_expires:
        return "danger"
    
    if date_expires > today:
        if date_expires <= today + timedelta(days=180):  
            return "warning"
        return "success"
    
    return "danger"