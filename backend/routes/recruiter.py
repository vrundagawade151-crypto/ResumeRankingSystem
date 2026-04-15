from flask import Blueprint, request, jsonify
from datetime import datetime
import jwt
from config import Config
from database import db
from models.user import User
from models.job import Job
from models.application import Application

recruiter_bp = Blueprint('recruiter', __name__)

@recruiter_bp.route('/recruiter/profile', methods=['GET'])
def get_recruiter_profile():
    """Get recruiter profile"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = data.get('user_id')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'company': user.company or ''
        }), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@recruiter_bp.route('/recruiter/profile', methods=['PUT'])
def update_recruiter_profile():
    """Update recruiter profile"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = data.get('user_id')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        update_data = request.get_json()
        
        if 'username' in update_data:
            user.username = update_data['username']
        if 'company' in update_data:
            user.company = update_data['company']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'company': user.company or ''
            }
        }), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@recruiter_bp.route('/recruiter/reports', methods=['GET'])
def generate_reports():
    """Generate reports for recruiter's jobs with applicants"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = data.get('user_id')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
    except:
        return jsonify({'message': 'Invalid token'}), 401
    
    jobs = Job.query.filter_by(company=user.company).all() if user.company else Job.query.all()
    
    reports = []
    for job in jobs:
        applications = Application.query.filter_by(job_id=job.id).all()
        
        if not applications:
            continue
        
        pending_count = sum(1 for a in applications if a.status == 'pending')
        reviewed_count = sum(1 for a in applications if a.status == 'reviewed')
        accepted_count = sum(1 for a in applications if a.status == 'accepted')
        rejected_count = sum(1 for a in applications if a.status == 'rejected')
        
        avg_score = 0
        scored_apps = [a for a in applications if a.ai_score is not None]
        if scored_apps:
            avg_score = sum(a.ai_score for a in scored_apps) / len(scored_apps)
        
        candidates = []
        for app in applications:
            candidate = {
                'application_id': app.id,
                'applicant_name': app.applicant_name,
                'applicant_email': app.applicant_email,
                'status': app.status,
                'score': app.ai_score,
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                'domain': app.domain,
                'experience_years': app.experience_years,
                'linkedin_id': app.linkedin_id,
                'github_id': app.github_id,
                'extracted_certifications': app.extracted_certifications,
                'name_mismatch': app.name_mismatch,
                'name_mismatch_reason': app.name_mismatch_reason
            }
            candidates.append(candidate)
        
        candidates.sort(key=lambda x: x['score'] or 0, reverse=True)
        
        reports.append({
            'job_id': job.id,
            'job_title': job.title,
            'company': job.company,
            'domain': job.domain,
            'deadline': job.deadline.isoformat() if job.deadline else None,
            'total_applications': len(applications),
            'pending': pending_count,
            'reviewed': reviewed_count,
            'accepted': accepted_count,
            'rejected': rejected_count,
            'average_score': round(avg_score, 2),
            'candidates': candidates
        })
    
    return jsonify({'reports': reports}), 200

@recruiter_bp.route('/recruiter/reports/<int:job_id>', methods=['GET'])
def generate_single_report(job_id):
    """Generate report for a specific job"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
    except:
        return jsonify({'message': 'Invalid token'}), 401
    
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    applications = Application.query.filter_by(job_id=job_id).all()
    
    if not applications:
        return jsonify({'message': 'No applications for this job'}), 404
    
    pending_count = sum(1 for a in applications if a.status == 'pending')
    reviewed_count = sum(1 for a in applications if a.status == 'reviewed')
    accepted_count = sum(1 for a in applications if a.status == 'accepted')
    rejected_count = sum(1 for a in applications if a.status == 'rejected')
    
    avg_score = 0
    scored_apps = [a for a in applications if a.ai_score is not None]
    if scored_apps:
        avg_score = sum(a.ai_score for a in scored_apps) / len(scored_apps)
    
    candidates = []
    for app in applications:
        candidate = {
            'application_id': app.id,
            'applicant_name': app.applicant_name,
            'applicant_email': app.applicant_email,
            'status': app.status,
            'score': app.ai_score,
            'applied_at': app.applied_at.isoformat() if app.applied_at else None,
            'domain': app.domain,
            'experience_years': app.experience_years,
            'linkedin_id': app.linkedin_id,
            'github_id': app.github_id,
            'extracted_certifications': app.extracted_certifications,
            'name_mismatch': app.name_mismatch,
            'name_mismatch_reason': app.name_mismatch_reason
        }
        candidates.append(candidate)
    
    candidates.sort(key=lambda x: x['score'] or 0, reverse=True)
    
    report = {
        'job_id': job.id,
        'job_title': job.title,
        'company': job.company,
        'domain': job.domain,
        'deadline': job.deadline.isoformat() if job.deadline else None,
        'total_applications': len(applications),
        'pending': pending_count,
        'reviewed': reviewed_count,
        'accepted': accepted_count,
        'rejected': rejected_count,
        'average_score': round(avg_score, 2),
        'candidates': candidates
    }
    
    return jsonify(report), 200
