"""Flask application entry point."""
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config import Config
from models.db import db
from models.user import User
from models.candidate import Candidate
from models.recruiter import Recruiter
from routes import auth_bp, jobs_bp, applications_bp, recruiter_bp, admin_bp, ai_screening_bp


def create_app(config_class=Config):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Create upload directory
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    CORS(app, origins=config_class.CORS_ORIGINS, supports_credentials=True)
    JWTManager(app)
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_screening_bp)

    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Resume Screening API is running'}

    with app.app_context():
        db.create_all()
        # Ensure admin user exists
        from models.user import User
        admin = User.query.filter_by(email='admin@resumescreen.com', role='admin').first()
        if not admin:
            admin = User(email='admin@resumescreen.com', password_hash='admin123', role='admin', is_verified=True)
            db.session.add(admin)
            db.session.commit()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
