from flask import Blueprint, request, jsonify
from datetime import datetime
from config import Config
from database import db
from models.job import Job
from models.application import Application
from models.user import User
import jwt

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/applications', methods=['POST'])
def create_application():
    """Apply for a job"""
    # Accept multipart/form-data
    if not request.form:
        return jsonify({'message': 'Missing form data'}), 400
    
    # Get user from token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_email = data.get('email')
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid token'}), 401
        
    job_id = request.form.get('job_id')
    applicant_name = request.form.get('name') or request.form.get('applicant_name')
    applicant_email = request.form.get('email') or request.form.get('applicant_email')
    
    if not job_id or not applicant_name or not applicant_email:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        job_id = int(job_id)
    except ValueError:
        return jsonify({'error': 'Invalid job ID'}), 400
        
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    resume_file = request.files.get('resume')
    resume_path = ''
    if resume_file:
        import os
        from werkzeug.utils import secure_filename
        # ensure uploads dir exists
        os.makedirs('uploads', exist_ok=True)
        filename = secure_filename(resume_file.filename)
        resume_path = os.path.join('uploads', f"app_{filename}")
        resume_file.save(resume_path)
    
    # Create application
    application = Application(
        job_id=job_id,
        user_id=user.id,
        applicant_name=applicant_name,
        applicant_email=applicant_email,
        resume_path=resume_path,
        cover_letter=request.form.get('cover_letter', ''),
        status='pending'
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify(application.to_dict()), 201

@applications_bp.route('/applications/job/<int:job_id>', methods=['GET'])
def get_job_applications(job_id):
    """Get all applications for a job"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    applications = Application.query.filter_by(job_id=job_id).all()
    return jsonify([app.to_dict() for app in applications]), 200

@applications_bp.route('/applications/candidate', methods=['GET'])
def get_candidate_applications():
    """Get applications for the current candidate"""
    # Get token from header
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_email = data.get('email')
        
        # Filter applications by email
        applications = Application.query.filter_by(applicant_email=user_email).all()
        return jsonify([app.to_dict() for app in applications]), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@applications_bp.route('/applications/<int:app_id>', methods=['GET'])
def get_application(app_id):
    """Get a specific application"""
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    return jsonify(application.to_dict()), 200

@applications_bp.route('/applications/<int:app_id>', methods=['PUT'])
def update_application(app_id):
    """Update application status"""
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    
    data = request.get_json()
    application.status = data.get('status', application.status)
    application.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(application.to_dict()), 200

@applications_bp.route('/applications/resume/<path:filename>', methods=['GET'])
def download_resume(filename):
    """Download a resume file"""
    import os
    from flask import send_file
    
    # Path is relative to the backend directory where 'uploads' is created
    file_path = filename
    if not os.path.exists(file_path):
        return jsonify({'message': 'File not found'}), 404
        
    return send_file(file_path, as_attachment=True)

