from db import update, query

from .course import get_course

def get_courses(app):
    courses = query(app, 'SELECT * FROM courses')

    result = []

    for course in courses:
        data = get_course(app, course[0])
        result.append(data)

    return result

    for row in courses:
        result.append({
                "id": row[0],
                "name": row[1],
                "expires": row[2],
                "renewal": row[3],
                "method": row[4],
                "provider": row[5],
                "cost": row[6],
            })
        
    return result

def set_course(app, request):
    sql = """
    INSERT INTO courses (`name`, `expires`, `renewal`, `method`, `provider`, `cost`)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    timeUnit = request.form['timeUnit']
    if request.form['renewal'] == "1":
        timeUnit = timeUnit[:-3]

    cost = None if request.form['cost'] == "" else float(request.form['cost'])

    values = (
        request.form['name'],
        request.form.get('expires', '0'),
        f"{request.form['renewal']} {timeUnit}",
        request.form['method'],
        request.form['provider'],
        cost,
    )

    update(app, sql, values)