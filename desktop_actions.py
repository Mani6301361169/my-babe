"""Safe Windows desktop actions used by the J.A.R.V.I.S. command router."""

from __future__ import annotations

import datetime
import logging
import os
import platform
import re
import shutil
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

import psutil
import pyautogui
import pyperclip


LOGGER = logging.getLogger("jarvis")


class DesktopActions:
    """Perform bounded desktop actions and report whether they succeeded."""

    def __init__(self) -> None:
        self.home = Path.home()
        self.desktop = self._known_folder("Desktop")
        self.documents = self._known_folder("Documents")
        self.downloads = self._known_folder("Downloads")
        self._reminders: list[threading.Timer] = []

    def _known_folder(self, name: str) -> Path:
        return self.home / name

    def _result(self, success: bool, message: str, action: str = "") -> tuple[bool, str]:
        LOGGER.info("[RESULT] %s", "SUCCESS" if success else "FAILURE")
        if action:
            LOGGER.info("[ACTION] %s", action)
        return success, message

    def open_url(self, url: str, message: str) -> tuple[bool, str]:
        LOGGER.info("[INTENT] OPEN_WEBSITE")
        LOGGER.info("[ACTION] Opening %s", url)
        try:
            if webbrowser.open_new_tab(url):
                return self._result(True, message)
        except webbrowser.Error as error:
            LOGGER.error("[ERROR] Browser error: %s", error)
        return self._result(False, "I couldn't open that website.")

    def search(self, provider: str, phrase: str) -> tuple[bool, str]:
        phrase = phrase.strip()
        if not phrase:
            return self._result(False, f"I need something to search for on {provider}.")
        encoded = __import__("urllib.parse", fromlist=["quote"]).quote(phrase)
        if provider == "youtube":
            url = f"https://www.youtube.com/results?search_query={encoded}"
        else:
            url = f"https://www.google.com/search?q={encoded}"
        return self.open_url(url, f"Searching {provider.title()} for {phrase}.")

    def _application_specs(self) -> dict[str, tuple[str, ...]]:
        return {
            "chrome": ("chrome.exe",),
            "edge": ("msedge.exe",),
            "vs code": ("code.exe", "code"),
            "notepad": ("notepad.exe",),
            "calculator": ("calc.exe",),
            "file explorer": ("explorer.exe",),
            "command prompt": ("cmd.exe",),
            "powershell": ("powershell.exe",),
            "settings": ("ms-settings:",),
            "task manager": ("taskmgr.exe",),
        }

    def open_application(self, requested: str) -> tuple[bool, str]:
        name = requested.lower().strip()
        specs = self._application_specs()
        commands = specs.get(name)
        if not commands:
            return self._result(False, f"I don't know how to open {requested}.")
        try:
            command = commands[0]
            if command.endswith(":"):
                os.startfile(command)
            else:
                executable = next((shutil.which(item) for item in commands if shutil.which(item)), None)
                if not executable:
                    return self._result(False, f"{requested.title()} is not installed on this computer.")
                process = subprocess.Popen([executable], close_fds=True)
                if process.poll() is not None:
                    return self._result(False, f"I couldn't open {requested}.")
            time.sleep(0.15)
            return self._result(True, f"{requested.title()} is open.", f"Opening {requested}")
        except (OSError, ValueError) as error:
            LOGGER.error("[ERROR] Application launch failed: %s", error)
            return self._result(False, f"I couldn't open {requested}.")

    def close_application(self, requested: str) -> tuple[bool, str]:
        process_names = {
            "chrome": "chrome.exe", "edge": "msedge.exe", "vs code": "code.exe",
            "notepad": "notepad.exe", "calculator": "CalculatorApp.exe",
        }
        process_name = process_names.get(requested.lower().strip())
        if not process_name:
            return self._result(False, "I can only close supported applications by name.")
        found = [process for process in psutil.process_iter(["name"]) if process.info["name"] == process_name]
        if not found:
            return self._result(False, f"{requested.title()} is not running.")
        try:
            for process in found:
                process.terminate()
            return self._result(True, f"Closed {requested.title()}.", f"Closing {process_name}")
        except (psutil.Error, OSError) as error:
            LOGGER.error("[ERROR] Application close failed: %s", error)
            return self._result(False, f"I couldn't close {requested}.")

    def resolve_path(self, value: str, default_folder: Optional[Path] = None) -> Path:
        value = value.strip().strip('"')
        folders = {
            "desktop": self.desktop, "downloads": self.downloads,
            "documents": self.documents, "my desktop": self.desktop,
            "my downloads": self.downloads, "my documents": self.documents,
        }
        lower = value.lower()
        for label, folder in folders.items():
            if lower == label:
                return folder
        path = Path(os.path.expandvars(os.path.expanduser(value)))
        if path.is_absolute():
            return path
        return (default_folder or self.desktop) / path

    def open_folder(self, name: str) -> tuple[bool, str]:
        folder = self.resolve_path(name)
        if not folder.is_dir():
            return self._result(False, f"I couldn't find {folder.name}.")
        try:
            os.startfile(str(folder))
            return self._result(True, f"Opened {folder.name}.", f"Opening folder {folder}")
        except OSError as error:
            LOGGER.error("[ERROR] Folder open failed: %s", error)
            return self._result(False, "I couldn't open that folder.")

    def create_folder(self, name: str, parent: str = "desktop") -> tuple[bool, str]:
        folder = self.resolve_path(parent) / name.strip().strip('"')
        try:
            folder.mkdir(parents=False, exist_ok=False)
            return self._result(True, f"Created folder {folder.name}.")
        except FileExistsError:
            return self._result(False, f"Folder {folder.name} already exists.")
        except OSError as error:
            LOGGER.error("[ERROR] Folder creation failed: %s", error)
            return self._result(False, "I couldn't create that folder.")

    def create_file(self, name: str, parent: str = "desktop") -> tuple[bool, str]:
        path = self.resolve_path(parent) / name.strip().strip('"')
        try:
            path.touch(exist_ok=False)
            return self._result(True, f"Created {path.name}.")
        except FileExistsError:
            return self._result(False, f"{path.name} already exists.")
        except OSError as error:
            LOGGER.error("[ERROR] File creation failed: %s", error)
            return self._result(False, "I couldn't create that file.")

    def write_file(self, name: str, content: str, append: bool = False) -> tuple[bool, str]:
        path = self.resolve_path(name)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            mode = "a" if append else "w"
            with path.open(mode, encoding="utf-8") as file:
                file.write(content + ("\n" if content else ""))
            verb = "Updated" if append else "Wrote"
            return self._result(True, f"{verb} {path.name}.")
        except OSError as error:
            LOGGER.error("[ERROR] File write failed: %s", error)
            return self._result(False, f"I couldn't update {path.name}.")

    def rename_file(self, old_name: str, new_name: str) -> tuple[bool, str]:
        source = self.resolve_path(old_name)
        target = source.with_name(new_name.strip().strip('"'))
        try:
            source.rename(target)
            return self._result(True, f"Renamed {source.name} to {target.name}.")
        except FileNotFoundError:
            return self._result(False, f"I couldn't find {source.name}.")
        except OSError as error:
            LOGGER.error("[ERROR] Rename failed: %s", error)
            return self._result(False, "I couldn't rename that file.")

    def copy_file(self, source_name: str, destination: str) -> tuple[bool, str]:
        source = self.resolve_path(source_name)
        target_folder = self.resolve_path(destination)
        try:
            target_folder.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target_folder / source.name)
            return self._result(True, f"Copied {source.name} to {target_folder.name}.")
        except (FileNotFoundError, NotADirectoryError):
            return self._result(False, f"I couldn't find {source.name} or the destination.")
        except OSError as error:
            LOGGER.error("[ERROR] Copy failed: %s", error)
            return self._result(False, "I couldn't copy that file.")

    def move_file(self, source_name: str, destination: str) -> tuple[bool, str]:
        source = self.resolve_path(source_name)
        target_folder = self.resolve_path(destination)
        try:
            target_folder.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target_folder / source.name))
            return self._result(True, f"Moved {source.name} to {target_folder.name}.")
        except (FileNotFoundError, NotADirectoryError):
            return self._result(False, f"I couldn't find {source.name} or the destination.")
        except OSError as error:
            LOGGER.error("[ERROR] Move failed: %s", error)
            return self._result(False, "I couldn't move that file.")

    def delete_file(self, name: str) -> tuple[bool, str]:
        path = self.resolve_path(name)
        try:
            if not path.is_file():
                return self._result(False, f"I couldn't find {path.name}.")
            path.unlink()
            return self._result(True, f"Deleted {path.name}.")
        except OSError as error:
            LOGGER.error("[ERROR] Delete failed: %s", error)
            return self._result(False, "I couldn't delete that file.")

    def list_files(self, folder_name: str) -> tuple[bool, str]:
        folder = self.resolve_path(folder_name)
        if not folder.is_dir():
            return self._result(False, f"I couldn't find {folder.name}.")
        entries = sorted(item.name for item in folder.iterdir())
        if not entries:
            return self._result(True, f"{folder.name} is empty.")
        return self._result(True, f"{folder.name} contains: {', '.join(entries[:20])}.")

    def find_files(self, folder_name: str, extension: str) -> tuple[bool, str]:
        folder = self.resolve_path(folder_name)
        suffix = extension if extension.startswith(".") else f".{extension}"
        matches = list(folder.rglob(f"*{suffix}")) if folder.is_dir() else []
        if not matches:
            return self._result(True, f"I found no {suffix[1:]} files in {folder.name}.")
        names = ', '.join(item.name for item in matches[:20])
        return self._result(True, f"I found {len(matches)} {suffix[1:]} files: {names}.")

    def read_file(self, name: str) -> tuple[bool, str]:
        path = self.resolve_path(name)
        try:
            if path.stat().st_size > 1_000_000:
                return self._result(False, "That file is too large to read aloud.")
            content = path.read_text(encoding="utf-8", errors="replace").strip()
            return self._result(True, content[:3000] if content else f"{path.name} is empty.")
        except (FileNotFoundError, IsADirectoryError):
            return self._result(False, f"I couldn't find {path.name}.")
        except OSError as error:
            LOGGER.error("[ERROR] Read failed: %s", error)
            return self._result(False, "I couldn't read that file.")

    def screenshot(self, name: str = "screenshot.png") -> tuple[bool, str]:
        path = self.desktop / name.strip().strip('"')
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            pyautogui.screenshot().save(path)
            if not path.is_file() or path.stat().st_size == 0:
                return self._result(False, "The screenshot was not saved correctly.")
            return self._result(True, f"Screenshot saved to {path.name}.")
        except (OSError, pyautogui.FailSafeException) as error:
            LOGGER.error("[ERROR] Screenshot failed: %s", error)
            return self._result(False, "I couldn't take the screenshot.")

    def system_info(self, kind: str) -> tuple[bool, str]:
        try:
            if kind == "cpu":
                return self._result(True, f"CPU usage is {psutil.cpu_percent(interval=0.2)} percent.")
            if kind == "ram":
                return self._result(True, f"Memory usage is {psutil.virtual_memory().percent} percent.")
            if kind == "storage":
                disk = psutil.disk_usage(str(self.home.anchor))
                return self._result(True, f"There are {disk.free // (1024 ** 3)} gigabytes free.")
            if kind == "battery":
                battery = psutil.sensors_battery()
                return self._result(True, f"Battery is at {battery.percent} percent." if battery else "Battery information is unavailable.")
            if kind == "operating system":
                return self._result(True, f"You are using {platform.platform()}.")
            if kind == "computer name":
                return self._result(True, f"Your computer name is {platform.node()}.")
            if kind == "ip address":
                return self._result(True, f"Your local IP address is {__import__('socket').gethostbyname(__import__('socket').gethostname())}.")
        except (OSError, ValueError) as error:
            LOGGER.error("[ERROR] System information failed: %s", error)
        return self._result(False, "That system information is unavailable.")

    def clipboard_get(self) -> tuple[bool, str]:
        try:
            value = pyperclip.paste()
            return self._result(True, value[:2000] if value else "The clipboard is empty.")
        except pyperclip.PyperclipException:
            return self._result(False, "The clipboard is unavailable.")

    def clipboard_set(self, value: str) -> tuple[bool, str]:
        try:
            pyperclip.copy(value)
            return self._result(True, "Copied the requested text.")
        except pyperclip.PyperclipException:
            return self._result(False, "I couldn't copy that text.")

    def clipboard_clear(self) -> tuple[bool, str]:
        return self.clipboard_set("")

    def keyboard(self, action: str) -> tuple[bool, str]:
        try:
            if action.startswith("type "):
                pyautogui.write(action[5:], interval=0.01)
            else:
                keys = action.split("+")
                pyautogui.hotkey(*[key.strip() for key in keys]) if len(keys) > 1 else pyautogui.press(keys[0].strip())
            return self._result(True, "Done.")
        except (OSError, pyautogui.FailSafeException) as error:
            LOGGER.error("[ERROR] Keyboard action failed: %s", error)
            return self._result(False, "I couldn't perform that keyboard action.")

    def mouse(self, action: str) -> tuple[bool, str]:
        try:
            if action == "click":
                pyautogui.click()
            elif action == "double click":
                pyautogui.doubleClick()
            elif action == "scroll up":
                pyautogui.scroll(5)
            elif action == "scroll down":
                pyautogui.scroll(-5)
            else:
                return self._result(False, "I don't recognize that mouse action.")
            return self._result(True, "Done.")
        except (OSError, pyautogui.FailSafeException) as error:
            LOGGER.error("[ERROR] Mouse action failed: %s", error)
            return self._result(False, "I couldn't perform that mouse action.")

    def media(self, action: str) -> tuple[bool, str]:
        keys = {"play": "playpause", "pause": "playpause", "resume": "playpause", "next": "nexttrack", "previous": "prevtrack"}
        try:
            pyautogui.press(keys[action])
            return self._result(True, "Done.")
        except (KeyError, OSError, pyautogui.FailSafeException):
            return self._result(False, "I couldn't control the media player.")

    def volume(self, direction: str) -> tuple[bool, str]:
        try:
            pyautogui.press("volumeup" if direction == "up" else "volumedown" if direction == "down" else "volumemute")
            return self._result(True, "Done.")
        except (OSError, pyautogui.FailSafeException):
            return self._result(False, "I couldn't change the volume.")

    def window(self, action: str, target: str = "") -> tuple[bool, str]:
        try:
            if target:
                pyautogui.hotkey("alt", "tab")
            elif action == "minimize":
                pyautogui.hotkey("win", "down")
            elif action == "maximize":
                pyautogui.hotkey("win", "up")
            elif action == "close":
                pyautogui.hotkey("alt", "f4")
            elif action == "switch":
                pyautogui.hotkey("alt", "tab")
            return self._result(True, "Done.")
        except (OSError, pyautogui.FailSafeException):
            return self._result(False, "I couldn't manage that window.")

    def open_settings(self, page: str = "") -> tuple[bool, str]:
        page_map = {"display": "display", "network": "network", "sound": "sound"}
        return self.open_application("settings") if not page else self._open_settings_page(page_map.get(page, ""))

    def _open_settings_page(self, page: str) -> tuple[bool, str]:
        try:
            os.startfile(f"ms-settings:{page}")
            return self._result(True, f"Opened {page} settings.")
        except OSError:
            return self._result(False, "I couldn't open Windows settings.")

    def lock(self) -> tuple[bool, str]:
        try:
            subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
            return self._result(True, "Locking the computer.")
        except OSError:
            return self._result(False, "I couldn't lock the computer.")

    def reminder(self, delay_seconds: int, message: str) -> tuple[bool, str]:
        def notify() -> None:
            try:
                import winsound
                winsound.MessageBeep()
            except (ImportError, RuntimeError):
                pass
            print(f"J.A.R.V.I.S. reminder: {message}")

        timer = threading.Timer(delay_seconds, notify)
        timer.daemon = True
        timer.start()
        self._reminders.append(timer)
        return self._result(True, f"I will remind you in {delay_seconds // 60} minutes to {message}.")

    def run_safe_command(self, command: str) -> tuple[bool, str]:
        safe = re.match(r"^(ipconfig|python(?:\.exe)? --version|node(?:\.exe)? --version|git status|pip list)$", command.strip(), re.IGNORECASE)
        if not safe:
            return self._result(False, "I can only run approved safe terminal commands.")
        try:
            completed = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
            output = (completed.stdout or completed.stderr).strip()
            return self._result(completed.returncode == 0, output[:2000] or "The command returned no output.")
        except (OSError, subprocess.TimeoutExpired) as error:
            LOGGER.error("[ERROR] Terminal command failed: %s", error)
            return self._result(False, "That terminal command failed.")

    def power(self, action: str) -> tuple[bool, str]:
        command = ["shutdown", "/r", "/t", "5"] if action == "restart" else ["shutdown", "/s", "/t", "5"]
        try:
            subprocess.run(command, check=True, capture_output=True)
            return self._result(True, f"{action.title()}ing the computer now.")
        except (OSError, subprocess.CalledProcessError) as error:
            LOGGER.error("[ERROR] Power action failed: %s", error)
            return self._result(False, f"I couldn't {action} the computer.")
