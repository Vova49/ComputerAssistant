import os
import subprocess
import pygame
import pyttsx3
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from config import SOUND_SIGNAL_PATH, KMPLAYER_PATH, DEFAULT_VOLUME

# Инициализация голосового движка
engine = pyttsx3.init()
kmplayer_process = None


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
    """Воспроизводит звуковой сигнал уведомления."""
    try:
        if not os.path.exists(SOUND_SIGNAL_PATH):
            print(f"Файл звукового сигнала не найден: {SOUND_SIGNAL_PATH}")
            return

        pygame.mixer.init()
        pygame.mixer.music.load(SOUND_SIGNAL_PATH)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"Ошибка при воспроизведении звука: {e}")


def speak(text):
    """
    Произносит текст с помощью синтезатора речи.
    
    Args:
        text (str): Текст для произнесения
    """
    try:
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
        speak("Не могу найти плеер KMPlayer.")
        print(f"KMPlayer не найден по пути: {KMPLAYER_PATH}")
        return

    if not os.path.exists(folder_path):
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
            speak(f"Не удалось выключить музыку: {e}")
    else:
        speak("Музыка сейчас не играет.")
