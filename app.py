import os
import time
from flask import Flask, redirect, url_for, flash, session, render_template, request, jsonify
from flask_login import current_user
from flask_cors import CORS
from database import init_db, query_db, execute_db
from auth import auth_bp, login_manager
from student import student_bp
from admin import admin_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'exam-portal-secret-key-2026')
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True

# Production domain configuration
APP_URL = os.environ.get('APP_URL', '')  # e.g., https://myapp.com
FRONTEND_URL = "https://exam-portal-7r8m.onrender.com"

# Enable CORS for frontend communication
CORS(app, supports_credentials=True)
# Initialize login manager
login_manager.init_app(app)

# Register blueprints with API prefix
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(student_bp, url_prefix='/api/student')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

# Initialize database
with app.app_context():
    init_db()


@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))


def get_external_url(endpoint):
    """Get full external URL for an endpoint, using APP_URL if configured."""
    if APP_URL:
        return f"{APP_URL}{url_for(endpoint)}"
    # Fallback to request-based URL
    return url_for(endpoint, _external=True)


# Route to handle shared link - accessible without login
@app.route('/join/<token>')
def join_with_token(token):
    """Handle shareable link access. Validates token and redirects to login."""
    print(f'[JOIN LINK] Accessing with token: {token[:20]}...')

    try:
        # Check if token exists and is valid
        link = query_db('SELECT * FROM share_links WHERE token = ? AND is_active = 1', [token], one=True)

        if not link:
            print(f'[JOIN LINK] ERROR: Token not found or inactive')
            return render_template('link_error.html', login_url=get_external_url('auth.login'))

        print(f'[JOIN LINK] Found link: id={link["id"]}, created_by={link["created_by"]}')

        # Check expiration
        current_time = int(time.time())
        if link['expires_at'] < current_time:
            print(f'[JOIN LINK] ERROR: Link expired (expires_at={link["expires_at"]}, now={current_time})')
            execute_db('UPDATE share_links SET is_active = 0 WHERE id = ?', [link['id']])
            return render_template('link_error.html', login_url=get_external_url('auth.login'))

        # Increment usage count
        execute_db('UPDATE share_links SET usage_count = COALESCE(usage_count, 0) + 1 WHERE id = ?', [link['id']])

        # Store token in session to track referral
        session['share_token'] = token
        session['referred_by'] = link['created_by']
        session.permanent = True

        print(f'[JOIN LINK] Session set: share_token={token[:20]}..., referred_by={link["created_by"]}')

        # If user is already logged in, redirect to dashboard
        if current_user.is_authenticated:
            print(f'[JOIN LINK] User already authenticated: {current_user.username}')
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.dashboard'))

        # Redirect to login page for new users
        print(f'[JOIN LINK] Redirecting to login page')
        flash('Welcome! Please login or register to access the exam portal.', 'success')
        return redirect(get_external_url('auth.login'))

    except Exception as e:
        print(f'[JOIN LINK] ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return render_template('link_error.html', login_url=get_external_url('auth.login'))


@app.template_filter('format_time')
def format_time(seconds):
    """Convert seconds to human readable format."""
    if not seconds:
        return 'N/A'
    minutes = seconds // 60
    secs = seconds % 60
    if minutes > 0:
        return f'{minutes}m {secs}s'
    return f'{secs}s'


@app.template_filter('grade_color')
def grade_color(percentage):
    """Return a CSS class based on percentage."""
    if not percentage:
        return 'grade-na'
    if percentage >= 80:
        return 'grade-excellent'
    elif percentage >= 60:
        return 'grade-good'
    elif percentage >= 40:
        return 'grade-pass'
    return 'grade-fail'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
