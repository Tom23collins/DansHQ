from db import update, query_values
from datetime import datetime, timedelta

from .course import get_course_status

def worst_status(statuses):
    if "danger" in statuses:
        return "danger"
    if "warning" in statuses:
        return "warning"
    return "success"

def get_person(app, user_id):
    sql = """
        SELECT 
            u.id, 
            u.email, 
            u.name, 
            u.phone, 
            u.date_start, 
            u.date_leave,
            r.role_id, 
            r.role_name, 
            c.id, 
            c.name, 
            c.expires,
            t.date_attended, 
            t.date_expires
        FROM users u
        LEFT JOIN users_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.role_id
        LEFT JOIN roles_courses rc ON r.role_id = rc.role_id
        LEFT JOIN courses c ON rc.course_id = c.id
        LEFT JOIN training t ON u.id = t.user_id AND c.id = t.course_id
        WHERE u.id = %s
    """
    
    data = query_values(app, sql, (user_id,))
    
    if not data:
        return None

    # User Info
    user_data = data[0]
    result = {
        "id": user_data[0],
        "email": user_data[1],
        "name": user_data[2],
        "phone": user_data[3],
        "date_start": user_data[4],
        "date_leave": user_data[5],
        "status": "danger",
        "roles": {}
    }

    # Build role->courses structure
    for row in data:
        role_id = row[6]
        if role_id:
            if role_id not in result["roles"]:
                result["roles"][role_id] = {
                    "id": role_id,
                    "name": row[7],
                    "status": "danger",
                    "courses": []
                }
            
            course_status = get_course_status(row[12], row[10])
            result["roles"][role_id]["courses"].append({
                "id": row[8],
                "name": row[9],
                "expires": row[10],
                "status": course_status,
                "date_attended": row[11],
                "date_expires": row[12],
            })

    for role_id, role_info in result["roles"].items():
        course_statuses = [course["status"] for course in role_info["courses"]]
        role_info["status"] = worst_status(course_statuses)
    
    all_role_statuses = [role_info["status"] for role_info in result["roles"].values()]
    user_status = worst_status(all_role_statuses)
    result["status"] = user_status

    result["roles"] = list(result["roles"].values())
    
    return result


def set_person(app, request):
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

    update(app, sql, values)