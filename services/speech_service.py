"""
Speech Recognition Service - Handles speech-to-text conversion
Supports both speech_recognition library and OpenAI Whisper API
"""

import logging
import base64
import io
from typing import Dict, Tuple, Optional
import speech_recognition as sr
from pathlib import Path

logger = logging.getLogger(__name__)


class SpeechRecognitionService:
    """Service for converting speech audio to text"""
    
    def __init__(self, config):
        """
        Initialize speech recognition service.
        
        Args:
            config: Flask app configuration
        """
        self.config = config
        self.recognizer = sr.Recognizer()
        self.wake_word = config['WAKE_WORD']
        self.timeout = config['SPEECH_RECOGNITION_TIMEOUT']
    
    def recognize_from_audio_data(
        self,
        audio_data: str,
        audio_format: str = 'wav',
        language: str = 'en-US'
    ) -> Dict[str, any]:
        """
        Recognize speech from base64-encoded audio data.
        
        Args:
            audio_data: Base64-encoded audio data
            audio_format: Audio format (wav, mp3, flac, ogg)
            language: Language code (e.g., 'en-US', 'es-ES')
        
        Returns:
            Dictionary with recognized text and confidence
        """
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            audio_io = io.BytesIO(audio_bytes)
            
            # Load audio into AudioData object
            if audio_format == 'wav':
                with sr.AudioFile(audio_io) as source:
                    audio = self.recognizer.record(source)
            else:
                logger.warning(f'Format {audio_format} may require conversion to WAV')
                with sr.AudioFile(audio_io) as source:
                    audio = self.recognizer.record(source)
            
            # Use Google Speech Recognition (free, no API key required)
            try:
                text = self.recognizer.recognize_google(
                    audio,
                    language=language
                )
                confidence = 0.95  # Google API doesn't return confidence
                
                return {
                    'success': True,
                    'text': text,
                    'confidence': confidence,
                    'wake_word_detected': self.wake_word.lower() in text.lower()
                }
                
            except sr.UnknownValueError:
                return {
                    'success': False,
                    'error': 'Could not understand audio',
                    'text': '',
                    'confidence': 0.0
                }
            except sr.RequestError as e:
                return {
                    'success': False,
                    'error': f'Speech recognition service error: {e}',
                    'text': '',
                    'confidence': 0.0
                }
            
        except Exception as e:
            logger.error(f'Error in speech recognition: {e}')
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def recognize_from_microphone(
        self,
        language: str = 'en-US',
        listen_duration: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Record audio from microphone and recognize speech.
        
        Args:
            language: Language code
            listen_duration: Duration to listen (seconds), uses config timeout if None
        
        Returns:
            Dictionary with recognized text
        """
        try:
            with sr.Microphone() as source:
                logger.info('Listening for audio...')
                
                # Adjust for background noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen with specified timeout
                timeout = listen_duration or self.timeout
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=language)
            
            return {
                'success': True,
                'text': text,
                'confidence': 0.95,
                'wake_word_detected': self.wake_word.lower() in text.lower(),
                'source': 'microphone'
            }
            
        except sr.UnknownValueError:
            logger.warning('Could not understand audio from microphone')
            return {
                'success': False,
                'error': 'Could not understand audio',
                'text': ''
            }
        except sr.RequestError as e:
            logger.error(f'Microphone recognition error: {e}')
            return {
                'success': False,
                'error': f'Error: {e}',
                'text': ''
            }
        except sr.WaitTimeoutError:
            logger.warning('Microphone listen timeout')
            return {
                'success': False,
                'error': 'Listening timeout - no speech detected',
                'text': ''
            }
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            return {
                'success': False,
                'error': str(e),
                'text': ''
            }
    
    def recognize_with_whisper(
        self,
        audio_data: str,
        language: str = 'en-US',
        api_key: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Use OpenAI Whisper API for higher accuracy speech recognition.
        Requires: pip install openai-whisper
        
        Args:
            audio_data: Base64-encoded audio data
            language: Language code
            api_key: OpenAI API key (uses config if not provided)
        
        Returns:
            Dictionary with recognized text and confidence
        """
        try:
            import openai
            
            api_key = api_key or self.config.get('OPENAI_API_KEY')
            if not api_key:
                return {
                    'success': False,
                    'error': 'OpenAI API key not configured for Whisper'
                }
            
            openai.api_key = api_key
            
            # Decode audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Call Whisper API
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_bytes,
                language=language.split('-')[0]  # Use language code only
            )
            
            text = response['text']
            
            return {
                'success': True,
                'text': text,
                'confidence': 0.98,  # Whisper is very accurate
                'wake_word_detected': self.wake_word.lower() in text.lower(),
                'engine': 'whisper'
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'openai-whisper not installed. Install: pip install openai-whisper'
            }
        except Exception as e:
            logger.error(f'Whisper API error: {e}')
            return {
                'success': False,
                'error': f'Whisper error: {str(e)}'
            }


