"""User model."""
from .db import db
from datetime import datetime

class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255))
    role = db.Column(db.Enum('candidate', 'recruiter', 'admin', name='user_role_enum'), nullable=False)
    otp = db.Column(db.String(6))
    otp_expires_at = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_verified': self.is_verified
        }
