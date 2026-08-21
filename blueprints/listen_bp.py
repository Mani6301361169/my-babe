"""
Listen Blueprint - Handles audio input and speech-to-text
Routes:
  POST /api/listen - Receive audio file and transcribe to text
  GET /api/listen/status - Check listening status
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from services.speech_service import SpeechRecognitionService

bp = Blueprint('listen', __name__, url_prefix='/api/listen')
logger = logging.getLogger(__name__)


@bp.route('', methods=['POST'])
def listen():
    """
    Receive audio file and transcribe it to text.
    
    Expected JSON payload:
    {
        "audio_data": "<base64_encoded_audio>",
        "format": "wav|mp3|flac|ogg" (optional, default: wav),
        "language": "en-US" (optional, default: en-US),
        "engine": "google|whisper" (optional, default: google)
    }
    
    Returns:
    {
        "success": true,
        "text": "transcribed text",
        "confidence": 0.95,
        "wake_word_detected": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'audio_data' not in data:
            return jsonify({'success': False, 'error': 'Missing audio_data'}), 400
        
        audio_data = data.get('audio_data')
        audio_format = data.get('format', 'wav')
        language = data.get('language', 'en-US')
        engine = data.get('engine', 'google')
        
        # Validate format
        if audio_format not in current_app.config['ALLOWED_AUDIO_EXTENSIONS']:
            return jsonify({
                'success': False,
                'error': f"Unsupported format. Allowed: {current_app.config['ALLOWED_AUDIO_EXTENSIONS']}"
            }), 400
        
        # Initialize speech recognition service
        speech_service = SpeechRecognitionService(current_app.config)
        
        logger.info(f'Transcribing audio: format={audio_format}, language={language}, engine={engine}')
        
        # Use appropriate recognition engine
        if engine == 'whisper':
            result = speech_service.recognize_with_whisper(
                audio_data,
                language=language,
                api_key=current_app.config.get('OPENAI_API_KEY')
            )
        else:
            # Default to Google Speech Recognition
            result = speech_service.recognize_from_audio_data(
                audio_data,
                audio_format=audio_format,
                language=language
            )
        
        return jsonify(result), (200 if result.get('success') else 400)
        
    except Exception as e:
        logger.error(f'Error in listen endpoint: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/status', methods=['GET'])
def status():
    """
    Get listening status and configuration.
    
    Returns:
    {
        "listening": true|false,
        "wake_word": "jarvis",
        "supported_formats": ["wav", "mp3", "flac", "ogg"]
    }
    """
    return jsonify({
        'listening': True,
        'wake_word': current_app.config['WAKE_WORD'],
        'supported_formats': list(current_app.config['ALLOWED_AUDIO_EXTENSIONS']),
        'timeout_seconds': current_app.config['SPEECH_RECOGNITION_TIMEOUT']
    }), 200
