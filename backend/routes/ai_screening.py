from flask import Blueprint, request, jsonify
import os

ai_bp = Blueprint('ai', __name__)

# Import from jobs module (shared storage)
import routes.jobs as jobs_module

@ai_bp.route('/ai-screening/extract', methods=['POST'])
def extract_and_rank():
    """Extract and rank resumes for a job"""
    data = request.get_json()
    
    if not data or not data.get('job_id'):
        return jsonify({'message': 'Job ID is required'}), 400
    
    job_id = data['job_id']
    job = jobs_module.jobs.get(job_id)
    
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    # Get all applications for this job
    applications = [app for app in jobs_module.applications.values() if app['job_id'] == job_id]
    
    # Simple ranking based on keywords
    ranked = []
    for app in applications:
        score = calculate_score(app, job)
        app['ai_score'] = score
        ranked.append({
            'application_id': app['id'],
            'applicant_name': app['applicant_name'],
            'applicant_email': app['applicant_email'],
            'score': score,
            'status': app['status']
        })
    
    # Sort by score descending
    ranked.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'job_id': job_id,
        'total_applications': len(applications),
        'ranked_candidates': ranked
    }), 200

@ai_bp.route('/ai-screening/ranked/<int:job_id>', methods=['GET'])
def get_ranked_candidates(job_id):
    """Get ranked candidates for a job"""
    job = jobs_module.jobs.get(job_id)
    
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    # Get all applications for this job
    applications = [app for app in jobs_module.applications.values() if app['job_id'] == job_id]
    
    # Sort by score
    ranked = sorted(applications, key=lambda x: x.get('ai_score', 0), reverse=True)
    
    return jsonify({
        'job_id': job_id,
        'candidates': ranked
    }), 200

@ai_bp.route('/ai/screen/<int:app_id>', methods=['POST'])
def screen_application(app_id):
    """Screen a single application using AI"""
    application = jobs_module.applications.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    
    # Get job details for comparison
    job = jobs_module.jobs.get(application['job_id'])
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    # Calculate score
    score = calculate_score(application, job)
    feedback = f"Resume screened. Match score: {score}%"
    
    # Update application with AI results
    application['ai_score'] = score
    application['ai_feedback'] = feedback
    application['status'] = 'reviewed'
    
    return jsonify({
        'application_id': app_id,
        'ai_score': score,
        'ai_feedback': feedback,
        'status': application['status']
    }), 200

def calculate_score(application, job):
    """Calculate matching score based on resume content and job requirements"""
    score = 50  # Base score
    
    # Check cover letter
    cover_letter = application.get('cover_letter', '').lower()
    job_title = job.get('title', '').lower()
    job_requirements = job.get('requirements', '').lower()
    job_description = job.get('description', '').lower()
    
    # Add points for relevant keywords
    keywords = ['experience', 'skills', 'qualified', 'degree', 'years', 'project', 'manager', 'developer', 'engineer']
    for keyword in keywords:
        if keyword in cover_letter:
            score += 3
        if keyword in job_requirements and keyword in cover_letter:
            score += 2
        if keyword in job_title and keyword in cover_letter:
            score += 2
    
    # Bonus for matching job type
    if job.get('job_type') in cover_letter:
        score += 5
    
    # Cap score at 100
    return min(score, 100)
