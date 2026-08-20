import pyttsx3
import wikipedia
import speech_recognition as sr
import webbrowser
import datetime
import os
import sys
import smtplib
from news import speak_news, getNewsUrl
from OCR import OCR
from diction import translate
from helpers import *
from youtube import youtube
from sys import platform
import os
import getpass
import cv2
import re
import shutil
import subprocess
import urllib.parse
import logging
from pathlib import Path
from desktop_actions import DesktopActions

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

logging.basicConfig(level=logging.INFO, format='%(message)s')
LOGGER = logging.getLogger('jarvis')

# print(voices[0].id)

class Jarvis:
    def __init__(self) -> None:
        self.platform = platform
        self.desktop = DesktopActions()
        self._last_action_success = True

    def wishMe(self) -> None:
        hour = datetime.datetime.now().hour
        if hour < 12:
            speak('Good morning, sir.')
        elif hour < 18:
            speak('Good afternoon, sir.')
        else:
            speak('Good evening, sir.')
        try:
            weather()
        except Exception as error:
            LOGGER.error('[ERROR] Weather startup failed: %s', error)
            speak('Weather information is currently unavailable.')
        speak('I am JARVIS. Say hey Jarvis followed by a command.')

    def _respond(self, result):
        success, message = result
        self._last_action_success = success
        speak(message)
        return success

    def _confirm(self, prompt):
        speak(prompt)
        answer = (takeCommand() or '').strip().lower()
        return answer in {'yes', 'yes please', 'confirm', 'do it', 'proceed'}

    def _extract_name(self, query, patterns):
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip().strip('"')
        return ''

    def _plan(self, query):
        """Split only unambiguous multi-step commands into executable steps."""
        parts = re.split(
            r'\s*(?:;|\bthen\b|\band then\b|,(?=\s*(?:open|launch|start|create|make|search|take|type|press|close|find|read|copy|move|rename|go|navigate|play|pause|increase|decrease|check|what|tell)\b))\s*',
            query,
            flags=re.IGNORECASE,
        )
        if len(parts) == 1:
            parts = re.split(
                r'\s+and\s+(?=(?:open|launch|start|create|make|search|take|type|press|close|find|read|copy|move|rename|go|navigate|play|pause|increase|decrease|check|what|tell)\b)',
                query,
                flags=re.IGNORECASE,
            )
        return [part.strip() for part in parts if part.strip()]

    def _retry_allowed(self, step):
        return not any(
            word in step.lower()
            for word in ('delete', 'shutdown', 'restart', 'move ', 'install', 'uninstall')
        )

    def execute_query(self, query, announce_complete=True):
        original_query = (query or '').strip()
        query = original_query.lower()
        if not query:
            return True
        self._last_action_success = True
        steps = self._plan(original_query)
        if len(steps) > 1:
            LOGGER.info('[INTENT] PLAN: %s', steps)
            for index, step in enumerate(steps, start=1):
                LOGGER.info('[INTENT] STEP %d/%d: %s', index, len(steps), step)
                outcome = self.execute_query(step, announce_complete=False)
                if outcome is False and self._retry_allowed(step):
                    LOGGER.info('[INTENT] RETRY STEP %d/%d: %s', index, len(steps), step)
                    speak(f'Retrying step {index}.')
                    outcome = self.execute_query(step, announce_complete=False)
                if outcome is False:
                    speak(f'I could not complete step {index}: {step}. The task stopped here.')
                    return False
            if announce_complete:
                speak('Task completed.')
            return True
        LOGGER.info('[COMMAND] %s', query)
        try:
            website_aliases = {
                'youtube': ('https://www.youtube.com', 'YouTube'),
                'google': ('https://www.google.com', 'Google'),
                'gmail': ('https://mail.google.com', 'Gmail'),
                'github': ('https://github.com', 'GitHub'),
                'chatgpt': ('https://chatgpt.com', 'ChatGPT'),
                'instagram': ('https://www.instagram.com', 'Instagram'),
                'linkedin': ('https://www.linkedin.com', 'LinkedIn'),
            }
            if any(alias in query for alias in ('search youtube', 'youtube search')):
                search = re.sub(r'.*?search youtube(?: for)?\s*', '', query).strip()
                self._respond(self.desktop.search('youtube', search))
            elif query in {'open the first result', 'open first result', 'open the first youtube result'}:
                self._respond(self.desktop.open_first_result())
            elif any(text in query for text in ('search google', 'search the web', 'search for ')):
                search = re.sub(r'^(?:please\s+)?(?:search google|search the web|search for)(?: for)?\s*', '', query).strip()
                self._respond(self.desktop.search('google', search))
            elif any(alias in query for alias in website_aliases):
                alias = next(alias for alias in website_aliases if alias in query)
                url, name = website_aliases[alias]
                self._respond(self.desktop.open_url(url, f'Opening {name}.'))
            elif re.search(r'^(?:open|navigate to|go to)\s+https?://', query):
                url = re.sub(r'^(?:open|navigate to|go to)\s+', '', original_query, flags=re.IGNORECASE).strip()
                self._respond(self.desktop.open_url(url, f'Opening {url}.'))
            elif re.match(r'^(?:please\s+)?(?:open|launch|start|show)\b', query):
                app_aliases = {
                    'visual studio code': 'vs code', 'code editor': 'vs code',
                    'vs code': 'vs code', 'chrome': 'chrome', 'edge': 'edge',
                    'notepad': 'notepad', 'calculator': 'calculator', 'calc': 'calculator',
                    'file explorer': 'file explorer', 'explorer': 'file explorer',
                    'command prompt': 'command prompt', 'cmd': 'command prompt',
                    'powershell': 'powershell', 'settings': 'settings', 'task manager': 'task manager',
                }
                app = next((value for key, value in app_aliases.items() if key in query), '')
                if app:
                    self._respond(self.desktop.open_application(app))
                else:
                    folder = next((name for name in ('downloads', 'documents', 'desktop') if name in query), '')
                    self._respond(self.desktop.open_folder(folder or query.replace('open', '').strip()))
            elif query.startswith('close '):
                app = query[6:].replace('the current application', '').strip()
                self._respond(self.desktop.window('close') if not app else self.desktop.close_application(app))
            elif query in {'minimize this window', 'minimize window'}:
                self._respond(self.desktop.window('minimize'))
            elif query in {'maximize this window', 'maximize window'}:
                self._respond(self.desktop.window('maximize'))
            elif query.startswith('switch to '):
                self._respond(self.desktop.window('switch', query[10:].strip()))
            elif 'the time' in query or 'what time' in query:
                self._respond((True, 'The time is ' + datetime.datetime.now().strftime('%I:%M %p') + '.'))
            elif "today's date" in query or 'todays date' in query or 'what is the date' in query:
                self._respond((True, 'Today is ' + datetime.datetime.now().strftime('%A, %B %d, %Y') + '.'))
            elif 'shutdown' in query or 'restart' in query:
                action = 'restart' if 'restart' in query else 'shut down'
                if self._confirm(f'Are you sure you want to {action} the computer?'):
                    self._respond(self.desktop.power('restart' if action == 'restart' else 'shutdown'))
                else:
                    speak('Cancelled.')
            elif query == 'lock' or 'lock the computer' in query or 'lock my computer' in query:
                self._respond(self.desktop.lock())
            elif 'weather' in query:
                weather()
            elif 'news' in query:
                try:
                    speak_news()
                except Exception as error:
                    LOGGER.error('[ERROR] News failed: %s', error)
                    speak('News is currently unavailable.')
            elif any(phrase in query for phrase in ('tell me about', 'what is ', 'who is ')) and not any(
                phrase in query for phrase in ('cpu', 'ram', 'memory', 'battery', 'storage', 'operating system', 'computer name', 'ip address')
            ):
                topic = re.sub(r'^(?:tell me about|what is|who is)\s+', '', query).strip()
                if topic:
                    try:
                        speak(wikipedia.summary(topic, sentences=2))
                    except Exception as error:
                        LOGGER.error('[ERROR] Information lookup failed: %s', error)
                        speak('I could not find that information.')
            elif query.startswith('define ') or query.startswith('dictionary '):
                translate(re.sub(r'^(?:define|dictionary)\s+', '', query).strip())
            elif 'create a folder' in query or 'make a folder' in query:
                name = self._extract_name(query, (r'(?:called|named)\s+(.+?)(?:\s+inside\s+.+|\s+on\s+.+)?$', r'folder\s+(.+)$'))
                parent_match = re.search(r'\s+inside\s+(.+)$', query)
                parent = parent_match.group(1).strip() if parent_match else 'desktop'
                self._respond(self.desktop.create_folder(name or 'New Folder', parent))
            elif 'create a text file' in query or 'create a file' in query:
                name = self._extract_name(query, (r'(?:called|named)\s+(.+)$', r'file\s+(.+)$'))
                self._respond(self.desktop.create_file(name or 'notes.txt'))
            elif query.startswith('write ') or query.startswith('append ') or query.startswith('edit '):
                match = re.search(r'^(?:write|append)\s+(.+?)\s+(?:to|in)\s+(?:the\s+)?(.+)$', original_query, re.IGNORECASE)
                edit_match = re.search(r'^edit\s+(.+?)\s+(?:to say|with)\s+(.+)$', original_query, re.IGNORECASE)
                if edit_match:
                    self._respond(self.desktop.write_file(edit_match.group(1), edit_match.group(2), append=True))
                elif match:
                    self._respond(self.desktop.write_file(match.group(2), match.group(1), append=query.startswith('append ')))
                else:
                    self._respond((False, 'Please say what text to write and which file to update.'))
            elif query.startswith('rename '):
                match = re.search(r'rename\s+(.+?)\s+to\s+(.+)$', query)
                self._respond(self.desktop.rename_file(match.group(1), match.group(2)) if match else (False, 'Please say what to rename and the new name.'))
            elif query.startswith('copy '):
                match = re.search(r'copy\s+(.+?)\s+to\s+(.+)$', query)
                self._respond(self.desktop.copy_file(match.group(1), match.group(2)) if match else (False, 'Please say what to copy and where.'))
            elif query.startswith('move '):
                match = re.search(r'move\s+(.+?)\s+to\s+(.+)$', query)
                if not match:
                    self._respond((False, 'Please say what to move and where.'))
                elif self._confirm(f'Are you sure you want to move {match.group(1)} to {match.group(2)}?'):
                    self._respond(self.desktop.move_file(match.group(1), match.group(2)))
                else:
                    speak('Cancelled.')
            elif query.startswith('delete '):
                name = query[7:].replace('the ', '', 1).strip()
                if self._confirm(f'I found {name}. Do you want me to permanently delete it?'):
                    self._respond(self.desktop.delete_file(name))
                else:
                    speak('Cancelled.')
            elif 'what files are in' in query or 'list files in' in query:
                folder = re.sub(r'^(?:what files are in|list files in)\s+', '', query).strip()
                self._respond(self.desktop.list_files(folder))
            elif 'find all ' in query and ' files in ' in query:
                match = re.search(r'find all (\w+) files in (.+)$', query)
                self._respond(self.desktop.find_files(match.group(2), match.group(1)) if match else (False, 'Please specify a file type and folder.'))
            elif query.startswith('read '):
                self._respond(self.desktop.read_file(query[5:].strip()))
            elif 'screenshot' in query:
                name = self._extract_name(query, (r'name it\s+([\w.-]+)', r'save.*?as\s+([\w.-]+)')) or 'screenshot.png'
                self._respond(self.desktop.screenshot(name))
            elif 'cpu' in query or 'ram' in query or 'memory' in query or 'battery' in query or 'storage' in query or 'operating system' in query or 'computer name' in query or 'ip address' in query:
                kind = next((item for item in ('cpu', 'ram', 'battery', 'storage', 'operating system', 'computer name', 'ip address') if item in query), 'ram')
                self._respond(self.desktop.system_info(kind))
            elif 'increase volume' in query or 'decrease volume' in query or 'mute volume' in query or 'unmute volume' in query:
                direction = 'up' if 'increase' in query else 'down' if 'decrease' in query else 'mute'
                self._respond(self.desktop.volume(direction))
            elif query.startswith('type '):
                self._respond(self.desktop.keyboard('type ' + original_query[5:]))
            elif query in {'press enter', 'press escape', 'press tab', 'press space'} or query.startswith('press ctrl+') or query.startswith('press alt+'):
                self._respond(self.desktop.keyboard(query.replace('press ', '')))
            elif query in {'click', 'double click', 'scroll up', 'scroll down'}:
                self._respond(self.desktop.mouse(query))
            elif 'clear the clipboard' in query or 'clear clipboard' in query:
                self._respond(self.desktop.clipboard_clear())
            elif 'what is currently copied' in query or 'what is on the clipboard' in query:
                self._respond(self.desktop.clipboard_get())
            elif query.startswith('copy this text '):
                self._respond(self.desktop.clipboard_set(original_query[15:]))
            elif 'open display settings' in query:
                self._respond(self.desktop.open_settings('display'))
            elif 'open network settings' in query or 'turn wi-fi' in query or 'turn wifi' in query:
                self._respond(self.desktop.open_settings('network'))
            elif 'open sound settings' in query:
                self._respond(self.desktop.open_settings('sound'))
            elif 'play music' in query or query.startswith('play '):
                self._respond(self.desktop.media('play'))
            elif query in {'pause', 'resume', 'next song', 'previous song'}:
                action = 'next' if query == 'next song' else 'previous' if query == 'previous song' else query
                self._respond(self.desktop.media(action))
            elif query.startswith('run '):
                self._respond(self.desktop.run_safe_command(query[4:].strip()))
            elif 'remind me in ' in query:
                match = re.search(r'remind me in (\d+) minutes? to (.+)$', query)
                self._respond(self.desktop.reminder(int(match.group(1)) * 60, match.group(2)) if match else (False, 'Please say: remind me in ten minutes to do something.'))
            elif 'your name' in query:
                self._respond((True, 'My name is JARVIS.'))
            elif 'joke' in query:
                joke()
            elif query in {'sleep', 'exit', 'quit', 'goodbye'}:
                speak('Goodbye.')
                return False
            else:
                speak("I don't know how to perform that command yet.")
                LOGGER.info('[INTENT] UNKNOWN')
        except Exception as error:
            LOGGER.exception('[ERROR] Command failed: %s', error)
            self._last_action_success = False
            speak('I could not complete that command, but I am still listening.')
        return self._last_action_success


