"""Authentication routes - OTP login simulation."""
import random
import string
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models.db import db
from models.user import User
from models.candidate import Candidate
from models.recruiter import Recruiter

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP for login (simulated - returns OTP in response for demo)."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()  # Normalize email to lowercase
    role = data.get('role', 'candidate')  # candidate, recruiter, admin
    name = data.get('name')  # For registration
    company_name = data.get('company_name')  # For recruiter registration
    phone = data.get('phone')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    otp = generate_otp(6)
    otp_expires = datetime.utcnow() + timedelta(minutes=10)

    user = User.query.filter_by(email=email).first()

    if user:
        user.otp = otp
        user.otp_expires_at = otp_expires
        db.session.commit()
    else:
        # New user - create account
        if role == 'admin':
            return jsonify({'error': 'Admin registration not allowed'}), 403

        user = User(
            email=email,
            role=role,
            otp=otp,
            otp_expires_at=otp_expires,
            is_verified=False
        )
        db.session.add(user)
        db.session.commit()

        if role == 'candidate' and name:
            candidate = Candidate(
                user_id=user.id,
                name=name,
                email=email,
                phone=phone or ''
            )
            db.session.add(candidate)
        elif role == 'recruiter' and name:
            recruiter = Recruiter(
                user_id=user.id,
                name=name,
                email=email,
                company_name=company_name or '',
                phone=phone or ''
            )
            db.session.add(recruiter)
        db.session.commit()

    # In production, send OTP via email/SMS. For demo, return in response
    return jsonify({
        'message': 'OTP sent successfully',
        'otp': otp,  # REMOVE IN PRODUCTION - only for demo
        'email': email
    }), 200


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and return JWT token."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()  # Normalize email to lowercase
    otp = data.get('otp', '').strip()  # Strip whitespace from OTP
    role = data.get('role', 'candidate')

    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found. Please request a new OTP.'}), 404

    # Verify the role matches what was used during registration
    if user.role != role:
        return jsonify({'error': 'Invalid role for this email. Please use the correct role.'}), 401

    if user.otp != otp:
        return jsonify({'error': 'Invalid OTP'}), 401

    if user.otp_expires_at and user.otp_expires_at < datetime.utcnow():
        return jsonify({'error': 'OTP has expired'}), 401

    user.is_verified = True
    user.otp = None
    user.otp_expires_at = None
    db.session.commit()

    # Get profile based on role
    profile = None
    if role == 'candidate':
        candidate = Candidate.query.filter_by(user_id=user.id).first()
        profile = candidate.to_dict() if candidate else {'email': user.email}
    elif role == 'recruiter':
        recruiter = Recruiter.query.filter_by(user_id=user.id).first()
        profile = recruiter.to_dict() if recruiter else {'email': user.email}
    elif role == 'admin':
        profile = {'email': user.email, 'role': 'admin'}

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': role, 'email': user.email}
    )

    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'profile': profile,
        'role': role
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login_direct():
    """Direct login for admin (email + password) and demo purposes."""
    data = request.get_json()
    email = data.get('email', '').strip().lower()  # Normalize email to lowercase
    password = data.get('password')
    role = data.get('role', 'candidate')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Use the user's actual role from the database
    actual_role = user.role

    # Admin can login with password (admin123)
    if actual_role == 'admin':
        if password != 'admin123':
            return jsonify({'error': 'Invalid credentials'}), 401
    else:
        # For candidate/recruiter, require OTP flow in production
        # For demo: allow login with any password if user exists
        if not user.is_verified and not password:
            return jsonify({'error': 'Please verify OTP first', 'require_otp': True}), 401

    profile = None
    if actual_role == 'candidate':
        candidate = Candidate.query.filter_by(user_id=user.id).first()
        profile = candidate.to_dict() if candidate else {'email': user.email}
    elif actual_role == 'recruiter':
        recruiter = Recruiter.query.filter_by(user_id=user.id).first()
        profile = recruiter.to_dict() if recruiter else {'email': user.email}
    elif actual_role == 'admin':
        profile = {'email': user.email, 'role': 'admin'}

    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': actual_role, 'email': user.email}
    )

    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'profile': profile,
        'role': actual_role
    }), 200


def get_current_user_profile():
    """Helper to get current user's profile based on role."""
    claims = get_jwt()
    role = claims.get('role')
    user_id = get_jwt_identity()

    if role == 'candidate':
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        return candidate.to_dict() if candidate else None
    elif role == 'recruiter':
        recruiter = Recruiter.query.filter_by(user_id=user_id).first()
        return recruiter.to_dict() if recruiter else None
    return None
