"""AI Resume Screening and Ranking routes."""
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from models.db import db
from models.application import Application
from models.resume import Resume
from models.job import Job
from models.recruiter import Recruiter
from ai_engine.resume_parser import ResumeParser
from ai_engine.ranking_engine import RankingEngine

ai_screening_bp = Blueprint('ai_screening', __name__, url_prefix='/api/ai-screening')


@ai_screening_bp.route('/extract', methods=['POST'])
@jwt_required()
def extract_and_rank_resumes():
    """
    Extract resumes using NLP and rank candidates.
    Body: { job_id: int, limit: int (optional, default all), file_type: 'pdf'|'docx' }
    """
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    job_id = data.get('job_id')
    limit = data.get('limit', 100)  # Max resumes to process
    file_type = data.get('file_type', 'all')  # pdf, docx, or all

    if not job_id:
        return jsonify({'error': 'job_id is required'}), 400

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    recruiter = Recruiter.query.filter_by(user_id=claims.get('sub')).first()
    if job.recruiter_id != recruiter.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get applications with resume files
    applications = Application.query.filter_by(job_id=job_id).all()
    upload_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    parser = ResumeParser()
    ranking_results = []

    processed = 0
    for app in applications:
        if processed >= limit:
            break
        if not app.resume_path:
            continue

        file_path = os.path.join(upload_dir, app.resume_path)
        if not os.path.exists(file_path):
            continue

        ext = os.path.splitext(app.resume_path)[1].lower()
        if file_type == 'pdf' and ext != '.pdf':
            continue
        if file_type == 'docx' and ext not in ['.docx', '.doc']:
            continue

        try:
            parsed = parser.parse(file_path)
        except Exception as e:
            ranking_results.append({
                'application_id': app.id,
                'name': app.name,
                'email': app.email,
                'error': str(e),
                'ranking_score': 0
            })
            continue

        # Use extracted data or fallback to form data
        skills = parsed.get('skills') or app.skills or ''
        education = parsed.get('education') or app.education or ''
        experience = parsed.get('experience') or app.experience or ''

        # Calculate ranking
        engine = RankingEngine(
            job.required_skills,
            job.experience_required,
            job.job_description
        )
        scores = engine.calculate_ranking(skills, education, experience)

        # Save or update Resume record
        resume_record = Resume.query.filter_by(application_id=app.id).first()
        if not resume_record:
            resume_record = Resume(application_id=app.id)
            db.session.add(resume_record)

        resume_record.extracted_name = parsed.get('name')
        resume_record.extracted_skills = skills
        resume_record.extracted_education = education
        resume_record.extracted_experience = experience
        resume_record.raw_text = parsed.get('raw_text', '')[:5000]
        resume_record.ranking_score = scores['ranking_score']
        resume_record.skill_match_score = scores['skill_match_score']
        resume_record.experience_match_score = scores['experience_match_score']
        resume_record.education_match_score = scores['education_match_score']
        resume_record.processed_at = datetime.utcnow()
        app.status = 'screened'

        ranking_results.append({
            'application_id': app.id,
            'name': parsed.get('name') or app.name,
            'email': app.email,
            'extracted_skills': skills,
            'extracted_education': education,
            'extracted_experience': experience,
            'ranking_score': scores['ranking_score'],
            'skill_match_score': scores['skill_match_score'],
            'experience_match_score': scores['experience_match_score'],
            'education_match_score': scores['education_match_score']
        })
        processed += 1

    db.session.commit()

    # Sort by ranking score descending
    ranking_results.sort(key=lambda x: x['ranking_score'], reverse=True)

    return jsonify({
        'job_id': job_id,
        'processed_count': processed,
        'total_applicants': len(applications),
        'ranked_candidates': ranking_results
    }), 200


@ai_screening_bp.route('/ranked/<int:job_id>', methods=['GET'])
@jwt_required()
def get_ranked_candidates(job_id):
    """Get previously ranked candidates for a job."""
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    recruiter = Recruiter.query.filter_by(user_id=claims.get('sub')).first()
    if job.recruiter_id != recruiter.id:
        return jsonify({'error': 'Unauthorized'}), 403

    applications = Application.query.filter_by(job_id=job_id).all()
    result = []
    for app in applications:
        app_dict = app.to_dict()
        if app.resume_data:
            app_dict['resume_extraction'] = app.resume_data.to_dict()
        result.append(app_dict)

    result.sort(key=lambda x: (x.get('ranking_score') or 0), reverse=True)
    return jsonify({'ranked_candidates': result}), 200
