import os

# Security
SECRET_KEY = 'replace_with_secure_random_key'   # Change in production

# Database
DATABASE = os.path.join('instance', 'sunshine.db')

# Uploads
UPLOAD_FOLDER = os.path.join('uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

