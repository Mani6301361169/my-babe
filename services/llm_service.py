"""
LLM Service - Handles integration with OpenAI or local Ollama
"""

import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMService:
    """Service for managing LLM interactions"""
    
    def __init__(self, config):
        """
        Initialize LLM service with configuration.
        
        Args:
            config: Flask app configuration object
        """
        self.config = config
        self.provider = config['LLM_PROVIDER']
        self.openai_api_key = config['OPENAI_API_KEY']
        self.openai_model = config['OPENAI_MODEL']
        self.ollama_base_url = config['OLLAMA_BASE_URL']
        self.ollama_model = config['OLLAMA_MODEL']
    
    def process_command(self, user_text: str, context: Dict = None, model: str = None) -> Dict[str, Any]:
        """
        Process a user command through the LLM.
        
        Args:
            user_text: The user's command or question
            context: Optional context from previous interactions
            model: Optional specific model to use
        
        Returns:
            Dictionary with success, response, and metadata
        """
        try:
            if self.provider == 'openai':
                return self._process_openai(user_text, context, model)
            elif self.provider == 'ollama':
                return self._process_ollama(user_text, context, model)
            else:
                return {
                    'success': False,
                    'error': f'Unknown LLM provider: {self.provider}'
                }
        except Exception as e:
            logger.error(f'Error processing command: {e}')
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_openai(self, user_text: str, context: Dict = None, model: str = None) -> Dict[str, Any]:
        """Process command using OpenAI API"""
        if not self.openai_api_key:
            return {
                'success': False,
                'error': 'OpenAI API key not configured'
            }
        
        try:
            import openai
            
            model = model or self.openai_model
            openai.api_key = self.openai_api_key
            
            # Build system prompt for JARVIS assistant
            system_prompt = """You are J.A.R.V.I.S, a sophisticated voice-activated AI assistant. 
You are helpful, witty, and professional. Respond concisely to commands and questions.
When asked to perform system actions (open apps, take screenshots, etc.), respond with 
instructions on what you're doing. Keep responses brief and conversational."""
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ]
            
            # Add context from previous interactions if provided
            if context and 'history' in context:
                for item in context['history'][-5:]:  # Last 5 interactions for context
                    messages.insert(1, {"role": "assistant", "content": item.get('response', '')})
                    messages.insert(1, {"role": "user", "content": item.get('user_input', '')})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            generated_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                'success': True,
                'response': generated_text,
                'command_type': self._classify_command(generated_text),
                'tokens_used': tokens_used,
                'model': model
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'OpenAI library not installed. Install with: pip install openai'
            }
        except Exception as e:
            logger.error(f'OpenAI API error: {e}')
            return {
                'success': False,
                'error': f'OpenAI API error: {str(e)}'
            }
    
    def _process_ollama(self, user_text: str, context: Dict = None, model: str = None) -> Dict[str, Any]:
        """Process command using local Ollama"""
        try:
            model = model or self.ollama_model
            
            # Build system prompt
            system_prompt = """You are J.A.R.V.I.S, a sophisticated voice-activated AI assistant. 
You are helpful, witty, and professional. Respond concisely to commands and questions."""
            
            # Prepare prompt with context
            prompt = user_text
            if context and 'history' in context:
                prompt = f"Previous context: {context['history'][-1]}\n\nUser: {user_text}"
            
            # Call Ollama API
            url = f"{self.ollama_base_url}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get('response', '')
            
            return {
                'success': True,
                'response': generated_text.strip(),
                'command_type': self._classify_command(generated_text),
                'model': model
            }
            
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': f'Cannot connect to Ollama at {self.ollama_base_url}. Is it running?'
            }
        except Exception as e:
            logger.error(f'Ollama error: {e}')
            return {
                'success': False,
                'error': f'Ollama error: {str(e)}'
            }
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check if the LLM service is operational.
        
        Returns:
            Dictionary with connection status and health message
        """
        try:
            if self.provider == 'openai':
                if not self.openai_api_key:
                    return {
                        'connected': False,
                        'status': 'error',
                        'message': 'OpenAI API key not configured'
                    }
                return {
                    'connected': True,
                    'status': 'operational',
                    'message': f'Connected to OpenAI ({self.openai_model})'
                }
            
            elif self.provider == 'ollama':
                try:
                    response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        return {
                            'connected': True,
                            'status': 'operational',
                            'message': f'Connected to Ollama ({self.ollama_model})'
                        }
                except:
                    pass
                
                return {
                    'connected': False,
                    'status': 'error',
                    'message': f'Cannot connect to Ollama at {self.ollama_base_url}'
                }
            
        except Exception as e:
            logger.error(f'Health check error: {e}')
            return {
                'connected': False,
                'status': 'error',
                'message': str(e)
            }
    
    def list_models(self) -> list:
        """
        Get list of available models.
        
        Returns:
            List of model names
        """
        try:
            if self.provider == 'openai':
                # Return common OpenAI models
                return ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview']
            
            elif self.provider == 'ollama':
                try:
                    response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        return [model['name'] for model in data.get('models', [])]
                except:
                    pass
                
                return [self.ollama_model]  # Return default if unable to fetch
            
        except Exception as e:
            logger.error(f'Error listing models: {e}')
            return []
    
    @staticmethod
    def _classify_command(response_text: str) -> str:
        """
        Classify the type of command based on the response.
        
        Args:
            response_text: The LLM response text
        
        Returns:
            Command type string
        """
        response_lower = response_text.lower()
        
        if any(word in response_lower for word in ['search', 'google', 'youtube', 'web']):
            return 'web_search'
        elif any(word in response_lower for word in ['open', 'close', 'click', 'screenshot', 'volume']):
            return 'system_control'
        elif any(word in response_lower for word in ['weather', 'time', 'date', 'news', 'wikipedia']):
            return 'information'
        else:
            return 'conversation'
