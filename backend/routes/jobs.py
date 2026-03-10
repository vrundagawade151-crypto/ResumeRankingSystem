"""Job listing and application routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.db import db
from models.job import Job
from models.application import Application
from models.recruiter import Recruiter
from models.candidate import Candidate

jobs_bp = Blueprint('jobs', __name__, url_prefix='/api/jobs')


@jobs_bp.route('', methods=['GET'])
def list_jobs():
    """List all active job posts (public - for candidate dashboard)."""
    jobs = Job.query.filter_by(status='active').order_by(Job.created_at.desc()).all()
    result = []
    for job in jobs:
        job_dict = job.to_dict()
        job_dict['applicant_count'] = job.applications.count()
        result.append(job_dict)
    return jsonify({'jobs': result}), 200


@jobs_bp.route('/recruiter', methods=['GET'])
@jwt_required()
def list_recruiter_jobs():
    """List jobs posted by current recruiter."""
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    recruiter = Recruiter.query.filter_by(user_id=int(claims.get('sub'))).first()
    if not recruiter:
        return jsonify({'error': 'Recruiter profile not found'}), 404

    jobs = Job.query.filter_by(recruiter_id=recruiter.id).order_by(Job.created_at.desc()).all()
    result = []
    for job in jobs:
        job_dict = job.to_dict()
        job_dict['applicant_count'] = job.applications.count()
        result.append(job_dict)
    return jsonify({'jobs': result}), 200


@jobs_bp.route('', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job post (recruiter only)."""
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    recruiter = Recruiter.query.filter_by(user_id=int(claims.get('sub'))).first()
    if not recruiter:
        return jsonify({'error': 'Recruiter profile not found'}), 404

    data = request.get_json()
    required = ['job_title', 'required_skills', 'job_description']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    job = Job(
        recruiter_id=recruiter.id,
        job_title=data['job_title'],
        company_name=data.get('company_name') or recruiter.company_name or 'Company',
        required_skills=data['required_skills'],
        experience_required=data.get('experience_required', ''),
        job_description=data['job_description'],
        number_of_openings=data.get('number_of_openings', 1)
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({'job': job.to_dict(), 'message': 'Job created successfully'}), 201


@jobs_bp.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get single job details."""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    job_dict = job.to_dict()
    job_dict['applicant_count'] = job.applications.count()
    return jsonify({'job': job_dict}), 200


@jobs_bp.route('/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update job (recruiter only)."""
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    recruiter = Recruiter.query.filter_by(user_id=int(claims.get('sub'))).first()
    if job.recruiter_id != recruiter.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    for key in ['job_title', 'company_name', 'required_skills', 'experience_required', 'job_description', 'number_of_openings', 'status']:
        if key in data:
            setattr(job, key, data[key])
    db.session.commit()
    return jsonify({'job': job.to_dict(), 'message': 'Job updated'}), 200


@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """Delete job (recruiter only)."""
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    recruiter = Recruiter.query.filter_by(user_id=int(claims.get('sub'))).first()
    if job.recruiter_id != recruiter.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(job)
    db.session.commit()
    return jsonify({'message': 'Job deleted'}), 200
