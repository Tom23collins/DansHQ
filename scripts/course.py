from db import query_values
from datetime import datetime, timedelta

def get_course(app, course_id):
    return query_values(app, 'SELECT * FROM courses WHERE id = %s', (course_id,))

def get_course_status(date_expires):
    today = datetime.today().date()
    
    if not date_expires:
        return "warning"
    
    if date_expires > today:
        if date_expires <= today + timedelta(days=180):  
            return "warning"
        return "success"
    
    return "danger"

def get_training(app, training_id):
    training = query_values(app, 'SELECT * FROM training WHERE id = %s', (training_id,))