def wakeUpJARVIS():
    bot_ = Jarvis()
    bot_.wishMe()
    while True:
        query = (takeCommand() or '').lower()
        if not query:
            continue

        wake_words = ('hey jarvis', 'jarvis')
        if any(word in query for word in wake_words):
            speak('Yes, how can I help?')
            command = query
            for word in wake_words:
                command = command.replace(word, '').strip()
            if not command:
                command = (takeCommand() or '').lower()
        else:
            LOGGER.info('[VOICE] Ignoring speech without wake word.')
            continue

        if bot_.execute_query(command) is False:
            break
 

def run_face_authentication():
    """Return True on success, False on rejection, None when unavailable."""
    base = Path(__file__).resolve().parent
    model_path = base / 'Face-Recognition' / 'trainer' / 'trainer.yml'
    cascade_path = base / 'Face-Recognition' / 'haarcascade_frontalface_default.xml'
    camera = None
    try:
        if not hasattr(cv2, 'face') or not model_path.is_file() or not cascade_path.is_file():
            return None
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(str(model_path))
        face_cascade = cv2.CascadeClassifier(str(cascade_path))
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not camera.isOpened():
            return None
        camera.set(3, 640)
        camera.set(4, 480)
        min_w = 0.1 * camera.get(3)
        min_h = 0.1 * camera.get(4)
        while True:
            ret, image = camera.read()
            if not ret or image is None:
                LOGGER.error('[ERROR] Camera frame unavailable.')
                return None
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(int(min_w), int(min_h)))
            for x, y, width, height in faces:
                _, accuracy = recognizer.predict(gray[y:y + height, x:x + width])
                if accuracy < 100:
                    return True
                speak('Optical face recognition failed.')
                return False
    except (AttributeError, OSError, cv2.error) as error:
        LOGGER.error('[ERROR] Face authentication unavailable: %s', error)
        return None
    finally:
        if camera is not None:
            camera.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    import sys

    authentication = None if '--skip-face' in sys.argv else run_face_authentication()
    if authentication is False:
        speak('Face authentication failed.')
    else:
        if authentication is None:
            speak('Face authentication is unavailable. Starting voice assistant.')
        else:
            speak('Optical face recognition done. Welcome.')
        wakeUpJARVIS()


    
