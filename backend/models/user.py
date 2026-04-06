from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), default='candidate')  # candidate, recruiter, admin
    company = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'role': self.role,
            'company': self.company,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
