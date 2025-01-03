from flask import Flask, redirect, render_template, url_for, request, flash
import flask_login
from db import db_query, db_query_values, db_update
import config
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from scripts import send_welcome_email
from datetime import datetime


app = Flask(__name__)
app.config.from_object(config)

app.secret_key = app.config.get('SECRET_KEY')


if os.getenv('FLASK_ENV') == 'development':
    app.config['DEBUG'] = True

class User(flask_login.UserMixin):
    def __init__(self, user_data):
        self.id = user_data[0]            # id
        self.email = user_data[1]         # email
        self.password = user_data[2]      # password
        self.name = user_data[3]          # name
        self.phone = user_data[4]         # last_name
        self.date_start = user_data[5]    # date_start
        self.date_leave = user_data[6]    # date_leave

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
                flash("You don't have the required role to access this page.")
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

@app.route('/')
@flask_login.login_required
def index():
    return redirect(url_for('training_register'))

@app.route('/training_register')
@flask_login.login_required
def training_register():
    return render_template('training_register.html', 
                           user=flask_login.current_user,
                           training_log = db_query(app, 'SELECT * FROM training_log'),
                           users = db_query(app, 'SELECT * FROM users'),
                           training_courses = db_query(app, 'SELECT * FROM training_courses'))

@app.route('/roles', methods=['GET', 'POST'])
@flask_login.login_required
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

@app.route('/course_register', methods=['GET', 'POST'])
@flask_login.login_required
def course_register():

    if request.method == 'GET':
        return render_template('course_register.html', 
                               user=flask_login.current_user, 
                               course_providers=db_query(app, 'SELECT * FROM course_providers'),
                               course_register = db_query(app, 'SELECT * FROM training_courses'))
    
    is_mandatory = 1 if request.form['is_mandatory'] == 'on' else 0

    sql = """
    INSERT INTO training_courses (`name`, `description`, `duration`, `is_mandatory`, `course_provider_id`)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        request.form['name'],
        request.form['description'],
        request.form['duration'],
        is_mandatory,
        request.form['course_provider_id'],
    )

    db_update(app, sql, values)
    return redirect(url_for('course_register'))

@app.route('/course-providers', methods=['GET', 'POST'])
@flask_login.login_required
def course_providers():
    course_providers = db_query(app, 'SELECT * FROM course_providers')

    if request.method == 'GET':
        return render_template('course_providers.html', user=flask_login.current_user, course_providers=course_providers)

    sql = """
    INSERT INTO course_providers (`name`, `phone_number`)
    VALUES (%s, %s)
    """
    values = (
        request.form['name'],
        request.form['phone'],
    )

    db_update(app, sql, values)
    return redirect(url_for('course_providers'))


@app.route('/settings', methods=['GET', 'POST'])
@flask_login.login_required
def settings():
    users = db_query(app, 'SELECT * FROM users')

    if request.method == 'GET':
        return render_template('settings.html', user=flask_login.current_user, users=users)
    
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
        datetime.strptime(request.form['date_start'], '%d/%m/%Y').strftime('%Y-%m-%d'),
    )

    db_update(app, sql, values)

    return redirect(url_for('settings'))

@app.route('/user-settings', methods=['GET', 'POST'])
@flask_login.login_required
def user_settings():
    user_id = None

    if request.method == 'POST':
        date_start = (
        datetime.strptime(request.form.get('date_start'), '%Y-%m-%d').strftime('%Y-%m-%d') if request.form.get('date_start') else None
        )
        date_leave = (
            datetime.strptime(request.form.get('date_leave'), '%Y-%m-%d').strftime('%Y-%m-%d') if request.form.get('date_leave') else None
        )

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
            request.form['user_id'],
        )

        db_update(app, sql, values)

        return redirect(url_for('settings'))
    
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        user_info = db_query_values(app, 'SELECT * FROM users WHERE id = %s', (user_id,))
        user_roles = db_query_values(app, 'SELECT * FROM user_roles WHERE user_id = %s', (user_id,))

        return render_template(
            'user_settings.html',
            user=flask_login.current_user,
            user_id=user_id,
            user_info=user_info,
            roles=db_query(app, 'SELECT * FROM roles'),
            user_roles = user_roles
        )

    return redirect(url_for('user_settings'))




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
        flash("User logged in successfully!")
        return redirect(url_for('training_register'))

    error = "Invalid email or password."
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()
