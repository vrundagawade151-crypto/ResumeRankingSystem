from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, inspect

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


def _migrate_jobs_table():
    """Ensure jobs table has all required columns for current model."""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('jobs')]
    except Exception:
        return

    alter_statements = []
    if 'location' not in columns:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN location VARCHAR(200);")
    if 'salary_range' not in columns:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN salary_range VARCHAR(100);")
    if 'job_type' not in columns:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN job_type VARCHAR(50);")
    if 'experience_required' not in columns:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN experience_required VARCHAR(200);")
    if 'number_of_openings' not in columns:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN number_of_openings INTEGER DEFAULT 1;")
    if 'is_active' not in columns:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")
    if 'domain' not in columns:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN domain VARCHAR(200);")
    if 'deadline' not in columns:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN deadline TIMESTAMP;")

    for stmt in alter_statements:
        try:
            db.session.execute(text(stmt))
        except Exception:
            pass
    db.session.commit()


def _migrate_applications_table():
    """Ensure applications table has all required columns for current model."""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('applications')]
    except Exception:
        return

    alter_statements = []
    if 'linkedin_id' not in columns:
        alter_statements.append("ALTER TABLE applications ADD COLUMN linkedin_id VARCHAR(200);")
    if 'github_id' not in columns:
        alter_statements.append("ALTER TABLE applications ADD COLUMN github_id VARCHAR(200);")
    if 'certification_path' not in columns:
        alter_statements.append("ALTER TABLE applications ADD COLUMN certification_path VARCHAR(500);")
    if 'domain' not in columns:
        alter_statements.append("ALTER TABLE applications ADD COLUMN domain VARCHAR(200);")
    if 'name_mismatch' not in columns:
        alter_statements.append("ALTER TABLE applications ADD COLUMN name_mismatch BOOLEAN DEFAULT FALSE;")
    if 'name_mismatch_reason' not in columns:
        alter_statements.append("ALTER TABLE applications ADD COLUMN name_mismatch_reason TEXT;")
    if 'extracted_certifications' not in columns:
        alter_statements.append("ALTER TABLE applications ADD COLUMN extracted_certifications TEXT;")
    if 'experience_years' not in columns:
        alter_statements.append("ALTER TABLE applications ADD COLUMN experience_years INTEGER;")

    for stmt in alter_statements:
        try:
            db.session.execute(text(stmt))
        except Exception:
            pass
    db.session.commit()


def _migrate_users_table():
    """Ensure users table has all required columns for current model."""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
    except Exception:
        return

    if 'domain' not in columns:
        try:
            db.session.execute(text("ALTER TABLE users ADD COLUMN domain VARCHAR(200);"))
            db.session.commit()
        except Exception:
            pass


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _migrate_jobs_table()
        _migrate_applications_table()
        _migrate_users_table()
