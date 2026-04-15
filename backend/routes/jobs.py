from flask import Blueprint, request, jsonify
from datetime import datetime
from database import db
from models.job import Job
from models.application import Application

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs', methods=['GET'])
def get_jobs():
    status = request.args.get('status', 'active')
    now = datetime.utcnow()
    
    if status == 'active':
        jobs_list = Job.query.filter_by(is_active=True).filter(
            (Job.deadline.is_(None)) | (Job.deadline > now)
        ).all()
    else:  # 'all'
        jobs_list = Job.query.all()
    
    return jsonify({'jobs': [job.to_dict() for job in jobs_list]}), 200

@jobs_bp.route('/jobs/recruiter', methods=['GET'])
def get_recruiter_jobs():
    """Get jobs posted by the logged-in recruiter"""
    jobs_list = Job.query.all()
    
    job_data_list = []
    for job in jobs_list:
        job_data = job.to_dict()
        # Count applicants for this job
        applicant_count = Application.query.filter_by(job_id=job.id).count()
        job_data['applicant_count'] = applicant_count
        job_data['status'] = 'active' if job.is_active else 'closed'
        job_data['job_title'] = job.title
        job_data['company_name'] = job.company
        job_data_list.append(job_data)
    
    return jsonify({'jobs': job_data_list}), 200

@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    return jsonify(job.to_dict()), 200

@jobs_bp.route('/jobs', methods=['POST'])
def create_job():
    data = request.get_json()
    
    if not data or not data.get('job_title') or not data.get('company_name') or not data.get('job_description'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    deadline = None
    if data.get('deadline'):
        try:
            deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00'))
        except:
            pass
    
    job = Job(
        title=data.get('job_title', ''),
        company=data.get('company_name', ''),
        description=data.get('job_description', ''),
        requirements=data.get('required_skills', ''),
        location=data.get('location', ''),
        salary_range=data.get('salary_range', ''),
        job_type=data.get('job_type', 'full-time'),
        experience_required=data.get('experience_required', ''),
        number_of_openings=data.get('number_of_openings', 1),
        is_active=True,
        domain=data.get('domain', ''),
        deadline=deadline
    )

    try:
        db.session.add(job)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create job', 'error': str(e)}), 500
    
    return jsonify(job.to_dict()), 201

@jobs_bp.route('/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    data = request.get_json()
    job.title = data.get('title', job.title)
    job.company = data.get('company', job.company)
    job.description = data.get('description', job.description)
    job.requirements = data.get('requirements', job.requirements)
    job.location = data.get('location', job.location)
    job.salary_range = data.get('salary_range', job.salary_range)
    job.job_type = data.get('job_type', job.job_type)
    job.experience_required = data.get('experience_required', job.experience_required)
    job.number_of_openings = data.get('number_of_openings', job.number_of_openings)
    job.is_active = data.get('is_active', job.is_active)
    job.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(job.to_dict()), 200

@jobs_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job deleted successfully'}), 200

@jobs_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
def apply_to_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    data = request.get_json()
    
    if not data or not data.get('applicant_name') or not data.get('applicant_email'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    application = Application(
        job_id=job_id,
        user_id=data.get('user_id'),
        applicant_name=data['applicant_name'],
        applicant_email=data['applicant_email'],
        resume_path=data.get('resume_path', ''),
        cover_letter=data.get('cover_letter', ''),
        status='pending'
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify(application.to_dict()), 201

@jobs_bp.route('/jobs/<int:job_id>/applications', methods=['GET'])
def get_job_applications(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    applications = Application.query.filter_by(job_id=job_id).all()
    return jsonify([app.to_dict() for app in applications]), 200

@jobs_bp.route('/applications/<int:app_id>', methods=['GET'])
def get_application(app_id):
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    return jsonify(application.to_dict()), 200

@jobs_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
def update_application_status(app_id):
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    
    data = request.get_json()
    application.status = data.get('status', application.status)
    application.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(application.to_dict()), 200
