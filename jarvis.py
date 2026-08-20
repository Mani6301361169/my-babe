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

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# print(voices[0].id)

class Jarvis:
    def __init__(self) -> None:
        self.platform = platform

    def wishMe(self) -> None:
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            def _open_url(self, url, message):
                try:
                    if webbrowser.open_new_tab(url):
                        speak(message)
                    else:
                        speak('I could not open the browser.')
                except webbrowser.Error as error:
                    print(f'Browser error: {error}')
                    speak('I could not open the browser.')

            def _launch_application(self, name, command):
                try:
                    executable = shutil.which(command)
                    if executable:
                        subprocess.Popen([executable])
                        speak(f'Opening {name}')
                        return
                    if self.platform == 'win32':
                        subprocess.Popen([command], shell=True)
                        speak(f'Opening {name}')
                        return
                except OSError as error:
                    print(f'Application error: {error}')
                speak(f'I could not open {name}.')

            def execute_query(self, query):
                query = (query or '').strip().lower()
                if not query:
                    return

                try:
                    if 'jarvis are you there' in query or 'hey jarvis' in query:
                        speak('Yes, how can I help?')
                    elif 'open youtube' in query:
                        self._open_url('https://www.youtube.com', 'Opening YouTube')
                    elif 'open google' in query:
                        self._open_url('https://www.google.com', 'Opening Google')
                    elif 'open gmail' in query:
                        self._open_url('https://mail.google.com', 'Opening Gmail')
                    elif 'open github' in query:
                        self._open_url('https://github.com', 'Opening GitHub')
                    elif 'open amazon' in query:
                        self._open_url('https://amazon.com', 'Opening Amazon')
                    elif 'open stackoverflow' in query:
                        self._open_url('https://stackoverflow.com', 'Opening Stack Overflow')
                    elif 'search youtube' in query:
                        search = re.sub(r'^search youtube(?: for)?', '', query).strip()
                        if not search:
                            speak('What should I search for on YouTube?')
                            search = takeCommand()
                        if search:
                            url = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote(search)
                            self._open_url(url, f'Searching YouTube for {search}')
                    elif 'search google' in query or query.startswith('search for '):
                        search = re.sub(r'^(search google|search for)(?: for)?', '', query).strip()
                        if search:
                            url = 'https://www.google.com/search?q=' + urllib.parse.quote(search)
                            self._open_url(url, f'Searching Google for {search}')
                        else:
                            speak('What should I search for?')
                    elif 'open chrome' in query:
                        self._launch_application('Chrome', 'chrome.exe')
                    elif 'open notepad' in query:
                        self._launch_application('Notepad', 'notepad.exe')
                    elif 'open calculator' in query or 'open calc' in query:
                        self._launch_application('Calculator', 'calc.exe')
                    elif 'open vs code' in query or 'open visual studio code' in query or 'open code' in query:
                        self._launch_application('VS Code', 'code')
                    elif 'the time' in query or 'what time' in query:
                        speak('The time is ' + datetime.datetime.now().strftime('%I:%M %p'))
                    elif "today's date" in query or 'todays date' in query or 'what is the date' in query:
                        speak('Today is ' + datetime.datetime.now().strftime('%A, %B %d, %Y'))
                    elif 'shutdown' in query or 'restart' in query:
                        action = 'restart' if 'restart' in query else 'shut down'
                        speak(f'Are you sure you want to {action} the computer?')
                        confirmation = takeCommand().lower()
                        if confirmation in {'yes', 'yes please', 'confirm', 'do it'}:
                            speak(f'{action.capitalize()}ing the computer.')
                            if action == 'restart':
                                os.system('shutdown /r /t 5')
                            else:
                                os.system('shutdown /s /t 5')
                        else:
                            speak('Cancelled.')
                    elif 'weather' in query:
                        weather()
                    elif 'news' in query:
                        try:
                            speak_news()
                        except Exception as error:
                            print(f'News error: {error}')
                            speak('News is currently unavailable.')
                    elif 'wikipedia' in query or 'tell me about' in query:
                        topic = query.replace('wikipedia', '').replace('tell me about', '').strip()
                        if topic:
                            try:
                                speak('Searching Wikipedia.')
                                results = wikipedia.summary(topic, sentences=2)
                                print(results)
                                speak(results)
                            except Exception as error:
                                print(f'Wikipedia error: {error}')
                                speak('I could not find that information.')
                    elif 'your name' in query:
                        speak('My name is JARVIS.')
                    elif 'who made you' in query:
                        speak('I was created by my AI master.')
                    elif 'joke' in query:
                        joke()
                    elif 'cpu' in query:
                        cpu()
                    elif 'screenshot' in query:
                        speak('Taking a screenshot.')
                        screenshot()
                    elif 'sleep' in query or query in {'exit', 'quit', 'goodbye'}:
                        speak('Goodbye.')
                        return False
                    else:
                        speak("I don't know how to perform that command yet.")
                except Exception as error:
                    print(f'Command error: {error}')
                    speak('I could not complete that command, but I am still listening.')
                return True

        elif 'voice' in query:
            if 'female' in query:
                engine.setProperty('voice', voices[0].id)
            else:
                engine.setProperty('voice', voices[1].id)
            speak("Hello Sir, I have switched my voice. How is it?")

        elif 'email to gaurav' in query:
            try:
                speak('What should I say?')
                content = takeCommand()
                to = 'email'
                self.sendEmail(to, content)
                speak('Email has been sent!')

            except Exception as e:
                speak('Sorry sir, Not able to send email at the moment')

    def wishMe(self) -> None:
        hour = datetime.datetime.now().hour
        if hour < 12:
            speak('Good morning, sir.')
        elif hour < 18:
            speak('Good afternoon, sir.')
        else:
            speak('Good evening, sir.')
        weather()
        speak('I am JARVIS. Say hey Jarvis followed by a command.')

    def _open_url(self, url, message):
        try:
            if webbrowser.open_new_tab(url):
                speak(message)
            else:
                speak('I could not open the browser.')
        except webbrowser.Error as error:
            print(f'Browser error: {error}')
            speak('I could not open the browser.')

    def _launch_application(self, name, command):
        try:
            executable = shutil.which(command)
            if executable:
                subprocess.Popen([executable])
                speak(f'Opening {name}')
                return
            if self.platform == 'win32':
                subprocess.Popen([command], shell=True)
                speak(f'Opening {name}')
                return
        except OSError as error:
            print(f'Application error: {error}')
        speak(f'I could not open {name}.')

    def execute_query(self, query):
        query = (query or '').strip().lower()
        if not query:
            return True
        try:
            if 'open youtube' in query:
                self._open_url('https://www.youtube.com', 'Opening YouTube.')
            elif 'open google' in query:
                self._open_url('https://www.google.com', 'Opening Google.')
            elif 'open gmail' in query:
                self._open_url('https://mail.google.com', 'Opening Gmail.')
            elif 'open github' in query:
                self._open_url('https://github.com', 'Opening GitHub.')
            elif 'search youtube' in query:
                search = re.sub(r'^search youtube(?: for)?', '', query).strip()
                if search:
                    url = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote(search)
                    self._open_url(url, f'Searching YouTube for {search}.')
                else:
                    speak('What should I search for on YouTube?')
            elif 'search google' in query or query.startswith('search for '):
                search = re.sub(r'^(search google|search for)(?: for)?', '', query).strip()
                if search:
                    url = 'https://www.google.com/search?q=' + urllib.parse.quote(search)
                    self._open_url(url, f'Searching Google for {search}.')
                else:
                    speak('What should I search for?')
            elif 'open chrome' in query:
                self._launch_application('Chrome', 'chrome.exe')
            elif 'open notepad' in query:
                self._launch_application('Notepad', 'notepad.exe')
            elif 'open calculator' in query or 'open calc' in query:
                self._launch_application('Calculator', 'calc.exe')
            elif 'open vs code' in query or 'open visual studio code' in query or 'open code' in query:
                self._launch_application('VS Code', 'code')
            elif 'the time' in query or 'what time' in query:
                speak('The time is ' + datetime.datetime.now().strftime('%I:%M %p'))
            elif "today's date" in query or 'todays date' in query or 'what is the date' in query:
                speak('Today is ' + datetime.datetime.now().strftime('%A, %B %d, %Y'))
            elif 'shutdown' in query or 'restart' in query:
                action = 'restart' if 'restart' in query else 'shut down'
                speak(f'Are you sure you want to {action} the computer?')
                confirmation = (takeCommand() or '').lower()
                if confirmation in {'yes', 'yes please', 'confirm', 'do it'}:
                    speak(f'{action.capitalize()}ing the computer.')
                    os.system('shutdown /r /t 5' if action == 'restart' else 'shutdown /s /t 5')
                else:
                    speak('Cancelled.')
            elif 'weather' in query:
                weather()
            elif 'news' in query:
                try:
                    speak_news()
                except Exception as error:
                    print(f'News error: {error}')
                    speak('News is currently unavailable.')
            elif 'wikipedia' in query or 'tell me about' in query:
                topic = query.replace('wikipedia', '').replace('tell me about', '').strip()
                if topic:
                    try:
                        results = wikipedia.summary(topic, sentences=2)
                        print(results)
                        speak(results)
                    except Exception as error:
                        print(f'Wikipedia error: {error}')
                        speak('I could not find that information.')
            elif 'your name' in query:
                speak('My name is JARVIS.')
            elif 'who made you' in query:
                speak('I was created by my AI master.')
            elif 'joke' in query:
                joke()
            elif 'cpu' in query:
                cpu()
            elif 'screenshot' in query:
                speak('Taking a screenshot.')
                screenshot()
            elif 'sleep' in query or query in {'exit', 'quit', 'goodbye'}:
                speak('Goodbye.')
                return False
            else:
                speak("I don't know how to perform that command yet.")
        except Exception as error:
            print(f'Command error: {error}')
            speak('I could not complete that command, but I am still listening.')
        return True


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
            command = query

        if bot_.execute_query(command) is False:
            break
               

