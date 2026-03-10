"""Application and resume upload routes."""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from models.db import db
from models.application import Application
from models.job import Job
from models.candidate import Candidate
from models.recruiter import Recruiter

applications_bp = Blueprint('applications', __name__, url_prefix='/api/applications')


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in {'pdf', 'docx', 'doc'}


@applications_bp.route('', methods=['POST'])
@jwt_required()
def apply_for_job():
    """Candidate applies for a job with resume upload."""
    claims = get_jwt()
    if claims.get('role') != 'candidate':
        return jsonify({'error': 'Only candidates can apply'}), 403

    candidate = Candidate.query.filter_by(user_id=claims.get('sub')).first()
    if not candidate:
        return jsonify({'error': 'Candidate profile not found'}), 404

    job_id = request.form.get('job_id') or request.get_json().get('job_id') if request.is_json else None
    if not job_id:
        return jsonify({'error': 'job_id is required'}), 400

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    # Check duplicate application
    existing = Application.query.filter_by(job_id=job_id, candidate_id=candidate.id).first()
    if existing:
        return jsonify({'error': 'Already applied for this job'}), 400

    # Get form data
    name = request.form.get('name') or candidate.name
    email = request.form.get('email') or candidate.email
    phone = request.form.get('phone') or candidate.phone or ''
    skills = request.form.get('skills') or candidate.skills or ''
    education = request.form.get('education') or candidate.education or ''
    experience = request.form.get('experience') or candidate.experience or ''

    resume_path = None
    if 'resume' in request.files:
        file = request.files['resume']
        if file and file.filename and allowed_file(file.filename):
            upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            ext = file.filename.rsplit('.', 1)[-1].lower()
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            resume_path = filename

    application = Application(
        job_id=job_id,
        candidate_id=candidate.id,
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        education=education,
        experience=experience,
        resume_path=resume_path
    )
    db.session.add(application)
    db.session.commit()
    return jsonify({'application': application.to_dict(), 'message': 'Application submitted successfully'}), 201


@applications_bp.route('/job/<int:job_id>', methods=['GET'])
@jwt_required()
def get_applicants(job_id):
    """Get applicants for a job (recruiter only)."""
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    recruiter = Recruiter.query.filter_by(user_id=claims.get('sub')).first()
    if job.recruiter_id != recruiter.id:
        return jsonify({'error': 'Unauthorized'}), 403

    applications = Application.query.filter_by(job_id=job_id).order_by(Application.created_at.desc()).all()
    result = [app.to_dict() for app in applications]
    return jsonify({'applicants': result, 'total': len(result)}), 200


@applications_bp.route('/candidate', methods=['GET'])
@jwt_required()
def get_my_applications():
    """Get current candidate's applications."""
    claims = get_jwt()
    if claims.get('role') != 'candidate':
        return jsonify({'error': 'Unauthorized'}), 403

    candidate = Candidate.query.filter_by(user_id=claims.get('sub')).first()
    if not candidate:
        return jsonify({'error': 'Candidate profile not found'}), 404

    applications = Application.query.filter_by(candidate_id=candidate.id).all()
    result = []
    for app in applications:
        app_dict = app.to_dict()
        app_dict['job'] = app.job_obj.to_dict() if app.job_obj else None
        result.append(app_dict)
    return jsonify({'applications': result}), 200


@applications_bp.route('/resume/<path:filename>', methods=['GET'])
@jwt_required()
def get_resume_file(filename):
    """Serve resume file (recruiter or admin only)."""
    claims = get_jwt()
    if claims.get('role') not in ['recruiter', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403

    from flask import send_from_directory
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    safe_name = secure_filename(os.path.basename(filename))
    if not os.path.exists(os.path.join(upload_dir, safe_name)):
        return jsonify({'error': 'File not found'}), 404
    return send_from_directory(upload_dir, safe_name, as_attachment=True)
