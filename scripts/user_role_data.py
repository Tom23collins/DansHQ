from db import query_values
from datetime import datetime, timedelta


def get_training_data(app, course_id, user_id):

    sql = """
        SELECT * FROM training
        WHERE user_id = %s AND training_id = %s
        """

    values = (
        user_id,
        course_id,
        )
    
    training_data = query_values(app, sql, values)

    return training_data
