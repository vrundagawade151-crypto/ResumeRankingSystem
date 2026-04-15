from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import random
from datetime import datetime, timedelta
from functools import wraps
from config import Config
from database import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

# In-memory OTP storage (temporary, expires in 5 minutes)
otp_store = {}  # email -> {otp, expiry, role, name, company}

SECRET_KEY = Config.SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/auth/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to user's email"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('role'):
        return jsonify({'message': 'Email and role are required'}), 400
    
    email = data['email'].strip().lower()
    role = data['role'].strip().lower()
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP with 5-minute expiry (use lowercase email for consistency)
    otp_store[email] = {
        'otp': otp,
        'expiry': datetime.utcnow() + timedelta(minutes=5),
        'role': role,
        'name': data.get('name', ''),
        'company': data.get('company', '')
    }
    
    print(f"OTP stored for {email}: {otp}")
    
    # In production, send via email/SMS
    # For demo, OTP is returned in response
    return jsonify({
        'message': 'OTP sent successfully',
        'otp': otp,  # Demo only - remove in production!
        'email': email,
        'role': role
    }), 200

@auth_bp.route('/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and login/register user"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('otp') or not data.get('role'):
        return jsonify({'message': 'Email, OTP, and role are required'}), 400
    
    email = data['email'].strip().lower()
    otp = data['otp'].strip()
    role = data['role'].strip().lower()
    
    print(f"Verifying OTP for email: {email}, role: {role}")
    
    # Check if OTP exists and is valid
    stored_emails = [k.strip().lower() for k in otp_store.keys()]
    if email not in stored_emails:
        print(f"Email not found. Looking for: {email}")
        print(f"Available emails: {stored_emails}")
        return jsonify({'message': 'OTP not found or expired. Please request a new OTP.'}), 400
    
    # Find the matching email in store
    actual_email = None
    for k in otp_store.keys():
        if k.strip().lower() == email:
            actual_email = k
            break
    
    if not actual_email:
        return jsonify({'message': 'OTP not found or expired. Please request a new OTP.'}), 400
    
    otp_data = otp_store[actual_email]
    
    # Check if OTP is expired first
    if datetime.utcnow() > otp_data['expiry']:
        del otp_store[actual_email]
        return jsonify({'message': 'OTP expired. Please request a new OTP.'}), 400
    
    # Verify OTP
    if otp_data['otp'] != otp:
        print(f"OTP mismatch: stored={otp_data['otp']}, provided={otp}")
        return jsonify({'message': 'Invalid OTP. Please check and try again.'}), 400
    
    # Verify role
    if otp_data['role'] != role:
        print(f"Role mismatch: stored={otp_data['role']}, provided={role}")
        return jsonify({'message': 'Role mismatch. Please request OTP for the correct role.'}), 400
    
    # Find or create user in database
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Create new user
        user = User(
            username=otp_data.get('name', email.split('@')[0]),
            email=email,
            password_hash=None,  # No password for OTP users
            is_admin=False,
            role=role
        )
        db.session.add(user)
        db.session.commit()
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, SECRET_KEY, algorithm='HS256')
    
    # Clean up OTP
    del otp_store[email]
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role
        },
        'profile': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role
        },
        'role': role
    }), 200

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Direct admin login with email and password"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required'}), 401
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash or '', data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'role': 'admin',
        'exp': datetime.utcnow() + timedelta(days=1)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': 'admin'
        }
    }), 200

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user with username, email, and password"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'User already exists'}), 409
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        is_admin=data.get('is_admin', False),
        role=data.get('role', 'candidate')
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user_id': user.id}), 201

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    }), 200

@auth_bp.route('/auth/profile/resume', methods=['POST'])
@token_required
def upload_candidate_resume(current_user):
    import os
    from werkzeug.utils import secure_filename
    
    if 'resume' not in request.files:
        return jsonify({'message': 'No resume file provided'}), 400
        
    resume_file = request.files['resume']
    if resume_file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    os.makedirs('uploads', exist_ok=True)
    filename = secure_filename(resume_file.filename)
    resume_path = os.path.join('uploads', f"user_{current_user.id}_{filename}")
    resume_file.save(resume_path)
    
    # Mock extracted details based on the resume
    extracted_details = {
        'skills': ['Python', 'React', 'Node.js', 'System Design'],
        'education': [
            {
                'degree': 'M.S. Computer Science',
                'university': 'Tech Innovations University',
                'year': '2023'
            }
        ],
        'experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'Advanced AI Labs',
                'duration': '2021 - Present',
                'location': 'Remote',
                'description': 'Developed scalable backend services and AI-driven applications.'
            }
        ]
    }
    
    return jsonify({
        'message': 'Resume uploaded successfully',
        'resume_path': resume_path,
        'extracted_details': extracted_details
    }), 200

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    return jsonify({'message': 'Logged out successfully'}), 200

