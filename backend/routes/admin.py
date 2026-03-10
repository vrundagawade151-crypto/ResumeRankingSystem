"""Admin panel routes."""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.db import db
from models.user import User
from models.candidate import Candidate
from models.recruiter import Recruiter
from models.job import Job
from models.application import Application

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def admin_required(fn):
    """Decorator to require admin role."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return fn(*args, **kwargs)
    return wrapper


@admin_bp.route('/recruiters', methods=['GET'])
@jwt_required()
@admin_required
def list_recruiters():
    """View all recruiters."""
    recruiters = Recruiter.query.all()
    return jsonify({'recruiters': [r.to_dict() for r in recruiters]}), 200


@admin_bp.route('/candidates', methods=['GET'])
@jwt_required()
@admin_required
def list_candidates():
    """View all candidates."""
    candidates = Candidate.query.all()
    return jsonify({'candidates': [c.to_dict() for c in candidates]}), 200


@admin_bp.route('/jobs', methods=['GET'])
@jwt_required()
@admin_required
def list_all_jobs():
    """View all job postings."""
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    result = []
    for job in jobs:
        j = job.to_dict()
        j['recruiter'] = job.recruiter_obj.to_dict() if job.recruiter_obj else None
        j['applicant_count'] = job.applications.count()
        result.append(j)
    return jsonify({'jobs': result}), 200


@admin_bp.route('/statistics', methods=['GET'])
@jwt_required()
@admin_required
def get_statistics():
    """View application statistics."""
    total_recruiters = Recruiter.query.count()
    total_candidates = Candidate.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    active_jobs = Job.query.filter_by(status='active').count()

    return jsonify({
        'total_recruiters': total_recruiters,
        'total_candidates': total_candidates,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'active_jobs': active_jobs
    }), 200
