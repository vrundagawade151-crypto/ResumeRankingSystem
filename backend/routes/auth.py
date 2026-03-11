from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import random
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# In-memory storage for demo (replace with database in production)
users = {}
otp_store = {}  # email -> {otp, expiry, role}

SECRET_KEY = 'your-secret-key-here'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = users.get(data['user_id'])
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
    
    email = data['email']
    role = data['role']  # 'candidate', 'recruiter', or 'admin'
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    
    # Store OTP with 5-minute expiry
    otp_store[email] = {
        'otp': otp,
        'expiry': datetime.utcnow() + timedelta(minutes=5),
        'role': role,
        'name': data.get('name', ''),
        'company': data.get('company', '')
    }
    
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
    
    email = data['email']
    otp = data['otp']
    role = data['role']
    
    # Check if OTP exists and is valid
    if email not in otp_store:
        return jsonify({'message': 'OTP not requested or expired'}), 400
    
    otp_data = otp_store[email]
    
    # Verify OTP and role match
    if otp_data['otp'] != otp or otp_data['role'] != role:
        return jsonify({'message': 'Invalid OTP'}), 400
    
    # Check if OTP is expired
    if datetime.utcnow() > otp_data['expiry']:
        del otp_store[email]
        return jsonify({'message': 'OTP expired'}), 400
    
    # Find or create user
    user = None
    for u in users.values():
        if u['email'] == email:
            user = u
            break
    
    if not user:
        # Create new user
        user_id = len(users) + 1
        users[user_id] = {
            'id': user_id,
            'username': otp_data.get('name', email.split('@')[0]),
            'email': email,
            'password_hash': None,  # No password for OTP users
            'role': role,
            'is_admin': False,
            'created_at': datetime.utcnow()
        }
        user = users[user_id]
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=1)
    }, SECRET_KEY, algorithm='HS256')
    
    # Clean up OTP
    del otp_store[email]
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': role
        },
        'profile': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
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
    
    user = None
    for u in users.values():
        if u['email'] == data['email']:
            user = u
            break
    
    if not user or not check_password_hash(user.get('password_hash', ''), data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'role': user.get('role', 'admin'),
        'exp': datetime.utcnow() + timedelta(days=1)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user.get('role', 'admin')
        }
    }), 200

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user with username, email, and password"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if user already exists
    for u in users.values():
        if u['email'] == data['email']:
            return jsonify({'message': 'User already exists'}), 409
    
    user_id = len(users) + 1
    users[user_id] = {
        'id': user_id,
        'username': data['username'],
        'email': data['email'],
        'password_hash': generate_password_hash(data['password']),
        'role': data.get('role', 'candidate'),
        'is_admin': data.get('is_admin', False),
        'created_at': datetime.utcnow()
    }
    
    return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'id': current_user['id'],
        'username': current_user['username'],
        'email': current_user['email'],
        'role': current_user.get('role', 'candidate')
    }), 200