if __name__ == '__main__':
    
    recognizer = cv2.face.LBPHFaceRecognizer_create() # Local Binary Patterns Histograms
    recognizer.read('./Face-Recognition/trainer/trainer.yml')   #load trained model
    cascadePath = "./Face-Recognition/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath) #initializing haar cascade for object detection approach

    font = cv2.FONT_HERSHEY_SIMPLEX #denotes the font type


    id = 2 #number of persons you want to Recognize


    names = ['','Gaurav']  #names, leave first empty bcz counter starts from 0


    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW) #cv2.CAP_DSHOW to remove warning
    cam.set(3, 640) # set video FrameWidht
    cam.set(4, 480) # set video FrameHeight

    # Define min window size to be recognized as a face
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    # flag = True

    while True:

        ret, img =cam.read() #read the frames using the above created object

        converted_image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)  #The function converts an input image from one color space to another

        faces = faceCascade.detectMultiScale( 
            converted_image,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
        )

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2) #used to draw a rectangle on any image

            id, accuracy = recognizer.predict(converted_image[y:y+h,x:x+w]) #to predict on every single image

            # Check if accuracy is less them 100 ==> "0" is perfect match 
            if (accuracy < 100):
                
                # Do a bit of cleanup
                speak("Optical Face Recognition Done. Welcome")
                cam.release()
                cv2.destroyAllWindows()
                wakeUpJARVIS()
            else:
                speak("Optical Face Recognition Failed")
                break;


    
