"""Flask application configuration."""
import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'resume-screening-secret-key-2024')
    
    # MySQL configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'resume_screening_db')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    USE_SQLITE = os.environ.get('USE_SQLITE', '').lower() in ('1', 'true', 'yes')

    if USE_SQLITE:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
    
    # CORS - Allow React frontend
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # JWT configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-resume-2024')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # OTP configuration (simulation - 6 digit, expires in 10 minutes)
    OTP_EXPIRY_MINUTES = 10
    OTP_LENGTH = 6
