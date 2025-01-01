from flask import Flask, redirect, render_template, url_for, request, flash
import flask_login
from db import db_query_values, db_update
import config
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from scripts import send_welcome_email
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(config)
mail = Mail(app)

if os.getenv('FLASK_ENV') == 'development':
    app.config['DEBUG'] = True

class User(flask_login.UserMixin):
    def __init__(self, user_data):
        self.id = user_data[0]            # id
        self.email = user_data[1]         # email
        self.password = user_data[2]      # password
        self.first_name = user_data[3]    # first_name
        self.last_name = user_data[4]     # last_name
        self.user_role = user_data[6]     # user_role

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

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
def index():
    return render_template('index.html', user=flask_login.current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    sql = """
    INSERT INTO users (`email`, `password`, `first_name`, `last_name`)
    VALUES (%s, %s, %s, %s)
    """
    values = (
        request.form['email'],
        generate_password_hash(request.form['password']),
        request.form['first_name'],
        request.form['last_name'],
    )

    db_update(app, sql, values)
    send_welcome_email(app, mail, request.form['email'], request.form['first_name'])
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
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()
