from flask import Blueprint, request, jsonify
import jwt

admin_bp = Blueprint('admin', __name__)

# Import from other modules
import routes.auth as auth_module
import routes.jobs as jobs_module

@admin_bp.route('/admin/recruiters', methods=['GET'])
def get_recruiters():
    """Get all recruiters"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        recruiters = [u for u in auth_module.users.values() if u.get('role') == 'recruiter']
        return jsonify(recruiters), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@admin_bp.route('/admin/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        candidates = [u for u in auth_module.users.values() if u.get('role') == 'candidate']
        return jsonify(candidates), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@admin_bp.route('/admin/jobs', methods=['GET'])
def get_admin_jobs():
    """Get all jobs (admin view)"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        job_list = list(jobs_module.jobs.values())
        return jsonify(job_list), 200
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
        recruiters = [u for u in auth_module.users.values() if u.get('role') == 'recruiter']
        candidates = [u for u in auth_module.users.values() if u.get('role') == 'candidate']
        jobs = list(jobs_module.jobs.values())
        applications = list(jobs_module.applications.values())
        
        return jsonify({
            'total_recruiters': len(recruiters),
            'total_candidates': len(candidates),
            'total_jobs': len(jobs),
            'total_applications': len(applications),
            'active_jobs': len([j for j in jobs if j.get('is_active', True)])
        }), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401
