"""Application model."""
from .db import db
from datetime import datetime

class Application(db.Model):
    """Job application model."""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    resume_path = db.Column(db.String(500))
    status = db.Column(db.Enum('pending', 'screened', 'shortlisted', 'rejected', name='application_status_enum'), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resume_data = db.relationship('Resume', backref='application_obj', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'candidate_id': self.candidate_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'skills': self.skills,
            'education': self.education,
            'experience': self.experience,
            'resume_path': self.resume_path,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ranking_score': float(self.resume_data.ranking_score) if self.resume_data and self.resume_data.ranking_score else None
        }
