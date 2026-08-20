import pyttsx3
import pyautogui
import psutil
import pyjokes
import speech_recognition as sr
import json
import requests
import geocoder
from difflib import get_close_matches


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
g = geocoder.ip('me')
data = json.load(open('data.json'))

def speak(audio) -> None:
    print(f'J.A.R.V.I.S.: {audio}')
    engine.say(audio)
    engine.runAndWait()

def screenshot() -> None:
    img = pyautogui.screenshot()
    img.save('path of folder you want to save/screenshot.png')

def cpu() -> None:
    usage = str(psutil.cpu_percent())
    speak("CPU is at"+usage)

    battery = psutil.sensors_battery()
    speak("battery is at")
    speak(battery.percent)

def joke() -> None:
    for i in range(5):
        speak(pyjokes.get_jokes()[i])

def takeCommand() -> str:
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print('Listening...')
            r.pause_threshold = 0.8
            r.energy_threshold = 494
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=8)

        print('Recognizing..')
        query = r.recognize_google(audio, language='en-in')
        print(f'You said: {query}\n')
        return query.strip()
    except sr.WaitTimeoutError:
        print('No speech detected.')
    except sr.UnknownValueError:
        print('You said: [unrecognized]')
    except sr.RequestError:
        print('Speech recognition service is unavailable.')
    except (OSError, AttributeError) as error:
        print(f'Microphone error: {error}')
    except Exception as error:
        print(f'Speech input error: {error}')
    return ''

def weather():
    try:
        if not g.latlng:
            raise ValueError('Location unavailable')

        api_url = "https://fcc-weather-api.glitch.me/api/current?lat=" + \
            str(g.latlng[0]) + "&lon=" + str(g.latlng[1])
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data_json = response.json()

        if data_json.get('cod') == 200:
            main = data_json['main']
            wind = data_json['wind']
            weather_desc = data_json['weather'][0]
            speak(str(data_json['coord']['lat']) + ' latitude ' + str(data_json['coord']['lon']) + ' longitude')
            speak('Current location is ' + data_json['name'] + ' ' + data_json['sys']['country'])
            speak('Weather type ' + weather_desc['main'])
            speak('Wind speed is ' + str(wind['speed']) + ' metre per second')
            speak('Temperature: ' + str(main['temp']) + ' degree Celsius')
            speak('Humidity is ' + str(main['humidity']))
        else:
            raise ValueError('Weather service returned an invalid response')
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        print('Weather information is currently unavailable.')
        speak('Weather information is currently unavailable.')


def translate(word):
    word = word.lower()
    if word in data:
        speak(data[word])
    elif len(get_close_matches(word, data.keys())) > 0:
        x = get_close_matches(word, data.keys())[0]
        speak('Did you mean ' + x +
              ' instead,  respond with Yes or No.')
        ans = takeCommand().lower()
        if 'yes' in ans:
            speak(data[x])
        elif 'no' in ans:
            speak("Word doesn't exist. Please make sure you spelled it correctly.")
        else:
            speak("We didn't understand your entry.")

    else:
        speak("Word doesn't exist. Please double check it.")
