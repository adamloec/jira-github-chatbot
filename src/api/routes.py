from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os
import logging

from services.chatbot_service import ChatbotService

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Initialize chatbot service
chatbot_service = ChatbotService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@api_bp.route('/test')
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({'message': 'API is working!'})

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint for processing user queries"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        logger.info(f"Received query: {query}")
        
        # Process with chatbot service
        result = chatbot_service.chat(query)
        
        if result['success']:
            response = {
                'query': query,
                'response': result['response'],
                'tools_used': result.get('tools_used', []),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            return jsonify(response)
        else:
            return jsonify({
                'error': result['error'],
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }), 500
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@api_bp.route('/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'api_status': 'operational',
        'chatbot_configured': chatbot_service.api_key is not None,
        'endpoints': [
            {'path': '/test', 'method': 'GET'},
            {'path': '/chat', 'method': 'POST'},
            {'path': '/status', 'method': 'GET'}
        ]
    })