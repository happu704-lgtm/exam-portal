from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import query_db, execute_db

auth_bp = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


class User(UserMixin):
    def __init__(self, id, username, full_name, role, student_id=None, email=None):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.role = role
        self.student_id = student_id
        self.email = email

    @staticmethod
    def get(user_id):
        row = query_db('SELECT * FROM users WHERE id = ?', [user_id], one=True)
        if row:
            return User(row['id'], row['username'], row['full_name'], row['role'],
                        row['student_id'], row['email'])
        return None

    @staticmethod
    def get_by_username(username):
        row = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        return row


@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('student.dashboard'))
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'student':
            flash('Access denied.', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        selected_role = request.form.get('role', 'student')

        row = User.get_by_username(username)
        if row and check_password_hash(row['password_hash'], password):
            if row['role'] != selected_role:
                flash(f'This account is not registered as {selected_role}. Please select the correct role.', 'error')
                return render_template('login.html')

            user = User(row['id'], row['username'], row['full_name'], row['role'],
                        row['student_id'], row['email'])
            login_user(user, remember=True)
            flash(f'Welcome back, {user.full_name}!', 'success')

            next_page = request.args.get('next')
            if user.role == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            return redirect(next_page or url_for('student.dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()

        if not all([username, password, full_name]):
            flash('Please fill in all required fields.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        elif len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
        elif User.get_by_username(username):
            flash('Username already exists.', 'error')
        else:
            import random
            student_id = f"STU{random.randint(10000, 99999)}"
            execute_db(
                'INSERT INTO users (username, password_hash, full_name, role, student_id, email) VALUES (?, ?, ?, ?, ?, ?)',
                [username, generate_password_hash(password), full_name, 'student', student_id, email]
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
