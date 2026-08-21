"""
System Control Service - Controls desktop applications and system functions
Handles: opening apps, screenshots, clipboard, volume, media keys, window control
"""

import logging
import os
import subprocess
import sys
import psutil
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SystemControlService:
    """Service for system-level desktop control and automation"""
    
    def __init__(self):
        """Initialize system control service"""
        self.platform = sys.platform
        logger.info(f'SystemControlService initialized for platform: {self.platform}')
    
    # ============================================================================
    # APPLICATION CONTROL
    # ============================================================================
    
    def open_application(self, app_name: str) -> Dict[str, Any]:
        """
        Open a desktop application by name.
        
        Args:
            app_name: Name of application (chrome, notepad, vscode, etc.)
        
        Returns:
            Success status and message
        """
        try:
            app_name_lower = app_name.lower().strip()
            
            # Map common app names to executables
            app_mapping = {
                'chrome': 'chrome' if self.platform != 'win32' else 'chrome',
                'google chrome': 'chrome' if self.platform != 'win32' else 'chrome',
                'edge': 'msedge',
                'firefox': 'firefox',
                'notepad': 'notepad.exe' if self.platform == 'win32' else 'gedit',
                'vscode': 'code',
                'visual studio code': 'code',
                'calculator': 'calc.exe' if self.platform == 'win32' else 'gnome-calculator',
                'file explorer': 'explorer.exe' if self.platform == 'win32' else 'nautilus',
                'paint': 'mspaint.exe' if self.platform == 'win32' else 'kolourpaint',
                'word': 'winword.exe' if self.platform == 'win32' else 'libreoffice',
                'excel': 'excel.exe' if self.platform == 'win32' else 'libreoffice',
                'powerpoint': 'powerpnt.exe' if self.platform == 'win32' else 'libreoffice',
                'settings': 'ms-settings:' if self.platform == 'win32' else 'gnome-control-center',
                'task manager': 'taskmgr.exe' if self.platform == 'win32' else 'gnome-system-monitor',
                'powershell': 'powershell.exe' if self.platform == 'win32' else 'bash',
                'command prompt': 'cmd.exe' if self.platform == 'win32' else 'bash',
            }
            
            app_to_launch = app_mapping.get(app_name_lower, app_name)
            
            if self.platform == 'win32':
                os.startfile(app_to_launch) if ' ' not in app_to_launch else subprocess.Popen(app_to_launch)
            else:
                subprocess.Popen([app_to_launch])
            
            logger.info(f'Opened application: {app_name}')
            return {
                'success': True,
                'message': f'Opened {app_name}'
            }
            
        except Exception as e:
            logger.error(f'Error opening application {app_name}: {e}')
            return {
                'success': False,
                'message': f'Could not open {app_name}: {str(e)}'
            }
    
    def close_application(self, app_name: str) -> Dict[str, Any]:
        """
        Close a running application by name.
        
        Args:
            app_name: Name of application to close
        
        Returns:
            Success status
        """
        try:
            # Map to process names
            process_mapping = {
                'chrome': ['chrome.exe', 'google-chrome'],
                'edge': ['msedge.exe'],
                'firefox': ['firefox.exe', 'firefox'],
                'notepad': ['notepad.exe'],
                'vscode': ['code.exe', 'code'],
                'calculator': ['calc.exe', 'gnome-calculator'],
            }
            
            process_names = process_mapping.get(app_name.lower(), [app_name.lower()])
            
            killed = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if any(pname in proc.info['name'].lower() for pname in process_names):
                        proc.terminate()
                        proc.wait(timeout=5)
                        killed = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if killed:
                logger.info(f'Closed application: {app_name}')
                return {'success': True, 'message': f'Closed {app_name}'}
            else:
                return {'success': False, 'message': f'{app_name} not found'}
                
        except Exception as e:
            logger.error(f'Error closing {app_name}: {e}')
            return {'success': False, 'message': str(e)}
    
    # ============================================================================
    # SCREEN & CLIPBOARD CONTROL
    # ============================================================================
    
    def take_screenshot(self) -> Dict[str, Any]:
        """
        Take a screenshot and save to file.
        
        Returns:
            Path to screenshot file
        """
        try:
            from PIL import ImageGrab
            import time
            
            screenshot_dir = Path('screenshots')
            screenshot_dir.mkdir(exist_ok=True)
            
            timestamp = int(time.time())
            screenshot_path = screenshot_dir / f'screenshot_{timestamp}.png'
            
            image = ImageGrab.grab()
            image.save(str(screenshot_path))
            
            logger.info(f'Screenshot saved: {screenshot_path}')
            return {
                'success': True,
                'message': f'Screenshot saved to {screenshot_path}',
                'path': str(screenshot_path)
            }
            
        except Exception as e:
            logger.error(f'Error taking screenshot: {e}')
            return {'success': False, 'message': str(e)}
    
    def read_clipboard(self) -> Dict[str, Any]:
        """
        Read text from clipboard.
        
        Returns:
            Clipboard content
        """
        try:
            import pyperclip
            content = pyperclip.paste()
            return {
                'success': True,
                'content': content,
                'length': len(content)
            }
        except Exception as e:
            logger.error(f'Error reading clipboard: {e}')
            return {'success': False, 'message': str(e)}
    
    def write_clipboard(self, text: str) -> Dict[str, Any]:
        """
        Write text to clipboard.
        
        Args:
            text: Text to copy
        
        Returns:
            Success status
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            logger.info(f'Copied {len(text)} chars to clipboard')
            return {
                'success': True,
                'message': 'Copied to clipboard'
            }
        except Exception as e:
            logger.error(f'Error writing to clipboard: {e}')
            return {'success': False, 'message': str(e)}
    
    # ============================================================================
    # KEYBOARD & MOUSE CONTROL
    # ============================================================================
    
    def type_text(self, text: str, delay: float = 0.05) -> Dict[str, Any]:
        """
        Type text character by character.
        
        Args:
            text: Text to type
            delay: Delay between keystrokes (seconds)
        
        Returns:
            Success status
        """
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=delay)
            logger.info(f'Typed {len(text)} characters')
            return {'success': True, 'message': f'Typed {len(text)} characters'}
        except Exception as e:
            logger.error(f'Error typing text: {e}')
            return {'success': False, 'message': str(e)}
    
    def press_key(self, key: str) -> Dict[str, Any]:
        """
        Press a keyboard key.
        
        Args:
            key: Key name (enter, space, delete, alt, ctrl, etc.)
        
        Returns:
            Success status
        """
        try:
            import pyautogui
            pyautogui.press(key.lower())
            logger.info(f'Pressed key: {key}')
            return {'success': True, 'message': f'Pressed {key}'}
        except Exception as e:
            logger.error(f'Error pressing key: {e}')
            return {'success': False, 'message': str(e)}
    
    def click(self, x: int, y: int, button: str = 'left') -> Dict[str, Any]:
        """
        Click at screen coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
        
        Returns:
            Success status
        """
        try:
            import pyautogui
            pyautogui.click(x, y, button=button)
            logger.info(f'Clicked at ({x}, {y}) with {button} button')
            return {'success': True, 'message': f'Clicked at ({x}, {y})'}
        except Exception as e:
            logger.error(f'Error clicking: {e}')
            return {'success': False, 'message': str(e)}
    
    def scroll(self, direction: str = 'down', amount: int = 3) -> Dict[str, Any]:
        """
        Scroll the mouse wheel.
        
        Args:
            direction: Scroll direction ('up', 'down')
            amount: Number of scroll units
        
        Returns:
            Success status
        """
        try:
            import pyautogui
            scroll_amount = amount if direction.lower() == 'down' else -amount
            pyautogui.scroll(scroll_amount)
            logger.info(f'Scrolled {direction} by {amount} units')
            return {'success': True, 'message': f'Scrolled {direction}'}
        except Exception as e:
            logger.error(f'Error scrolling: {e}')
            return {'success': False, 'message': str(e)}
    
    # ============================================================================
    # WINDOW CONTROL
    # ============================================================================
    
    def minimize_window(self) -> Dict[str, Any]:
        """Minimize the current window"""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'F9')
            return {'success': True, 'message': 'Minimized window'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def maximize_window(self) -> Dict[str, Any]:
        """Maximize the current window"""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'F10')
            return {'success': True, 'message': 'Maximized window'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def close_window(self) -> Dict[str, Any]:
        """Close the current window"""
        try:
            import pyautogui
            pyautogui.hotkey('alt', 'F4')
            return {'success': True, 'message': 'Closed window'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ============================================================================
    # SYSTEM INFORMATION
    # ============================================================================
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information (CPU, RAM, disk, battery).
        
        Returns:
            Dictionary with system stats
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'disk_total_gb': disk.total / (1024**3),
            }
            
            # Battery info (if available)
            try:
                battery = psutil.sensors_battery()
                if battery:
                    info['battery_percent'] = battery.percent
                    info['battery_plugged'] = battery.power_plugged
            except:
                pass
            
            return {'success': True, 'data': info}
            
        except Exception as e:
            logger.error(f'Error getting system info: {e}')
            return {'success': False, 'message': str(e)}
    
    # ============================================================================
    # AUDIO CONTROL
    # ============================================================================
    
    def set_volume(self, level: int) -> Dict[str, Any]:
        """
        Set system volume level (0-100).
        
        Args:
            level: Volume level (0-100)
        
        Returns:
            Success status
        """
        if not (0 <= level <= 100):
            return {'success': False, 'message': 'Volume must be between 0 and 100'}
        
        try:
            if self.platform == 'win32':
                # Windows volume control
                subprocess.run(['powershell', '-c', f'(Get-Volume).Mute = $false; [int]$volume = {level}; $volume'], 
                             capture_output=True)
            else:
                # Linux/Mac volume control
                subprocess.run(['amixer', 'set', 'Master', f'{level}%'], capture_output=True)
            
            logger.info(f'Set volume to {level}%')
            return {'success': True, 'message': f'Volume set to {level}%'}
        except Exception as e:
            logger.error(f'Error setting volume: {e}')
            return {'success': False, 'message': str(e)}
    
    def mute_audio(self) -> Dict[str, Any]:
        """Mute system audio"""
        try:
            if self.platform == 'win32':
                subprocess.run(['powershell', '-c', '(Get-Volume).Mute = $true'], capture_output=True)
            else:
                subprocess.run(['amixer', 'set', 'Master', 'mute'], capture_output=True)
            
            return {'success': True, 'message': 'Audio muted'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def unmute_audio(self) -> Dict[str, Any]:
        """Unmute system audio"""
        try:
            if self.platform == 'win32':
                subprocess.run(['powershell', '-c', '(Get-Volume).Mute = $false'], capture_output=True)
            else:
                subprocess.run(['amixer', 'set', 'Master', 'unmute'], capture_output=True)
            
            return {'success': True, 'message': 'Audio unmuted'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ============================================================================
    # SYSTEM CONTROL
    # ============================================================================
    
    def lock_screen(self) -> Dict[str, Any]:
        """Lock the system"""
        try:
            if self.platform == 'win32':
                os.system('rundll32.exe user32.dll,LockWorkStation')
            else:
                os.system('loginctl lock-session')
            
            return {'success': True, 'message': 'Screen locked'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def shutdown(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Shutdown the system.
        
        Args:
            confirm: If False, aborts. Requires explicit confirmation.
        
        Returns:
            Success status
        """
        if not confirm:
            return {'success': False, 'message': 'Shutdown requires explicit confirmation'}
        
        try:
            if self.platform == 'win32':
                os.system('shutdown /s /t 30 /c "Shutdown initiated by JARVIS"')
            else:
                os.system('shutdown -h 1')
            
            return {'success': True, 'message': 'System shutdown initiated'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def restart(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Restart the system.
        
        Args:
            confirm: If False, aborts. Requires explicit confirmation.
        
        Returns:
            Success status
        """
        if not confirm:
            return {'success': False, 'message': 'Restart requires explicit confirmation'}
        
        try:
            if self.platform == 'win32':
                os.system('shutdown /r /t 30 /c "Restart initiated by JARVIS"')
            else:
                os.system('shutdown -r 1')
            
            return {'success': True, 'message': 'System restart initiated'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
