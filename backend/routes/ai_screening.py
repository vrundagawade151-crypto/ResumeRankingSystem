from flask import Blueprint, request, jsonify
import os
import sys
from database import db
from models.job import Job
from models.application import Application

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ai_bp = Blueprint('ai', __name__)

# Import the resume extractor
try:
    from utils.resume_extractor import extract_text_from_file
except ImportError:
    from backend.utils.resume_extractor import extract_text_from_file


@ai_bp.route('/ai-screening/extract', methods=['POST'])
def extract_and_rank():
    """Extract and rank resumes for a job"""
    data = request.get_json()
    
    if not data or not data.get('job_id'):
        return jsonify({'message': 'Job ID is required'}), 400
    
    job_id = data['job_id']
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    job_domain = job.domain.lower() if job.domain else ""
    
    applications = Application.query.filter_by(job_id=job_id).all()
    
    ranked = []
    for app in applications:
        if app.name_mismatch:
            ranked.append({
                'application_id': app.id,
                'applicant_name': app.applicant_name,
                'applicant_email': app.applicant_email,
                'score': 0,
                'status': app.status,
                'resume_path': app.resume_path,
                'extracted_skills': '',
                'extracted_experience': '',
                'extracted_education': '',
                'domain_match': False,
                'name_mismatch': True,
                'name_mismatch_reason': app.name_mismatch_reason,
                'extracted_certifications': app.extracted_certifications,
                'experience_years': app.experience_years,
                'linkedin_id': app.linkedin_id,
                'github_id': app.github_id
            })
            continue
        
        resume_text = ""
        if app.resume_path:
            try:
                resume_text = extract_text_from_file(app.resume_path) or ""
            except Exception as e:
                print(f"Error extracting text from {app.resume_path}: {e}")
                resume_text = ""
        
        combined_text = resume_text + " " + (app.cover_letter or "")
        
        domain_match = False
        if job_domain and app.domain:
            app_domain_lower = app.domain.lower()
            if job_domain in app_domain_lower or app_domain_lower in job_domain:
                domain_match = True
        
        score, details = calculate_score(combined_text, job, domain_match, app.experience_years)
        
        app.ai_score = score
        app.ai_feedback = details.get('feedback', '')
        
        if domain_match:
            score += min(app.experience_years * 2, 20)
        
        app.ai_score = min(score, 100)
        
        ranked.append({
            'application_id': app.id,
            'applicant_name': app.applicant_name,
            'applicant_email': app.applicant_email,
            'score': app.ai_score,
            'status': app.status,
            'resume_path': app.resume_path,
            'extracted_skills': details.get('skills', ''),
            'extracted_experience': details.get('experience', ''),
            'extracted_education': details.get('education', ''),
            'domain_match': domain_match,
            'domain': app.domain,
            'extracted_certifications': app.extracted_certifications,
            'experience_years': app.experience_years,
            'linkedin_id': app.linkedin_id,
            'github_id': app.github_id
        })
    
    db.session.commit()
    
    ranked.sort(key=lambda x: x['score'], reverse=True)
    
    return jsonify({
        'job_id': job_id,
        'job_title': job.title,
        'company': job.company,
        'domain': job.domain,
        'total_applications': len(applications),
        'ranked_candidates': ranked
    }), 200

@ai_bp.route('/ai-screening/ranked/<int:job_id>', methods=['GET'])
def get_ranked_candidates(job_id):
    """Get ranked candidates for a job"""
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    # Get all applications for this job
    applications = Application.query.filter_by(job_id=job_id).order_by(Application.ai_score.desc()).all()
    
    return jsonify({
        'job_id': job_id,
        'ranked_candidates': [app.to_dict() for app in applications]
    }), 200

