"""
System Control Blueprint - Handles desktop control requests
Routes:
  POST /api/system/app - Open/close applications
  POST /api/system/screenshot - Take screenshot
  POST /api/system/clipboard - Read/write clipboard
  POST /api/system/control - Window/media control
  GET /api/system/info - Get system information
"""

from flask import Blueprint, request, jsonify
import logging
from services.system_control_service import SystemControlService

bp = Blueprint('system', __name__, url_prefix='/api/system')
logger = logging.getLogger(__name__)
system_service = SystemControlService()


@bp.route('/app', methods=['POST'])
def control_app():
    """
    Open or close an application.
    
    Expected JSON:
    {
        "action": "open|close",
        "app": "chrome|notepad|vscode|..."
    }
    """
    try:
        data = request.get_json()
        if not data or 'action' not in data or 'app' not in data:
            return jsonify({'success': False, 'error': 'Missing action or app'}), 400
        
        action = data['action'].lower()
        app_name = data['app'].lower()
        
        if action == 'open':
            result = system_service.open_application(app_name)
        elif action == 'close':
            result = system_service.close_application(app_name)
        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error in app control: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/screenshot', methods=['POST'])
def take_screenshot():
    """
    Take a screenshot.
    
    Returns:
    {
        "success": true,
        "path": "/path/to/screenshot.png"
    }
    """
    try:
        result = system_service.take_screenshot()
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        logger.error(f'Error taking screenshot: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/clipboard', methods=['POST', 'GET'])
def clipboard_control():
    """
    Read or write clipboard.
    
    POST - Write text to clipboard:
    {
        "text": "Text to copy"
    }
    
    GET - Read clipboard content
    """
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({'success': False, 'error': 'Missing text'}), 400
            result = system_service.write_clipboard(data['text'])
        else:
            result = system_service.read_clipboard()
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error in clipboard control: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/input', methods=['POST'])
def input_control():
    """
    Keyboard and mouse control.
    
    Expected JSON:
    {
        "type": "type|press|click|scroll",
        "data": {...}
    }
    
    Examples:
    - Type: {"type": "type", "data": {"text": "Hello"}}
    - Press key: {"type": "press", "data": {"key": "enter"}}
    - Click: {"type": "click", "data": {"x": 100, "y": 200, "button": "left"}}
    - Scroll: {"type": "scroll", "data": {"direction": "down", "amount": 3}}
    """
    try:
        data = request.get_json()
        if not data or 'type' not in data:
            return jsonify({'success': False, 'error': 'Missing type'}), 400
        
        control_type = data['type'].lower()
        control_data = data.get('data', {})
        
        if control_type == 'type':
            result = system_service.type_text(control_data.get('text', ''))
        elif control_type == 'press':
            result = system_service.press_key(control_data.get('key', ''))
        elif control_type == 'click':
            result = system_service.click(
                control_data.get('x', 0),
                control_data.get('y', 0),
                control_data.get('button', 'left')
            )
        elif control_type == 'scroll':
            result = system_service.scroll(
                control_data.get('direction', 'down'),
                control_data.get('amount', 3)
            )
        else:
            return jsonify({'success': False, 'error': 'Invalid control type'}), 400
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error in input control: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/window', methods=['POST'])
def window_control():
    """
    Window control (minimize, maximize, close).
    
    Expected JSON:
    {
        "action": "minimize|maximize|close"
    }
    """
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'success': False, 'error': 'Missing action'}), 400
        
        action = data['action'].lower()
        
        if action == 'minimize':
            result = system_service.minimize_window()
        elif action == 'maximize':
            result = system_service.maximize_window()
        elif action == 'close':
            result = system_service.close_window()
        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error in window control: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/audio', methods=['POST'])
def audio_control():
    """
    Audio control (volume, mute/unmute).
    
    Expected JSON:
    {
        "action": "volume|mute|unmute",
        "level": 50 (for volume action)
    }
    """
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'success': False, 'error': 'Missing action'}), 400
        
        action = data['action'].lower()
        
        if action == 'volume':
            level = data.get('level', 50)
            result = system_service.set_volume(level)
        elif action == 'mute':
            result = system_service.mute_audio()
        elif action == 'unmute':
            result = system_service.unmute_audio()
        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error in audio control: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/info', methods=['GET'])
def system_info():
    """
    Get system information.
    
    Returns:
    {
        "success": true,
        "data": {
            "cpu_percent": 45.2,
            "memory_percent": 62.5,
            "memory_available_gb": 4.2,
            "memory_total_gb": 16,
            "disk_percent": 35.1,
            "disk_free_gb": 250,
            "disk_total_gb": 500,
            "battery_percent": 85,
            "battery_plugged": true
        }
    }
    """
    try:
        result = system_service.get_system_info()
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        logger.error(f'Error getting system info: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/control', methods=['POST'])
def system_control():
    """
    System-level control (lock, shutdown, restart).
    
    Expected JSON:
    {
        "action": "lock|shutdown|restart",
        "confirm": true (required for shutdown/restart)
    }
    
    WARNING: Shutdown and restart actions are dangerous and require confirmation.
    """
    try:
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'success': False, 'error': 'Missing action'}), 400
        
        action = data['action'].lower()
        confirm = data.get('confirm', False)
        
        if action == 'lock':
            result = system_service.lock_screen()
        elif action == 'shutdown':
            result = system_service.shutdown(confirm=confirm)
        elif action == 'restart':
            result = system_service.restart(confirm=confirm)
        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        return jsonify(result), (200 if result['success'] else 400)
        
    except Exception as e:
        logger.error(f'Error in system control: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500
