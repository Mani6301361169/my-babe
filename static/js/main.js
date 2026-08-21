/**
 * J.A.R.V.I.S Web UI - Main JavaScript
 * Handles user interactions, API calls, and real-time updates
 */

class JarvisUI {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.isListening = false;
        this.recognition = null;
        this.settings = this.loadSettings();
        this.history = [];
        this.currentJobId = null;
        
        this.init();
    }

    init() {
        this.cacheElements();
        this.attachEventListeners();
        this.initSpeechRecognition();
        this.updateSystemInfo();
        this.checkLLMStatus();
        
        // Update system info every 5 seconds
        setInterval(() => this.updateSystemInfo(), 5000);
    }

    // ========================================================================
    // DOM & Cache
    // ========================================================================

    cacheElements() {
        this.elements = {
            btnListen: document.getElementById('btnListen'),
            btnText: document.getElementById('btnText'),
            btnClear: document.getElementById('btnClear'),
            btnSettings: document.getElementById('btnSettings'),
            btnCloseSettings: document.getElementById('btnCloseSettings'),
            btnSaveSettings: document.getElementById('btnSaveSettings'),
            btnClearHistory: document.getElementById('btnClearHistory'),
            btnInfo: document.getElementById('btnInfo'),
            
            commandInput: document.getElementById('commandInput'),
            outputContent: document.getElementById('outputContent'),
            historyList: document.getElementById('historyList'),
            
            settingsPanel: document.getElementById('settingsPanel'),
            llmProvider: document.getElementById('llmProvider'),
            speechEngine: document.getElementById('speechEngine'),
            ttsEngine: document.getElementById('ttsEngine'),
            volumeControl: document.getElementById('volumeControl'),
            volumeValue: document.getElementById('volumeValue'),
            themeSelect: document.getElementById('themeSelect'),
            openaiKey: document.getElementById('openaiKey'),
            
            arcStatus: document.getElementById('arcStatus'),
            statusValue: document.getElementById('statusValue'),
            modeValue: document.getElementById('modeValue'),
            systemValue: document.getElementById('systemValue'),
            
            toast: document.getElementById('toast'),
        };
    }

    attachEventListeners() {
        this.elements.btnListen.addEventListener('click', () => this.startListening());
        this.elements.btnText.addEventListener('click', () => this.sendTextCommand());
        this.elements.btnClear.addEventListener('click', () => this.clearInput());
        this.elements.btnSettings.addEventListener('click', () => this.toggleSettings());
        this.elements.btnCloseSettings.addEventListener('click', () => this.toggleSettings());
        this.elements.btnSaveSettings.addEventListener('click', () => this.saveSettings());
        this.elements.btnClearHistory.addEventListener('click', () => this.clearHistory());
        this.elements.btnInfo.addEventListener('click', () => this.showSystemInfo());
        this.elements.volumeControl.addEventListener('change', (e) => this.setVolume(e.target.value));
        this.elements.commandInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                this.sendTextCommand();
            }
        });
    }

    // ========================================================================
    // Settings Management
    // ========================================================================

    loadSettings() {
        const saved = localStorage.getItem('jarvis_settings');
        return saved ? JSON.parse(saved) : {
            llmProvider: 'openai',
            speechEngine: 'google',
            ttsEngine: 'pyttsx3',
            volume: 70,
            theme: 'dark',
            openaiKey: ''
        };
    }

    saveSettings() {
        this.settings.llmProvider = this.elements.llmProvider.value;
        this.settings.speechEngine = this.elements.speechEngine.value;
        this.settings.ttsEngine = this.elements.ttsEngine.value;
        this.settings.volume = this.elements.volumeControl.value;
        this.settings.theme = this.elements.themeSelect.value;
        this.settings.openaiKey = this.elements.openaiKey.value;
        
        localStorage.setItem('jarvis_settings', JSON.stringify(this.settings));
        this.applyTheme(this.settings.theme);
        this.showToast('Settings saved successfully', 'success');
    }

    toggleSettings() {
        this.elements.settingsPanel.classList.toggle('active');
        
        // Load current settings into form
        this.elements.llmProvider.value = this.settings.llmProvider;
        this.elements.speechEngine.value = this.settings.speechEngine;
        this.elements.ttsEngine.value = this.settings.ttsEngine;
        this.elements.volumeControl.value = this.settings.volume;
        this.elements.volumeValue.textContent = this.settings.volume + '%';
        this.elements.themeSelect.value = this.settings.theme;
        this.elements.openaiKey.value = this.settings.openaiKey;
    }

    applyTheme(theme) {
        const root = document.documentElement;
        
        switch(theme) {
            case 'light':
                root.style.setProperty('--color-primary', '#0066ff');
                root.style.setProperty('--color-dark', '#f0f0f0');
                break;
            case 'blue':
                root.style.setProperty('--color-primary', '#00d4ff');
                root.style.setProperty('--color-secondary', '#0099ff');
                break;
            default: // dark
                root.style.setProperty('--color-primary', '#00d4ff');
                root.style.setProperty('--color-secondary', '#ff6b00');
        }
    }

    // ========================================================================
    // Speech Recognition
    // ========================================================================

    initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            this.showToast('Speech recognition not supported in your browser', 'error');
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateStatus('LISTENING', 'VOICE', 'ACTIVE');
            this.elements.btnListen.classList.add('active');
            this.elements.arcStatus.textContent = 'LISTENING';
            this.elements.commandInput.focus();
        };

        this.recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            this.elements.commandInput.value = transcript;
        };

        this.recognition.onerror = (event) => {
            let message = `Speech error: ${event.error}`;
            if (event.error === 'not-allowed') {
                message = 'Microphone access was blocked. Allow microphone access for this site and try again.';
            } else if (event.error === 'network') {
                message = 'Online speech recognition is unavailable. Check your internet connection or use Text mode.';
            }
            this.showToast(message, 'error');
            this.elements.arcStatus.textContent = 'ERROR';
            this.updateStatus('ERROR', 'TEXT', 'VOICE UNAVAILABLE');
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.elements.btnListen.classList.remove('active');
            
            // Auto-send if we have text
            if (this.elements.commandInput.value.trim()) {
                setTimeout(() => this.sendTextCommand(), 500);
            }
        };
    }

    startListening() {
        if (!this.recognition) {
            this.showToast('Voice input is unavailable. Use Chrome or Edge, allow microphone access, or use Text.', 'error');
            this.updateStatus('ERROR', 'TEXT', 'UNAVAILABLE');
            return;
        }

        if (this.isListening) {
            this.recognition.stop();
            return;
        }

        this.elements.commandInput.value = '';
        this.recognition.start();
    }

    // ========================================================================
    // Command Processing
    // ========================================================================

    async sendTextCommand() {
        const command = this.elements.commandInput.value.trim();
        
        if (!command) {
            this.showToast('Please enter a command', 'error');
            return;
        }

        this.updateStatus('PROCESSING', 'TEXT', 'BUSY');
        this.elements.arcStatus.textContent = 'THINKING';

        try {
            // Send command to API
            const response = await fetch(`${this.apiBase}/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: command,
                    context: { history: this.history.slice(-5) }
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.displayResponse(data.response);
                this.addToHistory(command, data.response);
                
                // Play TTS response
                await this.synthesizeSpeech(data.response);
                
                this.updateStatus('READY', 'IDLE', 'READY');
                this.elements.arcStatus.textContent = 'READY';
            } else {
                this.showToast(`Error: ${data.error}`, 'error');
                this.updateStatus('ERROR', 'IDLE', 'ERROR');
            }
            
        } catch (error) {
            console.error('Command error:', error);
            this.showToast(`Error: ${error.message}`, 'error');
            this.updateStatus('ERROR', 'IDLE', 'ERROR');
        }

        this.elements.commandInput.value = '';
    }

    displayResponse(response) {
        this.elements.outputContent.textContent = response;
        this.elements.outputContent.scrollTop = this.elements.outputContent.scrollHeight;
    }

    async synthesizeSpeech(text) {
        try {
            const response = await fetch(`${this.apiBase}/speak`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    engine: this.settings.ttsEngine,
                    rate: 1.0
                })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.audio_url) {
                    const audio = new Audio(data.audio_url);
                    audio.play().catch(e => console.log('Audio playback failed:', e));
                }
            }
        } catch (error) {
            console.error('TTS error:', error);
        }
    }

    // ========================================================================
    // History Management
    // ========================================================================

    addToHistory(query, response) {
        const item = {
            query: query,
            response: response,
            timestamp: new Date().toLocaleTimeString()
        };
        
        this.history.push(item);
        this.renderHistory();
    }

    renderHistory() {
        this.elements.historyList.innerHTML = '';
        
        if (this.history.length === 0) {
            this.elements.historyList.innerHTML = '<div class="history-empty">No history yet</div>';
            return;
        }

        this.history.slice().reverse().forEach((item, index) => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <div class="query"><strong>Q:</strong> ${this.escapeHtml(item.query)}</div>
                <div class="response"><strong>A:</strong> ${this.escapeHtml(item.response.substring(0, 50))}...</div>
                <small>${item.timestamp}</small>
            `;
            div.addEventListener('click', () => this.elements.commandInput.value = item.query);
            this.elements.historyList.appendChild(div);
        });
    }

    clearHistory() {
        if (confirm('Clear all history?')) {
            this.history = [];
            this.renderHistory();
            this.showToast('History cleared', 'success');
        }
    }

    // ========================================================================
    // System Information
    // ========================================================================

    async updateSystemInfo() {
        try {
            const response = await fetch(`${this.apiBase}/system/info`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const info = data.data;
                    const status = info.cpu_percent < 50 ? 'OPTIMAL' : info.cpu_percent < 80 ? 'GOOD' : 'HIGH';
                    this.elements.systemValue.textContent = `CPU: ${info.cpu_percent.toFixed(0)}% | RAM: ${info.memory_percent.toFixed(0)}%`;
                }
            }
        } catch (error) {
            console.error('System info error:', error);
        }
    }

    showSystemInfo() {
        fetch(`${this.apiBase}/system/info`)
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    const info = data.data;
                    let message = `System Information:\n\n`;
                    message += `CPU: ${info.cpu_percent.toFixed(1)}%\n`;
                    message += `Memory: ${info.memory_percent.toFixed(1)}% (${info.memory_available_gb.toFixed(1)}/${info.memory_total_gb.toFixed(0)} GB)\n`;
                    message += `Disk: ${info.disk_percent.toFixed(1)}% (${info.disk_free_gb.toFixed(0)}/${info.disk_total_gb.toFixed(0)} GB)\n`;
                    if (info.battery_percent !== undefined) {
                        message += `Battery: ${info.battery_percent.toFixed(0)}% (${info.battery_plugged ? 'Plugged' : 'On Battery'})\n`;
                    }
                    alert(message);
                }
            })
            .catch(error => console.error('Error fetching system info:', error));
    }

    async checkLLMStatus() {
        try {
            const response = await fetch(`${this.apiBase}/command/status`);
            if (response.ok) {
                const data = await response.json();
                if (data.connected) {
                    this.modeValue = data.model;
                }
            }
        } catch (error) {
            console.error('LLM status error:', error);
        }
    }

    // ========================================================================
    // System Control
    // ========================================================================

    async setVolume(level) {
        try {
            await fetch(`${this.apiBase}/system/audio`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'volume',
                    level: parseInt(level)
                })
            });
            this.elements.volumeValue.textContent = level + '%';
        } catch (error) {
            console.error('Volume control error:', error);
        }
    }

    // ========================================================================
    // UI Updates
    // ========================================================================

    updateStatus(status, mode, system) {
        this.elements.statusValue.textContent = status;
        this.elements.modeValue.textContent = mode;
        this.elements.systemValue.textContent = system;
    }

    clearInput() {
        this.elements.commandInput.value = '';
        this.elements.outputContent.textContent = 'Awaiting command...';
        this.elements.arcStatus.textContent = 'READY';
    }

    showToast(message, type = 'info') {
        this.elements.toast.textContent = message;
        this.elements.toast.className = `toast show ${type}`;
        
        setTimeout(() => {
            this.elements.toast.classList.remove('show');
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.jarvis = new JarvisUI();
});