@ai_bp.route('/ai/screen/<int:app_id>', methods=['POST'])
def screen_application(app_id):
    """Screen a single application using AI"""
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    
    # Get job details for comparison
    job = Job.query.get(application.job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    # Extract text from resume file if exists
    resume_text = ""
    if application.resume_path:
        try:
            resume_text = extract_text_from_file(application.resume_path) or ""
        except Exception as e:
            print(f"Error extracting text from resume: {e}")
            resume_text = ""
    
    # Combine with cover letter
    combined_text = resume_text + " " + (application.cover_letter or "")
    
    # Calculate score
    score, details = calculate_score(combined_text, job, False, 0)
    feedback = details.get('feedback', f"Resume screened. Match score: {score}%")
    
    # Update application with AI results
    application.ai_score = score
    application.ai_feedback = feedback
    application.status = 'reviewed'
    
    db.session.commit()
    
    return jsonify({
        'application_id': app_id,
        'ai_score': score,
        'ai_feedback': feedback,
        'status': application.status,
        'extracted_skills': details.get('skills', ''),
        'extracted_experience': details.get('experience', ''),
        'extracted_education': details.get('education', '')
    }), 200

def calculate_score(text, job, domain_match=False, experience_years=0):
    """Calculate matching score based on resume content and job requirements"""
    if not text:
        return 0, {'skills': '', 'experience': '', 'education': '', 'feedback': 'No resume content found'}
    
    text = text.lower()
    
    score = 50  # Base score
    skills_found = []
    exp_count = 0
    education_found = []
    
    job_title = job.title.lower() if job.title else ''
    job_requirements = job.requirements.lower() if job.requirements else ''
    job_description = job.description.lower() if job.description else ''
    job_skills = job.requirements.lower() if job.requirements else ''
    job_domain = job.domain.lower() if job.domain else ''
    
    skill_keywords = [
        'python', 'java', 'javascript', 'react', 'node', 'sql', 'html', 'css',
        'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'git', 'linux',
        'machine learning', 'data analysis', 'communication', 'teamwork',
        'leadership', 'project management', 'agile', 'scrum', 'typescript',
        'angular', 'vue', 'django', 'flask', 'spring', 'hibernate',
        'mongodb', 'postgresql', 'mysql', 'redis', 'graphql', 'rest api'
    ]
    
    for skill in skill_keywords:
        if skill in text:
            skills_found.append(skill)
    
    required_skills = [s.strip() for s in job_skills.split(',') if s.strip()]
    matched_skills = [s for s in required_skills if s.lower() in text]
    
    skill_match_score = min(len(matched_skills) * 5, 20)
    score += skill_match_score
    
    exp_keywords = ['years', 'year', 'experience', 'exp', 'senior', 'junior', 'lead', 'manager']
    exp_count = sum(1 for kw in exp_keywords if kw in text)
    if exp_count > 0:
        score += min(exp_count * 2, 10)
    
    edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'engineering']
    edu_count = sum(1 for kw in edu_keywords if kw in text)
    if edu_count > 0:
        score += min(edu_count * 2, 10)
    
    if job_title:
        title_words = job_title.split()
        for word in title_words:
            if len(word) > 2 and word in text:
                score += 3
    
    if job_requirements:
        req_words = [w.strip() for w in job_requirements.split() if len(w.strip()) > 3]
        req_matches = sum(1 for w in req_words if w in text)
        score += min(req_matches, 10)
    
    if job.job_type and job.job_type.lower() in text:
        score += 5
    
    if domain_match:
        score += 15
        domain_bonus = True
    else:
        domain_bonus = False
    
    final_score = min(score, 100)
    
    if domain_match:
        feedback = f"Score: {final_score}%. Domain matched. Matched {len(matched_skills)} of {len(required_skills)} required skills. Experience: {experience_years} years."
    else:
        feedback = f"Score: {final_score}%. Domain not matched. Only {len(matched_skills)} of {len(required_skills)} required skills matched."
    
    return final_score, {
        'skills': ', '.join(skills_found[:10]),
        'experience': f"{exp_count} experience indicators found",
        'education': f"{edu_count} education indicators found",
        'feedback': feedback
    }
