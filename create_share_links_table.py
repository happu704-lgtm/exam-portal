"""Create share_links table for shareable application links."""
from database import execute_db

# Create share_links table
execute_db('''
    CREATE TABLE IF NOT EXISTS share_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at INTEGER NOT NULL,
        is_active INTEGER DEFAULT 1,
        usage_count INTEGER DEFAULT 0,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
''')

print("share_links table created successfully!")
