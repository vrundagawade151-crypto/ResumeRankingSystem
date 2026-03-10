"""Recruiter model."""
from .db import db
from datetime import datetime

class Recruiter(db.Model):
    """Recruiter model."""
    __tablename__ = 'recruiters'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('recruiter', uselist=False))
    jobs = db.relationship('Job', backref='recruiter_obj', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'company_name': self.company_name,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
