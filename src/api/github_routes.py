from flask import Blueprint, request, jsonify
from services.github_service import GitHubService
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
github_bp = Blueprint('github', __name__)

# Initialize GitHub service
github_service = GitHubService()

@github_bp.route('/test-connection')
def test_github_connection():
    """Test GitHub API connection"""
    result = github_service.test_connection()
    
    if result['success']:
        return jsonify({
            'status': 'success',
            'message': 'GitHub connection successful',
            'user': result['data']
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'GitHub connection failed',
            'error': result['error']
        }), 400

@github_bp.route('/user/<username>/activity')
def get_user_activity(username):
    """Get comprehensive GitHub activity for a user"""
    result = github_service.get_user_activity(username)
    
    if result['success']:
        return jsonify(result['data'])
    else:
        return jsonify({
            'error': result['error']
        }), 400