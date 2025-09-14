from flask import Blueprint, request, jsonify
from services.jira_service import JiraService
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
jira_bp = Blueprint('jira', __name__)

# Initialize JIRA service
jira_service = JiraService()

@jira_bp.route('/test-connection')
def test_jira_connection():
    """Test JIRA API connection"""
    result = jira_service.test_connection()
    
    if result['success']:
        return jsonify({
            'status': 'success',
            'message': 'JIRA connection successful',
            'user': result['data']
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'JIRA connection failed',
            'error': result['error']
        }), 400

@jira_bp.route('/user/<username>/activity')
def get_user_activity(username):
    """Get comprehensive user activity from JIRA"""
    result = jira_service.get_user_activity(username)
    
    if result['success']:
        return jsonify(result['data'])
    else:
        return jsonify({
            'error': result['error']
        }), 400