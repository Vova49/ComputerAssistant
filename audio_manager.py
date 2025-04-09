import os
import subprocess

import pygame
import pyttsx3
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from config import SOUND_SIGNAL_PATH, KMPLAYER_PATH, DEFAULT_VOLUME, LANGUAGE, SPEECH_RATE, VOICE_VOLUME, PYGAME_BUFFER

# Инициализация голосового движка с оптимизированными параметрами
engine = pyttsx3.init()
engine.setProperty('rate', SPEECH_RATE)  # Устанавливаем оптимальную скорость речи
engine.setProperty('volume', VOICE_VOLUME)  # Устанавливаем оптимальную громкость речи

# Предварительная инициализация pygame для ускорения воспроизведения звука
pygame.mixer.pre_init(44100, -16, 2, PYGAME_BUFFER)
pygame.mixer.init()

kmplayer_process = None

# Флаг для предотвращения автоматического воспроизведения звука при запуске
is_first_start = True


def ensure_sound_on():
    """Проверяет, что звук включен, и включает его при необходимости."""
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        volume = interface.QueryInterface(IAudioEndpointVolume)

        mute = volume.GetMute()
        if mute:
            volume.SetMute(0, None)
            print("Звук был отключен. Включаю.")
        else:
            print("Звук уже включен.")

    except Exception as e:
        print(f"Не удалось проверить или включить звук: {e}")


def set_volume(level):
    """
    Устанавливает уровень громкости системы.
    
    Args:
        level (int): Уровень громкости от 0 до 100
    """
    if 0 <= level <= 100:
        try:
            ensure_sound_on()
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume.SetMasterVolumeLevelScalar(level / 100, None)
            print(f"Громкость установлена на {level}%.")
        except Exception as e:
            print(f"Не удалось установить громкость: {e}")
    else:
        print("Уровень громкости должен быть от 0 до 100.")


def play_sound():
    """Воспроизводит звуковой сигнал уведомления с оптимизацией скорости."""
    try:
        global is_first_start

        # Пропускаем первое воспроизведение при запуске программы
        if is_first_start:
            is_first_start = False
            return
            
        if not os.path.exists(SOUND_SIGNAL_PATH):
            print(f"Файл звукового сигнала не найден: {SOUND_SIGNAL_PATH}")
            return

        # Используем уже инициализированный микшер
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, PYGAME_BUFFER)

        # Предварительная загрузка звука для ускорения воспроизведения
        if not hasattr(play_sound, 'sound_loaded'):
            pygame.mixer.music.load(SOUND_SIGNAL_PATH)
            play_sound.sound_loaded = True
            
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Ошибка при воспроизведении звука: {e}")


def speak(text):
    """
    Произносит текст с помощью синтезатора речи с оптимизацией скорости.
    
    Args:
        text (str): Текст для произнесения
    """
    try:
        # Используем кэширование для ускорения поиска голоса
        if not hasattr(speak, 'voice_set'):
            voices = engine.getProperty('voices')
            if LANGUAGE == "en":
                # Ищем английский голос
                for voice in voices:
                    if "english" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            else:
                # Ищем русский голос
                for voice in voices:
                    if "russian" in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            speak.voice_set = True
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Ошибка при произнесении текста: {e}")


def play_music(folder_path):
    """
    Запускает воспроизведение музыки через KMPlayer.
    
    Args:
        folder_path (str): Путь к папке с музыкой
    """
    global kmplayer_process

    # Проверка существования плеера и папки
    if not os.path.exists(KMPLAYER_PATH):
        if LANGUAGE == "en":
            speak("Cannot find KMPlayer.")
        else:
            speak("Не могу найти плеер KMPlayer.")
        print(f"KMPlayer не найден по пути: {KMPLAYER_PATH}")
        return

    if not os.path.exists(folder_path):
        if LANGUAGE == "en":
            speak("Cannot find music folder.")
        else:
            speak("Не могу найти папку с музыкой.")
        print(f"Папка с музыкой не найдена: {folder_path}")
        return

    try:
        # Проверяем, не запущен ли уже плеер
        if kmplayer_process and kmplayer_process.poll() is None:
            print("KMPlayer уже запущен")
        else:
            set_volume(DEFAULT_VOLUME)
            kmplayer_process = subprocess.Popen([KMPLAYER_PATH, folder_path])
            print(f"Включаю музыку из папки: {folder_path}")
    except Exception as e:
        print(f"Произошла ошибка при запуске плеера: {e}")
        if LANGUAGE == "en":
            speak("Could not start the player.")
        else:
            speak("Не удалось запустить плеер.")


def stop_music():
    """Останавливает воспроизведение музыки."""
    global kmplayer_process
    if kmplayer_process:
        try:
            kmplayer_process.terminate()
            kmplayer_process = None
            print("Музыка выключена.")
        except Exception as e:
            if LANGUAGE == "en":
                speak(f"Could not stop music: {e}")
            else:
                speak(f"Не удалось выключить музыку: {e}")
    else:
        if LANGUAGE == "en":
            speak("Music is not playing now.")
        else:
            speak("Музыка сейчас не играет.")
