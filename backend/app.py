from flask import Flask, jsonify
from flask_cors import CORS
import os

from config import Config
from database import db, init_db
from models.user import User
from models.job import Job
from models.application import Application
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.applications import applications_bp
from routes.recruiter import recruiter_bp
from routes.admin import admin_bp
from routes.ai_screening import ai_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    init_db(app)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(jobs_bp, url_prefix='/api')
    app.register_blueprint(applications_bp, url_prefix='/api')
    app.register_blueprint(recruiter_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Expense Tracker API is running',
            'version': '1.0.0'
        }), 200
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
