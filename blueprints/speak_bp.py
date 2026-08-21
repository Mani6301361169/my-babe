"""
Speak Blueprint - Handles text-to-speech generation
Routes:
  POST /api/speak - Convert text to speech audio
  GET /api/speak/voices - Get available voices
"""

from flask import Blueprint, request, jsonify, current_app, send_file
import logging
from services.speech_service import SpeechGenerationService
from pathlib import Path

bp = Blueprint('speak', __name__, url_prefix='/api/speak')
logger = logging.getLogger(__name__)


@bp.route('', methods=['POST'])
def speak():
    """
    Convert text to speech and return audio file.
    
    Expected JSON payload:
    {
        "text": "Text to convert to speech",
        "voice": "default" (optional),
        "rate": 1.0 (optional, speed: 0.5-2.0),
        "language": "en-US" (optional),
        "engine": "pyttsx3|elevenlabs" (optional, default: pyttsx3)
    }
    
    Returns:
    {
        "success": true,
        "audio_url": "/api/speak/audio/12345",
        "duration_seconds": 3.5,
        "engine": "pyttsx3"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'Missing text field'}), 400
        
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'success': False, 'error': 'Text cannot be empty'}), 400
        
        voice = data.get('voice', 'default')
        rate = data.get('rate', 1.0)
        language = data.get('language', 'en-US')
        engine = data.get('engine', 'pyttsx3')
        
        # Validate rate
        if not (0.5 <= rate <= 2.0):
            return jsonify({'success': False, 'error': 'Rate must be between 0.5 and 2.0'}), 400
        
        logger.info(f'TTS request: text="{text[:50]}...", engine={engine}, rate={rate}')
        
        # Initialize speech generation service
        speech_service = SpeechGenerationService(current_app.config)
        
        # Use appropriate TTS engine
        if engine == 'elevenlabs':
            result = speech_service.synthesize_speech_elevenlabs(
                text,
                voice_id=voice,
                rate=rate,
                api_key=current_app.config.get('ELEVENLABS_API_KEY')
            )
        else:
            # Default to pyttsx3
            result = speech_service.synthesize_speech(
                text,
                voice=voice,
                rate=rate,
                language=language
            )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f'Error in speak endpoint: {e}')
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/voices', methods=['GET'])
def voices():
    """
    Get available voices for text-to-speech.
    
    Returns:
    {
        "success": true,
        "voices": ["default", "male", "female", ...]
    }
    """
    return jsonify({
        'success': True,
        'voices': ['default', 'male', 'female'],
        'languages': ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE']
    }), 200


@bp.route('/audio/<audio_id>', methods=['GET'])
def get_audio(audio_id):
    """
    Retrieve previously generated audio file.
    
    Args:
        audio_id: ID of the audio file
    
    Returns:
        Audio file stream or 404 if not found
    """
    # TODO: Implement audio retrieval from storage
    return jsonify({'success': False, 'error': 'Audio not found'}), 404
