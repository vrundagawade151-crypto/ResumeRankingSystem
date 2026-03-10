"""Job model."""
from .db import db
from datetime import datetime

class Job(db.Model):
    """Job posting model."""
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiters.id', ondelete='CASCADE'), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    required_skills = db.Column(db.Text, nullable=False)
    experience_required = db.Column(db.String(100))
    job_description = db.Column(db.Text, nullable=False)
    number_of_openings = db.Column(db.Integer, default=1)
    status = db.Column(db.Enum('active', 'closed'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = db.relationship('Application', backref='job_obj', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'recruiter_id': self.recruiter_id,
            'job_title': self.job_title,
            'company_name': self.company_name,
            'required_skills': self.required_skills,
            'experience_required': self.experience_required,
            'job_description': self.job_description,
            'number_of_openings': self.number_of_openings,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
