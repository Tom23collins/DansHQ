from flask import Flask, redirect, render_template, url_for, request, flash
import flask_login
from db import db_query, db_query_values, db_update
import config
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from scripts import *
from datetime import datetime

# TODO Orange status/ expiring soon

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
    user_data = db_query_values(app, 'SELECT * FROM users WHERE id = %s', (user_id,))
    if not user_data:
        return None
    return User(user_data[0])

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']

    user_data = db_query_values(app, 'SELECT * FROM users WHERE email = %s', (email,))

    if user_data and check_password_hash(user_data[0][2], password):
        user = User(user_data[0])
        flask_login.login_user(user)
        return redirect(url_for('index'))

    error = "Invalid email or password."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

@app.route('/')
@flask_login.login_required
def index():
    return redirect(url_for('training_profile', user_id=flask_login.current_user.id))

@app.route('/training-profile', methods=['GET', 'POST'])
@flask_login.login_required
def training_profile():
    if request.method == 'POST':

        update_user_details(app, request)
        update_user_roles(app, request)
    
        return redirect(url_for('training_profile', 
                                user_id = request.form['user_id']
                                ))
    
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        user_info = db_query_values(app, 'SELECT * FROM users WHERE id = %s', (user_id,))
        user_training = db_query_values(app, 'SELECT * FROM training_log WHERE user_id = %s', (user_id,))
        user_roles = db_query_values(app, 'SELECT role_id FROM user_roles WHERE user_id = %s', (user_id,))
        all_roles = db_query(app, 'SELECT * FROM roles')

        return render_template(
            'training_profile.html',   
            user=flask_login.current_user,
            user_id=user_id,
            user_info = user_info,
            user_roles = user_roles,
            roles = all_roles,
            user_training=user_training,
            result_data=get_role_data_for_user(app, user_id)
        )

    return redirect(url_for('training_profile', user_id=user_id))

@app.route('/training-register', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('office_staff')
def training_register():
    if request.method == 'GET':

        training_data = get_training_data(app)

        return render_template('training_register.html', 
                                user=flask_login.current_user,
                                training_data = training_data,
                                users = db_query(app, 'SELECT * FROM users'),
                                training_courses = db_query(app, 'SELECT * FROM training_courses'))
    
    passed = 1 if request.form['passed'] == 'on' else 0
    
    sql = """
    INSERT INTO training_log (`user_id`, `training_id`, `date_attended`, `date_expires`, `passed`)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        request.form['user_id'],
        request.form['training_id'],
        request.form['date_attended'],
        request.form['date_expires'],
        passed,
    )

    db_update(app, sql, values)

    return redirect(url_for('training_register'))

@app.route('/roles', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('office_staff')
def roles():

    if request.method == 'GET':
        return render_template('roles.html', 
                               user=flask_login.current_user, 
                               roles = db_query(app, 'SELECT * FROM roles'))
    

    sql = """
    INSERT INTO roles (`role_name`, `role_description`)
    VALUES (%s, %s)
    """
    values = (
        request.form['name'],
        request.form['description'],
    )

    db_update(app, sql, values)

    return redirect(url_for('roles'))

@app.route('/role-settings', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('office_staff')
def role_settings():

    if request.method == 'POST':

        role_id = request.form['role_id']

        sql = """
        UPDATE roles
        SET role_name = %s, role_description = %s
        WHERE role_id = %s
        """

        values = (
            request.form.get('name'),
            request.form.get('description'),
            request.form['role_id'],
        )

        db_update(app, sql, values)

        #  Update required courses

        training_courses_ids = db_query(app, sql = "SELECT id FROM training_courses")

        sql = """
        DELETE FROM role_requirements
        WHERE role_id = %s
        """

        values = [role_id]

        db_update(app, sql, values)

        for training_course in training_courses_ids:
            training_course_id = training_course[0]
            training_course_mandatory = request.form.get(f'is_mandatory_{training_course_id}')
            
            if training_course_mandatory != None:
                sql = """
                INSERT INTO role_requirements (`role_id`, `training_course_id`)
                VALUES (%s, %s)
                """
                values = (
                    role_id,
                    training_course_id,
                )

                db_update(app, sql, values)

        return redirect(url_for('role_settings', role_id = request.form['role_id']))
    
    if request.method == 'GET':
        role_id = request.args.get('role_id')
        role_info = db_query_values(app, 'SELECT * FROM roles WHERE role_id = %s', (role_id,))
        courses = db_query(app, 'SELECT * FROM training_courses')
        role_requirements = db_query_values(app, 'SELECT * FROM role_requirements WHERE role_id = %s', (role_id,))

        return render_template(
            'role_settings.html',
            user=flask_login.current_user,
            role_id=role_id,
            role_info=role_info,
            courses=courses,
            role_requirements=role_requirements
        )

    return redirect(url_for('role_settings'))

@app.route('/training-courses', methods=['GET', 'POST'])
@flask_login.login_required
@role_required('office_staff')
def training_courses():

    if request.method == 'GET':
        return render_template('training_courses.html', 
                               user=flask_login.current_user, 
                               course_register = db_query(app, 'SELECT * FROM training_courses'))

    sql = """
    INSERT INTO training_courses (`name`, `description`)
    VALUES (%s, %s)
    """
    values = (
        request.form['name'],
        request.form['description'],
    )

    db_update(app, sql, values)
    return redirect(url_for('training_courses'))


@app.route('/users', methods=['GET', 'POST'])
@role_required('office_staff')
@flask_login.login_required
def users():
    users = db_query(app, 'SELECT * FROM users')

    if request.method == 'GET':
        return render_template('users.html', user=flask_login.current_user, users=users)
    
    # Add user to database

    sql = """
    INSERT INTO users (`email`, `password`, `name`, `phone`, `date_start`)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        request.form['email'],
        generate_password_hash(request.form['password']),
        request.form['name'],
        request.form['phone'],
        datetime.strptime(request.form['date_start'], '%Y-%m-%d').strftime('%Y-%m-%d'),
    )

    db_update(app, sql, values)

    return redirect(url_for('users'))

@app.route('/admin-settings', methods=['GET', 'POST'])
@role_required('administrator')
@flask_login.login_required
def admin_settings():
    users = db_query(app, 'SELECT * FROM users')

    if request.method == 'GET':
        return render_template('admin_settings.html', user=flask_login.current_user, users=users)
    
    # Edit user settings

    sql = """
        UPDATE users
        SET user_role = %s
        WHERE id = %s
        """
    values = (
        request.form['role'],
        request.form['user_id'],
    )

    db_update(app, sql, values)

    return redirect(url_for('admin_settings'))

if __name__ == "__main__":
    app.run()
