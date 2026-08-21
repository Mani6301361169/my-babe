"""
J.A.R.V.I.S Web Application - Application Factory
Modular Flask application with blueprints for a voice-activated AI assistant
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """
    Application factory pattern - creates and configures the Flask app.
    
    Args:
        config_name: Configuration environment ('development' or 'production')
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, static_folder='static', template_folder='templates')
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Enable CORS for browser requests
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from blueprints import listen_bp, speak_bp, command_bp, system_bp, tasks_bp
    
    app.register_blueprint(listen_bp.bp)
    app.register_blueprint(speak_bp.bp)
    app.register_blueprint(command_bp.bp)
    app.register_blueprint(system_bp.bp)
    app.register_blueprint(tasks_bp.bp)
    
    # Web UI Routes
    @app.route('/')
    def index():
        """Serve the main web UI"""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'service': 'J.A.R.V.I.S'}), 200
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request', 'message': str(error)}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found', 'message': 'Endpoint does not exist'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f'Server error: {error}')
        return {'error': 'Internal server error'}, 500
    
    logger.info(f'JARVIS Flask app created in {config_name} mode')
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='127.0.0.1', port=5000)
