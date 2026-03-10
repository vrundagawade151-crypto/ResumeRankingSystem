"""Recruiter-specific routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.db import db
from models.recruiter import Recruiter

recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/api/recruiter')


@recruiter_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get recruiter profile."""
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    recruiter = Recruiter.query.filter_by(user_id=claims.get('sub')).first()
    if not recruiter:
        return jsonify({'error': 'Profile not found'}), 404
    return jsonify({'profile': recruiter.to_dict()}), 200


@recruiter_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update recruiter profile."""
    claims = get_jwt()
    if claims.get('role') != 'recruiter':
        return jsonify({'error': 'Unauthorized'}), 403

    recruiter = Recruiter.query.filter_by(user_id=claims.get('sub')).first()
    if not recruiter:
        return jsonify({'error': 'Profile not found'}), 404

    data = request.get_json()
    for key in ['name', 'company_name', 'phone']:
        if key in data:
            setattr(recruiter, key, data[key])
    db.session.commit()
    return jsonify({'profile': recruiter.to_dict(), 'message': 'Profile updated'}), 200
