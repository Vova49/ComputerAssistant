import os
import subprocess
from datetime import datetime

from audio_manager import speak, set_volume, play_music, stop_music
from config import DEFAULT_VOLUME, MUSIC_FOLDER, LANGUAGE
from language_manager import get_commands
from utils import toggle_radio
from weather_manager import get_current_weather


def process_greeting_command():
    """Обрабатывает приветствие."""
    if LANGUAGE == "en":
        speak("Hello!")
    else:
        speak("Привет!")


def process_time_command():
    """Обрабатывает запрос о времени."""
    if LANGUAGE == "en":
        speak(f"It's {datetime.now().strftime('%H:%M')}")
    else:
        speak(f"Сейчас {datetime.now().strftime('%H:%M')}")


def process_thanks_command():
    """Обрабатывает благодарность."""
    if LANGUAGE == "en":
        speak("You're welcome")
    else:
        speak("Пожалуйста")


def process_system_command(command):
    """Обрабатывает системные команды."""
    if LANGUAGE == "en":
        speak("Shutting down the computer")
    else:
        speak("Выключаю компьютер")
    os.system("shutdown /s /t 0")


def process_music_command(command):
    """Обрабатывает команды по управлению музыкой."""
    music_off_commands = get_commands("MUSIC_OFF_COMMANDS")

    if any(cmd in command for cmd in music_off_commands):
        stop_music()
    else:
        set_volume(DEFAULT_VOLUME)
        play_music(MUSIC_FOLDER)


def process_radio_command(command, radio_on_commands, radio_off_commands):
    """Обрабатывает команды по управлению радио."""
    from utils import is_command_match

    if is_command_match(command, radio_on_commands):
        set_volume(DEFAULT_VOLUME)
        if LANGUAGE == "en":
            speak("Turning on radio")
        else:
            speak("Включаю радио")
        toggle_radio()
    elif is_command_match(command, radio_off_commands):
        if LANGUAGE == "en":
            speak("Turning off radio")
        else:
            speak("Выключаю радио")
        toggle_radio()


def process_weather_command():
    """Обрабатывает запрос о погоде."""
    set_volume(DEFAULT_VOLUME)
    speak(get_current_weather())


def process_calculator_command():
    """Открывает системный калькулятор."""
    try:
        if LANGUAGE == "en":
            speak("Opening calculator")
            print("Opening calculator")
        else:
            speak("Открываю калькулятор")
            print("Открываю калькулятор")

        # Запуск калькулятора
        subprocess.Popen("calc.exe")
    except Exception as e:
        if LANGUAGE == "en":
            print(f"Error opening calculator: {e}")
            speak("Could not open calculator")
        else:
            print(f"Ошибка при открытии калькулятора: {e}")
            speak("Не удалось открыть калькулятор")
