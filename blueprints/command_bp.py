"""
Command Blueprint - Handles command processing and LLM integration
Routes:
  POST /api/command - Process user command through LLM
  GET /api/command/status - Get LLM service status
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import json
import re
from datetime import datetime

bp = Blueprint('command', __name__, url_prefix='/api/command')
logger = logging.getLogger(__name__)

# Import LLM handlers
from services.llm_service import LLMService
from services.system_control_service import SystemControlService
from services.task_scheduler_service import TaskSchedulerService

system_service = SystemControlService()


def execute_local_command(user_text):
    """Execute supported local actions without requiring an LLM."""
    normalized = user_text.lower().strip()

    match = re.fullmatch(r"(open|close)\s+(?:the\s+)?(.+)", normalized)
    if match:
        action, app = match.groups()
        result = (system_service.open_application(app)
                  if action == 'open'
                  else system_service.close_application(app))
        return result if result.get('success') else None

    if re.fullmatch(r"(take\s+)?a?\s*screenshot", normalized):
        result = system_service.take_screenshot()
        return result if result.get('success') else None

    match = re.fullmatch(r"remind me in (\d+) seconds? to (.+)", normalized)
    if match:
        delay_seconds, message = match.groups()
        scheduler = TaskSchedulerService()
        scheduler.start()
        result = scheduler.add_reminder(message, delay_seconds=int(delay_seconds))
        return result if result.get('success') else None

    return None


@bp.route('', methods=['POST'])
def command():
    """
    Process user text command through LLM and return generated response.
    
    Expected JSON payload:
    {
        "text": "User command or question",
        "context": {} (optional, context from previous commands),
        "model": "gpt-3.5-turbo" (optional, override default)
    }
    
    Returns:
    {
        "success": true,
        "response": "Generated response from LLM",
        "command_type": "web_search|system_control|information|conversation",
        "metadata": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'Missing text field'}), 400
        
        user_text = data.get('text', '').strip()
        if not user_text:
            return jsonify({'success': False, 'error': 'Text cannot be empty'}), 400
        
        context = data.get('context', {})
        model = data.get('model', current_app.config['OPENAI_MODEL'])
        
        logger.info(f'Processing command: "{user_text}"')

        local_result = execute_local_command(user_text)
        if local_result:
            return jsonify({
                'success': True,
                'response': local_result.get('message', 'Command completed.'),
                'command_type': 'system_control',
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'user_input': user_text,
                    'local_action': True
                }
            }), 200
        
        # Initialize LLM service
        llm_service = LLMService(current_app.config)
        
        # Process command through LLM
        result = llm_service.process_command(user_text, context, model)
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify({
            'success': True,
            'response': result['response'],
            'command_type': result.get('command_type', 'conversation'),
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_text,
                'model': model,
                'tokens_used': result.get('tokens_used', 0)
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error in command endpoint: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/status', methods=['GET'])
def status():
    """
    Get LLM service status and configuration.
    
    Returns:
    {
        "success": true,
        "provider": "openai|ollama",
        "model": "gpt-3.5-turbo",
        "connected": true,
        "health": "operational"
    }
    """
    try:
        llm_service = LLMService(current_app.config)
        health = llm_service.check_health()
        
        return jsonify({
            'success': True,
            'provider': current_app.config['LLM_PROVIDER'],
            'model': (current_app.config['OPENAI_MODEL'] 
                     if current_app.config['LLM_PROVIDER'] == 'openai'
                     else current_app.config['OLLAMA_MODEL']),
            'connected': health['connected'],
            'health': health['status'],
            'message': health['message']
        }), 200
        
    except Exception as e:
        logger.error(f'Error checking LLM status: {e}')
        return jsonify({
            'success': False,
            'error': str(e),
            'health': 'error'
        }), 500


@bp.route('/models', methods=['GET'])
def models():
    """
    Get list of available LLM models.
    
    Returns:
    {
        "success": true,
        "models": ["gpt-3.5-turbo", "gpt-4", ...],
        "current": "gpt-3.5-turbo"
    }
    """
    try:
        llm_service = LLMService(current_app.config)
        available_models = llm_service.list_models()
        
        return jsonify({
            'success': True,
            'models': available_models,
            'current': (current_app.config['OPENAI_MODEL'] 
                       if current_app.config['LLM_PROVIDER'] == 'openai'
                       else current_app.config['OLLAMA_MODEL']),
            'provider': current_app.config['LLM_PROVIDER']
        }), 200
        
    except Exception as e:
        logger.error(f'Error listing models: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/history', methods=['GET'])
def history():
    """
    Get command history (for conversation context).
    
    Query parameters:
    - limit: Max number of commands to return (default: 10)
    - offset: Pagination offset (default: 0)
    
    Returns:
    {
        "success": true,
        "history": [
            {"timestamp": "2024-01-01T12:00:00", "user_input": "...", "response": "..."},
            ...
        ],
        "total": 42
    }
    """
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # TODO: Implement history storage and retrieval from database
    # For now, return empty history
    return jsonify({
        'success': True,
        'history': [],
        'total': 0,
        'limit': limit,
        'offset': offset
    }), 200
