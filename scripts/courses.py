from db import update

def add_course(app, request):
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