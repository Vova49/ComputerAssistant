import os
from datetime import datetime

from audio_manager import speak, set_volume, play_music, stop_music
from config import DEFAULT_VOLUME, MUSIC_FOLDER
from timer_manager import process_timer_command
from utils import toggle_radio
from video_manager import process_video_command
from weather_manager import get_current_weather


def process_greeting_command():
    """Обрабатывает приветствие."""
    speak("Привет!")


def process_time_command():
    """Обрабатывает запрос о времени."""
    speak(f"Сейчас {datetime.now().strftime('%H:%M')}")


def process_thanks_command():
    """Обрабатывает благодарность."""
    speak("Пожалуйста")


def process_system_command(command):
    """Обрабатывает системные команды."""
    if "выключи компьютер" in command:
        speak("Выключаю компьютер")
        os.system("shutdown /s /t 0")


def process_music_command(command):
    """Обрабатывает команды по управлению музыкой."""
    if "выключи музыку" in command:
        stop_music()
    elif "включи музыку" in command:
        set_volume(DEFAULT_VOLUME)
        play_music(MUSIC_FOLDER)


def process_radio_command(command, radio_on_commands, radio_off_commands):
    """Обрабатывает команды по управлению радио."""
    from utils import is_command_match

    if is_command_match(command, radio_on_commands):
        set_volume(DEFAULT_VOLUME)
        speak("Включаю радио")
        toggle_radio()
    elif is_command_match(command, radio_off_commands):
        speak("Выключаю радио")
        toggle_radio()


def process_weather_command():
    """Обрабатывает запрос о погоде."""
    set_volume(DEFAULT_VOLUME)
    speak(get_current_weather())
