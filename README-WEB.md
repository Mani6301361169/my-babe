# J.A.R.V.I.S Web - Voice-Activated AI Assistant

A modern, futuristic web-based voice-activated AI assistant with an Arc Reactor-inspired UI. Built with Flask, featuring speech recognition, text-to-speech, LLM integration, and system control capabilities.

## Features

### 🎤 Phase 1: Architecture & Backend
- **Modular Flask Architecture** - Blueprints-based design for scalability
- **Application Factory Pattern** - Clean configuration management
- **LLM Integration** - Support for OpenAI GPT and local Ollama
- **RESTful API** - Comprehensive endpoints for all features

### 🎙️ Phase 2: Speech Processing
- **Speech Recognition** - Google Speech API (free) or OpenAI Whisper
- **Text-to-Speech** - pyttsx3 (offline) or ElevenLabs API
- **Real-time Transcription** - Live audio input processing
- **Multiple Languages** - Support for 100+ languages

### 🖥️ Phase 3: System Control
- **Application Launcher** - Open/close desktop applications
- **Desktop Control** - Screenshots, clipboard, keyboard/mouse control
- **Window Management** - Minimize, maximize, close windows
- **Audio Control** - Volume, mute/unmute
- **System Info** - CPU, memory, disk, battery monitoring
- **Background Tasks** - Reminders, alarms, scheduled tasks with APScheduler

### 🎨 Phase 4: Web UI
- **Arc Reactor Design** - Animated futuristic interface
- **Responsive Layout** - Works on desktop and tablets
- **Real-time Updates** - Live status and system monitoring
- **Settings Panel** - Customize LLM, speech engines, themes
- **Chat History** - Conversation tracking and replay

## Quick Start

### Prerequisites
- Python 3.8+
- pip
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Installation

1. **Navigate to the project directory:**
```bash
cd "C:\Users\LENOVO\Downloads\J.A.R.V.I.S-master\J.A.R.V.I.S-master"
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements-web.txt
```

4. **Copy configuration template:**
```bash
copy .env.example .env
```

5. **Configure `.env` file:**
```
FLASK_ENV=development
FLASK_DEBUG=True
LLM_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here
```

6. **Run the application:**
```bash
python app.py
```

7. **Open in browser:**
```
http://localhost:5000
```

## Configuration

### Environment Variables (.env)

```env
# Flask
FLASK_ENV=development          # development or production
FLASK_DEBUG=True

# LLM Provider
LLM_PROVIDER=openai           # openai or ollama
OPENAI_API_KEY=sk-...         # Your OpenAI API key
OPENAI_MODEL=gpt-3.5-turbo    # Model to use

# Ollama (if using local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral

# Speech Settings
SPEECH_RECOGNITION_TIMEOUT=10
WAKE_WORD=jarvis

# Server
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

## API Endpoints

### Command Processing
```
POST /api/command              - Process user command via LLM
GET  /api/command/status       - Check LLM service status
GET  /api/command/models       - List available models
GET  /api/command/history      - Get command history
```

### Speech Recognition
```
POST /api/listen               - Transcribe audio file
GET  /api/listen/status        - Get listening status
```

### Text-to-Speech
```
POST /api/speak                - Generate speech from text
GET  /api/speak/voices         - List available voices
GET  /api/speak/audio/{id}     - Get audio file
```

### System Control
```
POST /api/system/app           - Open/close applications
POST /api/system/screenshot    - Take screenshot
POST /api/system/clipboard     - Read/write clipboard
POST /api/system/input         - Keyboard/mouse control
POST /api/system/window        - Window control
POST /api/system/audio         - Audio control
GET  /api/system/info          - Get system information
POST /api/system/control       - System control (lock, shutdown, restart)
```

### Tasks & Scheduling
```
POST /api/tasks/reminder              - Create reminder
POST /api/tasks/reminder/recurring    - Create recurring reminder
POST /api/tasks/alarm                 - Create alarm
POST /api/tasks/alarm/recurring       - Create recurring alarm
GET  /api/tasks/jobs                  - List scheduled jobs
DELETE /api/tasks/jobs/{job_id}       - Remove job
POST /api/tasks/jobs/{job_id}/pause   - Pause job
POST /api/tasks/jobs/{job_id}/resume  - Resume job
```

## Usage Examples

### Using the Web UI
1. Click the **Listen** button to start voice input
2. Speak your command (e.g., "What's the weather?", "Open Chrome", "Set a reminder")
3. Watch the Arc Reactor respond and see the assistant's reply
4. Access settings via the ⚙️ button to customize behavior

### API Examples

#### Send a voice command
```bash
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"text":"What is the weather today?"}'
```

#### Create a reminder
```bash
curl -X POST http://localhost:5000/api/tasks/reminder \
  -H "Content-Type: application/json" \
  -d '{
    "message":"Meeting in 30 minutes",
    "delay_seconds":1800
  }'
