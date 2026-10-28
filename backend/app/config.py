import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'aicte-apaar-sec-key-7f9e8a1b2c3d4e5f60718293a4b5c6d7')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'aicte-apaar-jwt-sec-9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

    # Privacy and Cryptographic Keys
    APAAR_HMAC_SECRET = os.environ.get('APAAR_HMAC_SECRET', 'aicte-hmac-salt-apaar-2026-strict-key')
    # 32-byte url-safe base64 key for cryptography.fernet
    APAAR_ENCRYPTION_KEY = os.environ.get('APAAR_ENCRYPTION_KEY', 'J7mZ8pQwK3rL1sXvY9uNtF2gH4dE6jA8bC0eG2iK4mU=')

    # Database
    db_url = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(basedir, 'aicte_apaar.db')}")
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_UPLOAD_ROWS = 50000

    # System Configuration Defaults
    CURRENT_ACADEMIC_YEAR = '2025-2026'
    ACADEMIC_YEARS = ['2023-2024', '2024-2025', '2025-2026', '2026-2027']
    ENROLMENT_STATUSES = ['Active', 'Completed', 'Dropped Out', 'Suspended', 'Transferred']
    ADMISSION_CATEGORIES = ['General', 'OBC', 'SC', 'ST', 'EWS', 'Management', 'NRI']

    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
