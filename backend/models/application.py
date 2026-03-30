from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from database import db

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    applicant_name = Column(String(200), nullable=False)
    applicant_email = Column(String(120), nullable=False)
    resume_path = Column(String(500))
    cover_letter = Column(Text)
    status = Column(String(50), default='pending')  # pending, reviewed, accepted, rejected
    ai_score = Column(Integer)  # AI screening score
    ai_feedback = Column(Text)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'user_id': self.user_id,
            'applicant_name': self.applicant_name,
            'applicant_email': self.applicant_email,
            'resume_path': self.resume_path,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'ai_score': self.ai_score,
            'ai_feedback': self.ai_feedback,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
