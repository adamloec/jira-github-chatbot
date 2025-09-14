from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)

# Import API routes
from api.routes import api_bp
from api.jira_routes import jira_bp
from api.github_routes import github_bp

app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(jira_bp, url_prefix='/api/jira')
app.register_blueprint(github_bp, url_prefix='/api/github')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'JIRA-GitHub Chatbot API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'api': '/api',
            'chat': '/api/chat'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting server on port {port}")
    print(f"Health check: http://localhost:{port}/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)