```

#### Get system information
```bash
curl http://localhost:5000/api/system/info
```

#### Open an application
```bash
curl -X POST http://localhost:5000/api/system/app \
  -H "Content-Type: application/json" \
  -d '{"action":"open","app":"chrome"}'
```

## Architecture

### Project Structure
```
J.A.R.V.I.S-master/
├── app.py                 # Application factory
├── config.py             # Configuration management
├── requirements-web.txt  # Dependencies
├── .env.example         # Configuration template
│
├── blueprints/          # API endpoints
│   ├── __init__.py
│   ├── listen_bp.py    # Speech recognition
│   ├── speak_bp.py     # Text-to-speech
│   ├── command_bp.py   # LLM commands
│   ├── system_bp.py    # System control
│   └── tasks_bp.py     # Task scheduling
│
├── services/           # Business logic
│   ├── __init__.py
│   ├── llm_service.py              # LLM integration
│   ├── speech_service.py           # Speech processing
│   ├── system_control_service.py   # System control
│   └── task_scheduler_service.py   # Task scheduling
│
├── templates/          # HTML templates
│   └── index.html     # Main UI
│
└── static/            # Frontend assets
    ├── css/
    │   └── style.css  # Futuristic styling
    └── js/
        └── main.js    # UI logic & API calls
```

### Technology Stack
- **Backend**: Flask, Flask-CORS
- **LLM**: OpenAI API, Ollama
- **Speech**: speech_recognition, pyttsx3, OpenAI Whisper
- **Scheduling**: APScheduler
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla, no frameworks)
- **System Control**: psutil, PyAutoGUI, pyperclip

## Advanced Features

### Custom LLM Integration
Edit `services/llm_service.py` to add support for other LLM providers (Anthropic Claude, Cohere, etc.)

### Wake Word Detection
Implement continuous wake word listening:
```javascript
// Listen for "Hey Jarvis" without manual button click
// See static/js/main.js - initSpeechRecognition() for integration points
```

### Persistent Storage
Add database support for conversation history:
```python
# services/database_service.py (not yet implemented)
from sqlalchemy import create_engine
# Store commands, responses, and user preferences
```

### Custom Themes
Add new themes in `static/css/style.css` by defining new CSS variable sets:
```css
:root.cyberpunk {
    --color-primary: #ff00ff;
    --color-secondary: #00ffff;
}
```

## Troubleshooting

### "Cannot connect to Ollama"
- Ensure Ollama is running: `ollama serve`
- Check `OLLAMA_BASE_URL` in `.env`

### "Speech recognition not available"
- Install missing dependencies: `pip install SpeechRecognition pyaudio`
- For Whisper: `pip install openai-whisper`

### "OpenAI API key not configured"
- Set `OPENAI_API_KEY` in `.env` file
- Get key from: https://platform.openai.com/account/api-keys

### "pyttsx3 audio not working"
- Windows: Ensure audio device is set as default
- Linux: Install espeak: `sudo apt install espeak`
- Mac: Should work out of the box

### Port 5000 already in use
Change in `.env` or command line:
```bash
python app.py --port 5001
```

## Performance Tips

1. **Use local Ollama** for faster responses without API costs
2. **Enable GPU acceleration** in Ollama for faster inference
3. **Cache LLM responses** for common questions
4. **Optimize speech recognition** by reducing audio quality
5. **Use system volume control** instead of software mixing

## Security Considerations

⚠️ **Important**: This application performs system operations. Run only on trusted networks.

- API endpoints accept raw commands (be cautious with untrusted input)
- Store API keys securely (never commit `.env` to version control)
- Shutdown/restart operations require explicit confirmation
- Consider implementing authentication for production use
- Use HTTPS in production environments

## Contributing

To add new features:

1. Create a new blueprint in `blueprints/`
2. Implement service logic in `services/`
3. Register the blueprint in `app.py`
4. Update API documentation in this README

## Future Enhancements

- [ ] Wake word detection without manual button
- [ ] Database persistence for conversation history
- [ ] Multi-user support with authentication
- [ ] Plugin system for custom extensions
- [ ] Mobile app companion
- [ ] Natural language understanding for complex commands
- [ ] Integration with smart home (MQTT, Home Assistant)
- [ ] Streaming responses for long-form content
- [ ] Voice cloning for personalized TTS
- [ ] Real-time chat with WebSocket support

## License

[License type here - same as original J.A.R.V.I.S]

## Credits

Based on the J.A.R.V.I.S project with modern web interface additions.

## Support

For issues and questions:
1. Check the Troubleshooting section above
2. Review API documentation
3. Check logs: `python app.py` (debug output shown)
4. Open an issue on GitHub (if applicable)

---

**J.A.R.V.I.S v2.0** - "Sir, I have updated the system with a new web interface. The Arc Reactor is operational."
