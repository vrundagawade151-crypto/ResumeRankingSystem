"""Resume model for extracted/AI processed data."""
from .db import db
from datetime import datetime

class Resume(db.Model):
    """Resume extraction model."""
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    extracted_name = db.Column(db.String(255))
    extracted_skills = db.Column(db.Text)
    extracted_education = db.Column(db.Text)
    extracted_experience = db.Column(db.Text)
    raw_text = db.Column(db.Text)
    ranking_score = db.Column(db.Numeric(5, 2), default=0)
    skill_match_score = db.Column(db.Numeric(5, 2), default=0)
    experience_match_score = db.Column(db.Numeric(5, 2), default=0)
    education_match_score = db.Column(db.Numeric(5, 2), default=0)
    processed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'extracted_name': self.extracted_name,
            'extracted_skills': self.extracted_skills,
            'extracted_education': self.extracted_education,
            'extracted_experience': self.extracted_experience,
            'ranking_score': float(self.ranking_score) if self.ranking_score else 0,
            'skill_match_score': float(self.skill_match_score) if self.skill_match_score else 0,
            'experience_match_score': float(self.experience_match_score) if self.experience_match_score else 0,
            'education_match_score': float(self.education_match_score) if self.education_match_score else 0,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
