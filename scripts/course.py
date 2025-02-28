from db import query_values
from datetime import datetime, timedelta

def get_course(app, course_id):
    sql = """
        SELECT 
            c.id AS course_id, 
            c.name AS course_name, 
            c.expires, 
            c.renewal, 
            c.method, 
            c.provider, 
            c.cost,
            r.role_id, 
            r.role_name AS role_name,
            u.id AS user_id, 
            u.name AS user_name, 
            t.date_attended, 
            t.date_expires
        FROM courses c
        LEFT JOIN roles_courses rc ON c.id = rc.course_id
        LEFT JOIN roles r ON rc.role_id = r.role_id
        LEFT JOIN users_roles ur ON r.role_id = ur.role_id
        LEFT JOIN users u ON ur.user_id = u.id
        LEFT JOIN training t ON u.id = t.user_id AND t.course_id = c.id
        WHERE c.id = %s
    """

    data = query_values(app, sql, (course_id,))

    if not data:
        return None

    # Course Info
    course_data = data[0]
    result = {
        "id": course_data[0],
        "name": course_data[1],
        "expires": course_data[2],
        "renewal": course_data[3],
        "method": course_data[4],
        "provider": course_data[5],
        "cost": course_data[6],
        "roles": {},  # Keep roles here, but without personnel
        "personnel": [],  # Personnel is now a flat list
        "status": "success"  # Default to success, will update later
    }

    seen_personnel = set()  # To avoid duplicates
    status_levels = set()  # Track statuses of personnel

    # Process rows
    for row in data:
        role_id = row[7]
        if role_id:
            if role_id not in result["roles"]:
                result["roles"][role_id] = {
                    "id": role_id,
                    "name": row[8]
                }

        # Extract user details
        user_id = row[9]
        if user_id and user_id not in seen_personnel:
            seen_personnel.add(user_id)
            status = get_course_status(row[12], result["expires"]) if row[12] else "danger"
            status_levels.add(status)  # Collect status for later evaluation
            
            result["personnel"].append({
                "id": user_id,
                "name": row[10],
                "status": status,
                "date_attended": row[11] if row[11] else "Missing",
                "date_expires": row[12] if row[12] else "Missing",
            })

    # Determine course status based on personnel statuses
    if "danger" in status_levels:
        result["status"] = "danger"
    elif "warning" in status_levels:
        result["status"] = "warning"
    else:
        result["status"] = "success"

    # Convert roles dictionary to list
    result["roles"] = list(result["roles"].values())

    return result


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