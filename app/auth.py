from flask import Blueprint, render_template, request, session, redirect, url_for
from passlib.hash import sha256_crypt
from .db import execute_query

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/')
def index():
    return render_template('login.html')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_username = request.form['username']
        input_password = request.form['password']

        check_user_query = "SELECT username, password, role FROM users WHERE username = %s"
        user_data = execute_query(check_user_query, (input_username,))

        stored_username = None

        if user_data:
            stored_username, stored_password, role = user_data[0]

        if input_username == stored_username and sha256_crypt.verify(input_password, stored_password):
            print(input_username, stored_username, input_password, stored_password)
            # Store the user's role in the session
            session['role'] = role
            session['logged_in'] = True
            return redirect(url_for('main.dashboard'))

    return render_template('login.html')

@auth_routes.route('/logout')
def logout():
    session.clear()
    if 'timeout' in request.args:
        return render_template('timeout.html')
    return redirect(url_for('auth.index'))
