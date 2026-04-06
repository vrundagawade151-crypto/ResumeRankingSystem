from flask import Blueprint, request, jsonify
import jwt
from config import Config
from database import db
from models.user import User

recruiter_bp = Blueprint('recruiter', __name__)

@recruiter_bp.route('/recruiter/profile', methods=['GET'])
def get_recruiter_profile():
    """Get recruiter profile"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = data.get('user_id')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'company': user.company or ''
        }), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401

@recruiter_bp.route('/recruiter/profile', methods=['PUT'])
def update_recruiter_profile():
    """Update recruiter profile"""
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Authentication required'}), 401
    
    try:
        token = token.replace('Bearer ', '')
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user_id = data.get('user_id')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        update_data = request.get_json()
        
        if 'username' in update_data:
            user.username = update_data['username']
        if 'company' in update_data:
            user.company = update_data['company']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'company': user.company or ''
            }
        }), 200
    except:
        return jsonify({'message': 'Invalid token'}), 401
