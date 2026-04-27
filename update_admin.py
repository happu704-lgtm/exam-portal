"""Update admin credentials in existing database."""
from database import execute_db
from werkzeug.security import generate_password_hash

# Update admin username and password
execute_db(
    'UPDATE users SET username = ?, password_hash = ?, full_name = ?, email = ? WHERE role = "admin"',
    ['tulasi', generate_password_hash('tulasi@2005'), 'Tulsi', 'admin@digitalquiz.com']
)
print("Admin credentials updated successfully!")
print("Username: tulasi")
print("Password: tulasi@2005")
