"""
Configuration settings for JARVIS Flask application
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jarvis-secret-key-change-in-production')
    JSON_SORT_KEYS = False
    
    # LLM Configuration
    LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')  # 'openai' or 'ollama'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_MODEL = 'gpt-3.5-turbo'
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = 'mistral'
    
    # Speech Recognition
    SPEECH_RECOGNITION_TIMEOUT = 10  # seconds
    WAKE_WORD = 'jarvis'
    
    # File paths
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_AUDIO_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg'}
    MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25 MB
    
    # Background tasks
    SCHEDULER_TIMEZONE = 'UTC'
    SCHEDULER_POOL_SIZE = 10


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    ENV = 'production'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
