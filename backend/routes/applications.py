from flask import Blueprint, request, jsonify
from datetime import datetime
from config import Config
from database import db
from models.job import Job
from models.application import Application
from models.user import User
import jwt

applications_bp = Blueprint('applications', __name__)

# In-memory notification store
notifications = {}  # recruiter_email -> list of notifications

def add_notification(recruiter_email, message, job_title, candidate_name):
    """Add notification for recruiter"""
    if recruiter_email not in notifications:
        notifications[recruiter_email] = []
    notifications[recruiter_email].append({
        'id': len(notifications[recruiter_email]) + 1,
        'message': message,
        'job_title': job_title,
        'candidate_name': candidate_name,
        'created_at': datetime.utcnow().isoformat(),
        'read': False
    })

def extract_name_from_resume(resume_path):
    """Extract name from resume text"""
    if not resume_path:
        return None
    try:
        from utils.resume_extractor import extract_text_from_file
        text = extract_text_from_file(resume_path)
        if not text:
            print("No text extracted from resume for name extraction")
            return None
        lines = text.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            if len(first_line) > 0 and len(first_line) < 100:
                print(f"Extracted name from resume: {first_line}")
                return first_line
        return None
    except Exception as e:
        print(f"Error extracting name from resume: {e}")
        return None

def extract_certifications_from_resume(resume_path):
    """Extract certifications from resume text"""
    if not resume_path:
        return ""
    try:
        from utils.resume_extractor import extract_text_from_file
        text = extract_text_from_file(resume_path)
        if not text:
            return ""
        
        cert_keywords = ['certification', 'certificate', 'certified', 'license', 'accreditation']
        certs = []
        
        text_lower = text.lower()
        for keyword in cert_keywords:
            if keyword in text_lower:
                idx = text_lower.find(keyword)
                start = max(0, idx - 50)
                end = min(len(text), idx + 150)
                snippet = text[start:end].strip()
                if snippet:
                    certs.append(snippet)
        
        return " | ".join(certs[:10]) if certs else ""
    except Exception as e:
        print(f"Error extracting certifications: {e}")
        return ""

def extract_experience_years(text):
    """Extract years of experience from text"""
    if not text:
        return 0
    import re
    patterns = [
        r'(\d+)\+?\s*(?:years?|yrs?)',
        r'(\d+)\s*-\s*\d+\s*(?:years?|yrs?)',
        r'experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)'
    ]
    max_years = 0
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            years = int(match)
            if years > max_years:
                max_years = years
    return max_years

