from flask import Flask, redirect, render_template, url_for, request, flash
import flask_login
import config
import os
from db import query, query_values, update
from werkzeug.security import check_password_hash
from functools import wraps
from scripts import *
from datetime import datetime

# TODO
# Calculate status of each individual person, role and course
# Add adhoc training to users
# Archived personel and roles
# Time/ cost estimates in reporting
# Individual training report
# Upload evidence
# Label data being parsed into html (training profile)

app = Flask(__name__)
app.config.from_object(config)

app.secret_key = app.config.get('SECRET_KEY')

if os.getenv('FLASK_ENV') == 'development':
    app.config['DEBUG'] = True

class User(flask_login.UserMixin):
    def __init__(self, user_data):
        self.id = user_data[0]
        self.email = user_data[1]
        self.name = user_data[3]
        self.phone = user_data[4]
        self.date_start = user_data[5]
        self.date_leave = user_data[6]
        self.user_role = user_data[7]

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                flash("You need to be logged in to access this page.")
                return redirect(url_for('login'))

            if flask_login.current_user.user_role == 'administrator':
                return f(*args, **kwargs)

            if flask_login.current_user.user_role != role:
                return redirect(url_for('index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def user_loader(user_id):
    user_data = query_values(app, 'SELECT * FROM users WHERE id = %s', (user_id,))
    if not user_data:
        return None
    return User(user_data[0])

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')

    email = request.form['email']
    password = request.form['password']

    user_data = query_values(app, 'SELECT * FROM users WHERE email = %s', (email,))

    if user_data and check_password_hash(user_data[0][2], password):
        user = User(user_data[0])
        flask_login.login_user(user)
        return redirect(url_for('index'))

    error = "Invalid email or password."
    return render_template('auth/login.html', error=error)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

@app.route('/')
@flask_login.login_required
def index():
    return redirect(url_for('person', user_id=flask_login.current_user.id))

# DansHQ

@app.route('/courses/<int:course_id>', methods=['GET', 'POST'])
@flask_login.login_required
def course(course_id):

    if request.method == 'GET':

        return render_template(
            'course.html',
            user=flask_login.current_user,
            course = get_course(app, course_id)
        )

    return redirect(url_for('course', course_id=course_id))

@app.route('/courses', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('office_staff')
def courses():

    if request.method == 'GET':
            
        return render_template('courses.html', 
                               user=flask_login.current_user, 
                               courses = get_courses(app))

    set_course(app, request)
    return redirect(url_for('courses'))

@app.route('/personnel/<int:user_id>', methods=['GET', 'POST'])
@flask_login.login_required
def person(user_id):
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_user':
            set_person(app, request)

        return redirect(url_for('person', 
                        user_id=user_id))

    if request.method == 'GET':
        return render_template(
            'person.html',
            user=flask_login.current_user,
            person=get_person(app, user_id)
        )

@app.route('/personnel', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('office_staff')
def personnel():
    if request.method == 'GET':
        return render_template('personnel.html', 
                                user=flask_login.current_user,
                                personnel = get_personnel(app)
                                )
    
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'download':
            pass

        elif action == 'set_personnel':
            set_personnel(app, request)

        return redirect(url_for('personnel'))

@app.route('/roles/<int:role_id>', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('office_staff')
def role(role_id):

    if request.method == 'GET':
        return render_template(
            'role.html',
            user=flask_login.current_user,
            role=get_role(app, role_id)
        )

    if request.method == 'POST':
        set_role(app, request)
        return redirect(url_for('role', role_id = request.form['role_id']))

@app.route('/roles', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('office_staff')
def roles():

    if request.method == 'GET':
        return render_template('roles.html', 
                               user=flask_login.current_user, 
                               roles = get_roles(app))
    

    set_role(app, request)

    return redirect(url_for('roles'))

@app.route('/settings', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('administrator')
def settings():
    users = query(app, 'SELECT * FROM users')

    if request.method == 'GET':
        return render_template('settings.html', user=flask_login.current_user, users=users)
    
    set_user_access(app, request)
    return redirect(url_for('settings'))

if __name__ == "__main__":
    app.run()