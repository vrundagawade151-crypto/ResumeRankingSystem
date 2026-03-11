from flask import Blueprint, request, jsonify
from datetime import datetime

jobs_bp = Blueprint('jobs', __name__)

# In-memory storage for demo (replace with database in production)
jobs = {}
applications = {}
job_id_counter = 1
app_id_counter = 1

@jobs_bp.route('/jobs', methods=['GET'])
def get_jobs():
    status = request.args.get('status', 'active')
    job_list = []
    
    for job in jobs.values():
        job_data = dict(job)
        job_data['job_title'] = job.get('title', '')
        job_data['company_name'] = job.get('company', '')
        
        if status == 'active' and job['is_active']:
            job_list.append(job_data)
        elif status == 'all':
            job_list.append(job_data)
    
    return jsonify({'jobs': job_list}), 200

@jobs_bp.route('/jobs/recruiter', methods=['GET'])
def get_recruiter_jobs():
    """Get jobs posted by the logged-in recruiter"""
    # Add applicant count and format for frontend
    job_list = []
    for job in jobs.values():
        job_data = dict(job)
        job_data['job_title'] = job.get('title', '')
        job_data['company_name'] = job.get('company', '')
        # Count applicants for this job
        applicant_count = sum(1 for app in applications.values() if app['job_id'] == job['id'])
        job_data['applicant_count'] = applicant_count
        job_data['status'] = 'active' if job.get('is_active', True) else 'closed'
        job_list.append(job_data)
    
    return jsonify({'jobs': job_list}), 200

@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    return jsonify(job), 200

@jobs_bp.route('/jobs', methods=['POST'])
def create_job():
    global job_id_counter
    data = request.get_json()
    
    if not data or not data.get('job_title') or not data.get('company_name') or not data.get('job_description'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Convert frontend field names to backend format
    job = {
        'id': job_id_counter,
        'title': data.get('job_title', ''),
        'company': data.get('company_name', ''),
        'description': data.get('job_description', ''),
        'requirements': data.get('required_skills', ''),
        'location': data.get('location', ''),
        'salary_range': data.get('salary_range', ''),
        'job_type': data.get('job_type', 'full-time'),
        'experience_required': data.get('experience_required', ''),
        'number_of_openings': data.get('number_of_openings', 1),
        'is_active': True,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    jobs[job_id_counter] = job
    job_id_counter += 1
    
    return jsonify(job), 201

@jobs_bp.route('/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    data = request.get_json()
    job.update({
        'title': data.get('title', job['title']),
        'company': data.get('company', job['company']),
        'description': data.get('description', job['description']),
        'requirements': data.get('requirements', job['requirements']),
        'location': data.get('location', job['location']),
        'salary_range': data.get('salary_range', job['salary_range']),
        'job_type': data.get('job_type', job['job_type']),
        'is_active': data.get('is_active', job['is_active']),
        'updated_at': datetime.utcnow().isoformat()
    })
    
    return jsonify(job), 200

@jobs_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    if job_id not in jobs:
        return jsonify({'message': 'Job not found'}), 404
    
    del jobs[job_id]
    return jsonify({'message': 'Job deleted successfully'}), 200

@jobs_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
def apply_to_job(job_id):
    global app_id_counter
    
    if job_id not in jobs:
        return jsonify({'message': 'Job not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('applicant_name') or not data.get('applicant_email'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    application = {
        'id': app_id_counter,
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
    
    applications[app_id_counter] = application
    app_id_counter += 1
    
    return jsonify(application), 201

@jobs_bp.route('/jobs/<int:job_id>/applications', methods=['GET'])
def get_job_applications(job_id):
    if job_id not in jobs:
        return jsonify({'message': 'Job not found'}), 404
    
    app_list = [app for app in applications.values() if app['job_id'] == job_id]
    return jsonify(app_list), 200

@jobs_bp.route('/applications/<int:app_id>', methods=['GET'])
def get_application(app_id):
    application = applications.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    return jsonify(application), 200

@jobs_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
def update_application_status(app_id):
    application = applications.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    
    data = request.get_json()
    application['status'] = data.get('status', application['status'])
    application['updated_at'] = datetime.utcnow().isoformat()
    
    return jsonify(application), 200