@applications_bp.route('/applications', methods=['POST'])
def create_application():
    """Apply for a job"""
    print(f"Request form: {request.form}")
    print(f"Request files: {request.files}")
    print(f"Content-Type: {request.content_type}")
    
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_email = data.get('email')
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"Token error: {e}")
        return jsonify({'error': 'Invalid token'}), 401
    
    job_id = request.form.get('job_id')
    applicant_name = request.form.get('name') or request.form.get('applicant_name')
    applicant_email = request.form.get('email') or request.form.get('applicant_email')
    
    if not job_id or not applicant_name or not applicant_email:
        return jsonify({'error': 'Missing required fields (job_id, name, email required)'}), 400
    
    try:
        job_id = int(job_id)
    except ValueError:
        return jsonify({'error': 'Invalid job ID'}), 400
        
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    resume_file = request.files.get('resume')
    resume_path = ''
    if resume_file:
        import os
        from werkzeug.utils import secure_filename
        # Create uploads folder in project root
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(resume_file.filename)
        resume_path = os.path.join('uploads', f"app_{filename}")
        resume_file.save(resume_path)
    
    name_mismatch = False
    name_mismatch_reason = ""
    extracted_name = None
    
    if resume_path:
        extracted_name = extract_name_from_resume(resume_path)
        if extracted_name:
            form_name_lower = applicant_name.lower().strip()
            extracted_name_lower = extracted_name.lower().strip()
            
            form_name_parts = set(form_name_lower.split())
            extracted_name_parts = set(extracted_name_lower.split())
            
            common_words = form_name_parts & extracted_name_parts
            if len(common_words) < min(len(form_name_parts), len(extracted_name_parts)) * 0.5:
                name_mismatch = True
                name_mismatch_reason = f"Name in form ({applicant_name}) does not match name in resume ({extracted_name})"
    
    certification_file = request.files.get('certification')
    certification_path = ''
    if certification_file:
        import os
        from werkzeug.utils import secure_filename
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(certification_file.filename)
        certification_path = os.path.join('uploads', f"cert_{filename}")
        certification_file.save(certification_path)
    
    extracted_certifications = ""
    experience_years = 0
    if resume_path:
        extracted_certifications = extract_certifications_from_resume(resume_path)
        try:
            from utils.resume_extractor import extract_text_from_file
            resume_text = extract_text_from_file(resume_path)
            experience_years = extract_experience_years(resume_text)
        except:
            pass
    
    domain = request.form.get('domain', '')
    if not domain and user.domain:
        domain = user.domain
    
    application = Application(
        job_id=job_id,
        user_id=user.id,
        applicant_name=applicant_name,
        applicant_email=applicant_email,
        resume_path=resume_path,
        cover_letter=request.form.get('cover_letter', ''),
        status='rejected' if name_mismatch else 'pending',
        linkedin_id=request.form.get('linkedin_id', ''),
        github_id=request.form.get('github_id', ''),
        certification_path=certification_path,
        domain=domain,
        name_mismatch=name_mismatch,
        name_mismatch_reason=name_mismatch_reason,
        extracted_certifications=extracted_certifications,
        experience_years=experience_years
    )
    
    db.session.add(application)
    db.session.commit()
    
    # Add notification for recruiter
    if not name_mismatch:
        recruiter = User.query.filter_by(company=job.company, role='recruiter').first()
        if recruiter:
            add_notification(
                recruiter.email,
                f"New application from {applicant_name} for {job.title}",
                job.title,
                applicant_name
            )
    
    if name_mismatch:
        return jsonify({
            **application.to_dict(),
            'message': 'Application rejected due to name mismatch'
        }), 201
    
    return jsonify(application.to_dict()), 201

@applications_bp.route('/applications/job/<int:job_id>', methods=['GET'])
def get_job_applications(job_id):
    """Get all applications for a job"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'message': 'Job not found'}), 404
    
    applications = Application.query.filter_by(job_id=job_id).all()
    return jsonify([app.to_dict() for app in applications]), 200

@applications_bp.route('/applications/candidate', methods=['GET'])
def get_candidate_applications():
    """Get applications for the current candidate"""
    # Get token from header
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_email = data.get('email')
        
        # Filter applications by email
        applications = Application.query.filter_by(applicant_email=user_email).all()
        return jsonify([app.to_dict() for app in applications]), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@applications_bp.route('/applications/<int:app_id>', methods=['GET'])
def get_application(app_id):
    """Get a specific application"""
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    return jsonify(application.to_dict()), 200

@applications_bp.route('/applications/<int:app_id>', methods=['PUT'])
def update_application(app_id):
    """Update application status"""
    application = Application.query.get(app_id)
    if not application:
        return jsonify({'message': 'Application not found'}), 404
    
    data = request.get_json()
    application.status = data.get('status', application.status)
    application.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(application.to_dict()), 200

@applications_bp.route('/applications/resume/<path:filename>', methods=['GET'])
def download_resume(filename):
    """Download a resume file"""
    import os
    from flask import send_file
    
    # Path is relative to the backend directory where 'uploads' is created
    file_path = filename
    if not os.path.exists(file_path):
        return jsonify({'message': 'File not found'}), 404
        
    return send_file(file_path, as_attachment=True)

@applications_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for recruiter"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_email = data.get('email')
    except:
        return jsonify({'error': 'Invalid token'}), 401
    
    user_notifications = notifications.get(user_email, [])
    return jsonify({'notifications': user_notifications}), 200

@applications_bp.route('/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    """Mark notifications as read"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_email = data.get('email')
    except:
        return jsonify({'error': 'Invalid token'}), 401
    
    if user_email in notifications:
        for notif in notifications[user_email]:
            notif['read'] = True
    
    return jsonify({'message': 'Notifications marked as read'}), 200

