import os
import queue
import re
import threading
import time
import tkinter as tk
from datetime import datetime

import speech_recognition as sr
from speech_recognition.exceptions import RequestError

from audio_manager import speak, set_volume, play_music, stop_music
from timer_manager import start_timer_thread, close_timer_by_number, close_all_timers, timer_queue, number_words
from weather_manager import get_current_weather
from video_manager import process_video_command
from utils import parse_time, check_internet, turn_on_radio
from config import (
    DEFAULT_VOLUME, MUSIC_FOLDER,
    TIMER_COMMANDS, CLOSE_ALL_TIMERS_COMMANDS,
    TIME_COMMANDS, WEATHER_COMMANDS,
    RADIO_ON_COMMANDS, RADIO_OFF_COMMANDS
)

def process_timer_command(command):
    """Обрабатывает команды, связанные с таймерами."""
    try:
        if any(word in command for word in TIMER_COMMANDS):
            minutes = parse_time(command)
            if minutes:
                start_timer_thread(minutes)
                speak(f"Таймер поставлен.")
            else:
                speak("Не удалось определить время таймера")

        elif any(word in command for word in CLOSE_ALL_TIMERS_COMMANDS):
            close_all_timers()
            speak("Все таймеры выключены.")

        else:
            match = re.search(r"(закрой|выключи) (\d+|[а-я]+)[^\d]*таймер", command)
            if match:
                number_str = match.group(2)
                timer_number = int(number_str) if number_str.isdigit() else number_words.get(number_str, None)
                if timer_number:
                    if close_timer_by_number(timer_number):
                        speak(f"Таймер {timer_number} закрыт")
                    else:
                        speak(f"Не удалось закрыть таймер {timer_number}")
                else:
                    speak("Не удалось определить номер таймера.")
    except Exception as e:
        print(f"Ошибка при обработке команды таймера: {e}")
        speak("Произошла ошибка при работе с таймером")


def update_timer_ui():
    """Обновляет интерфейс таймеров."""
    try:
        while True:
            try:
                window, new_number = timer_queue.get_nowait()
                for widget in window.winfo_children():
                    if isinstance(widget, tk.Label):
                        widget.config(text=f"Таймер {new_number}")
                        break
            except queue.Empty:
                break
            except Exception as e:
                print(f"Ошибка при обновлении UI таймера: {e}")
                break
    except Exception as e:
        print(f"Ошибка при обработке очереди таймеров: {e}")


def is_command_match(command, command_list):
    """
    Проверяет соответствие команды одному из списка ключевых фраз.
    
    Args:
        command (str): Обрабатываемая команда
        command_list (list): Список ключевых фраз
        
    Returns:
        bool: True если команда соответствует одной из ключевых фраз
    """
    for cmd in command_list:
        if cmd in command:
            return True
    return False


def handle_speech_recognition():
    """Выполняет попытку распознавания речи с обработкой ошибок."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Говорите...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"Вы сказали: {command}")
            return command
        except sr.WaitTimeoutError:
            print("Микрофон не обнаружил звук, жду дальше.")
            return None
        except sr.UnknownValueError:
            print("Не могу распознать, попробуйте снова.")
            return None
        except RequestError:
            print("Ошибка сети. Проверьте интернет и попробуйте снова.")
            return None
        except Exception as e:
            print(f"Произошла ошибка при распознавании: {e}")
            return None


def main():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Ассистент активен")

        # Регулировка уровня окружающего шума
        print("Регулировка уровня шума, пожалуйста, подождите...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Регулировка завершена, можно говорить")

        while True:
            try:
                # Проверяем очередь на наличие обновлений UI
                update_timer_ui()

                # Проверяем подключение к интернету перед началом работы
                if not check_internet():
                    print("Интернет отсутствует, жду подключения...")
                    time.sleep(5)
                    continue

                command = handle_speech_recognition()
                if not command:
                    continue

                # Обработка команд
                if "привет" in command:
                    speak("Привет!")
                elif is_command_match(command, TIME_COMMANDS):
                    speak(f"Сейчас {datetime.now().strftime('%H:%M')}")
                elif "спасибо" in command or "благодарю" in command:
                    speak("Пожалуйста")
                elif "выключи компьютер" in command:
                    speak("Выключаю компьютер")
                    os.system("shutdown /s /t 0")

                # Управление таймерами
                elif "таймер" in command:
                    process_timer_command(command)

                # Управление музыкой
                elif "выключи музыку" in command:
                    stop_music()
                elif "включи музыку" in command:
                    set_volume(DEFAULT_VOLUME)
                    play_music(MUSIC_FOLDER)

                # Управление радио
                elif is_command_match(command, RADIO_ON_COMMANDS):
                    set_volume(DEFAULT_VOLUME)
                    turn_on_radio()
                elif is_command_match(command, RADIO_OFF_COMMANDS):
                    speak("Функция выключения радио еще не реализована")

                # Погода
                elif is_command_match(command, WEATHER_COMMANDS):
                    set_volume(DEFAULT_VOLUME)
                    speak(get_current_weather())

                # Воспроизведение видео
                elif "включи" in command:
                    process_video_command(command)

                else:
                    print("Я вас не понял. Попробуйте снова.")

            except Exception as e:
                print(f"Произошла ошибка: {e}")
                try:
                    speak("Произошла неизвестная ошибка. Попробуйте снова.")
                except:
                    print("Не удалось вывести голосовое сообщение об ошибке")

if __name__ == "__main__":
    set_volume(DEFAULT_VOLUME)
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
