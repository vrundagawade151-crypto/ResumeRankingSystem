import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_ENV_PATH = os.path.join(BASE_DIR, '..', '.env')
BACKEND_ENV_PATH = os.path.join(BASE_DIR, '.env')

# Prefer the repo-level .env for shared configuration, then fill in any
# missing backend-only values from backend/.env.
load_dotenv(ROOT_ENV_PATH)
load_dotenv(BACKEND_ENV_PATH)


def _normalize_database_url(database_url):
    """Use a Python 3.14-friendly Postgres driver when a Postgres URL is provided."""
    if database_url.startswith('postgresql://') and '+psycopg' not in database_url:
        return database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return database_url


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DATABASE_URL = _normalize_database_url(
        os.getenv('DATABASE_URL', 'sqlite:///expense_tracker.db')
    )
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
