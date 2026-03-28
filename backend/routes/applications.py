from flask import Blueprint, request, jsonify
from datetime import datetime
from config import Config

applications_bp = Blueprint('applications', __name__)

# Import from jobs module (shared storage)
import routes.jobs as jobs_module
import routes.auth as auth_module

@applications_bp.route('/applications', methods=['POST'])
def create_application():
    """Apply for a job"""
    data = request.get_json()
    
    if not data or not data.get('job_id') or not data.get('applicant_name') or not data.get('applicant_email'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    job_id = data['job_id']
    if job_id not in jobs_module.jobs:
        return jsonify({'message': 'Job not found'}), 404
    
    # Create application
    app_id = len(jobs_module.applications) + 1
    application = {
        'id': app_id,
        'job_id': job_id,
        'user_id': data.get('user_id'),
        'applicant_name': data['applicant_name'],
        'applicant_email': data['applicant_email'],
        'resume_path': data.get('resume_path', ''),
        'cover_letter': data.get('cover_letter', ''),
        'status': 'pending',
        'ai_score': None,
        'ai_feedback': None,
        'applied_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    jobs_module.applications[app_id] = application
    
    return jsonify(application), 201

@applications_bp.route('/applications/job/<int:job_id>', methods=['GET'])
def get_job_applications(job_id):
    """Get all applications for a job"""
    if job_id not in jobs_module.jobs:
        return jsonify({'message': 'Job not found'}), 404
    
    app_list = [app for app in jobs_module.applications.values() if app['job_id'] == job_id]
    return jsonify(app_list), 200

@applications_bp.route('/applications/candidate', methods=['GET'])
def get_candidate_applications():
    """Get applications for the current candidate"""
    # Get token from header
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        from flask import current_app
        import jwt
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_email = data.get('email')
        
        # Filter applications by email
        app_list = [app for app in jobs_module.applications.values() 
                   if app['applicant_email'] == user_email]
        return jsonify(app_list), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@applications_bp.route('/applications/<int:app_id>', methods=['GET'])
def get_application(app_id):
    """Get a specific application"""
    application = jobs_module.applications.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    return jsonify(application), 200

@applications_bp.route('/applications/<int:app_id>', methods=['PUT'])
def update_application(app_id):
    """Update application status"""
    application = jobs_module.applications.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    
    data = request.get_json()
    application['status'] = data.get('status', application['status'])
    application['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify(application), 200
