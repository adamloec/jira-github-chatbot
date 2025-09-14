from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
from datetime import datetime

# Add src to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)

try:
    from api.routes import api_bp
    from api.jira_routes import jira_bp
    from api.github_routes import github_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(jira_bp, url_prefix='/api/jira')
    app.register_blueprint(github_bp, url_prefix='/api/github')
    print("All blueprints registered successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

@app.route('/')
def home():
    """Serve the web interface"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting server on port {port}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"Web interface: http://localhost:{port}/")
    
    app.run(host='0.0.0.0', port=port, debug=debug)