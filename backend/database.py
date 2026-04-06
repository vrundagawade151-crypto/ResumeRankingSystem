from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

class Base(DeclarativeBase):
    pass

# Global database instance
db = SQLAlchemy(model_class=Base)


def _migrate_jobs_table():
    """Ensure jobs table has all required columns for current model."""
    conn = db.engine.connect()
    try:
        existing_cols = {row['name'] for row in conn.execute(text("PRAGMA table_info(jobs);"))}
    except Exception:
        # Table might not exist yet
        conn.close()
        return

    alter_statements = []
    if 'location' not in existing_cols:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN location VARCHAR(200);")
    if 'salary_range' not in existing_cols:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN salary_range VARCHAR(100);")
    if 'job_type' not in existing_cols:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN job_type VARCHAR(50);")
    if 'experience_required' not in existing_cols:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN experience_required VARCHAR(200);")
    if 'number_of_openings' not in existing_cols:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN number_of_openings INTEGER DEFAULT 1;")
    if 'is_active' not in existing_cols:
        alter_statements.append("ALTER TABLE jobs ADD COLUMN is_active BOOLEAN DEFAULT 1;")

    for stmt in alter_statements:
        try:
            conn.execute(text(stmt))
        except Exception:
            pass
    conn.close()


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _migrate_jobs_table()
