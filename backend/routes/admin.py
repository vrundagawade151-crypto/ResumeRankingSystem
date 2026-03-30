from flask import Blueprint, request, jsonify
import jwt
from config import Config
from database import db
from models.user import User
from models.job import Job
from models.application import Application

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/recruiters', methods=['GET'])
def get_recruiters():
    """Get all recruiters"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        recruiters = User.query.filter_by(role='recruiter').all()
        return jsonify([user.to_dict() for user in recruiters]), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@admin_bp.route('/admin/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        candidates = User.query.filter_by(role='candidate').all()
        return jsonify([user.to_dict() for user in candidates]), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@admin_bp.route('/admin/jobs', methods=['GET'])
def get_admin_jobs():
    """Get all jobs (admin view)"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        jobs = Job.query.all()
        return jsonify([job.to_dict() for job in jobs]), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@admin_bp.route('/admin/statistics', methods=['GET'])
def get_statistics():
    """Get admin statistics"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        # Count users by role
        recruiters_count = User.query.filter_by(role='recruiter').count()
        candidates_count = User.query.filter_by(role='candidate').count()
        total_jobs = Job.query.count()
        total_applications = Application.query.count()
        active_jobs = Job.query.filter_by(is_active=True).count()
        
        return jsonify({
            'total_recruiters': recruiters_count,
            'total_candidates': candidates_count,
            'total_jobs': total_jobs,
            'total_applications': total_applications,
            'active_jobs': active_jobs
        }), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401