class SpeechGenerationService:
    """Service for converting text to speech"""
    
    def __init__(self, config):
        """
        Initialize speech generation service.
        
        Args:
            config: Flask app configuration
        """
        self.config = config
        self.upload_folder = Path(config['UPLOAD_FOLDER'])
        self.upload_folder.mkdir(parents=True, exist_ok=True)
    
    def synthesize_speech(
        self,
        text: str,
        voice: str = 'default',
        rate: float = 1.0,
        language: str = 'en-US'
    ) -> Dict[str, any]:
        """
        Convert text to speech using pyttsx3 (offline, no API key needed).
        
        Args:
            text: Text to convert to speech
            voice: Voice selection (default, male, female)
            rate: Speech rate multiplier (0.5-2.0)
            language: Language code
        
        Returns:
            Dictionary with audio file path and duration
        """
        try:
            import pyttsx3
            import tempfile
            import os
            
            engine = pyttsx3.init()
            
            # Set voice
            voices = engine.getProperty('voices')
            if voice == 'male' and len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
            elif voice == 'female' and len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            
            # Set rate
            engine.setProperty('rate', 150 * rate)
            
            # Generate audio file
            audio_filename = f"speech_{int(len(text))}_{int(rate*10)}.wav"
            audio_path = self.upload_folder / audio_filename
            
            engine.save_to_file(text, str(audio_path))
            engine.runAndWait()
            
            # Estimate duration (rough: ~150 chars per minute at rate=1.0)
            duration_seconds = (len(text) / 150 / rate) * 60
            
            return {
                'success': True,
                'audio_path': str(audio_path),
                'audio_url': f'/api/speak/audio/{audio_filename}',
                'duration_seconds': duration_seconds,
                'engine': 'pyttsx3'
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'pyttsx3 not installed. Install: pip install pyttsx3'
            }
        except Exception as e:
            logger.error(f'TTS error: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def synthesize_speech_elevenlabs(
        self,
        text: str,
        voice_id: str = 'default',
        rate: float = 1.0,
        api_key: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Use ElevenLabs API for high-quality text-to-speech.
        Requires: pip install elevenlabs
        
        Args:
            text: Text to convert
            voice_id: ElevenLabs voice ID
            rate: Speech rate
            api_key: ElevenLabs API key
        
        Returns:
            Dictionary with audio URL
        """
        try:
            from elevenlabs import client, VoiceSettings
            import os
            
            api_key = api_key or os.environ.get('ELEVENLABS_API_KEY')
            if not api_key:
                return {
                    'success': False,
                    'error': 'ElevenLabs API key not configured'
                }
            
            client.api_key = api_key
            
            # Generate speech
            audio_data = client.generate(
                text=text,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )
            
            # Save audio
            audio_filename = f"elevenlabs_{hash(text)}.mp3"
            audio_path = self.upload_folder / audio_filename
            
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            
            return {
                'success': True,
                'audio_path': str(audio_path),
                'audio_url': f'/api/speak/audio/{audio_filename}',
                'engine': 'elevenlabs'
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'elevenlabs not installed. Install: pip install elevenlabs'
            }
        except Exception as e:
            logger.error(f'ElevenLabs error: {e}')
            return {
                'success': False,
                'error': str(e)
            }
