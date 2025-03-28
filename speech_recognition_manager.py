import time

import speech_recognition as sr
from speech_recognition.exceptions import RequestError

from audio_manager import speak
from config import LANGUAGE, SPEECH_ENERGY_THRESHOLD, SPEECH_PAUSE_THRESHOLD, SPEECH_RECOGNITION_TIMEOUT


def check_microphone():
    """Проверяет наличие микрофона в системе."""
    try:
        # Попытка создать микрофон - если микрофона нет, вызовет исключение
        with sr.Microphone() as source:
            return True
    except (ValueError, OSError, IOError) as e:
        if LANGUAGE == "en":
            print(f"Microphone initialization error: {e}")
        else:
            print(f"Ошибка при инициализации микрофона: {e}")
        return False


def wait_for_microphone():
    """Ожидает появления микрофона в системе."""
    while not check_microphone():
        if LANGUAGE == "en":
            print("Microphone not detected. Waiting for connection...")
        else:
            print("Микрофон не обнаружен. Ожидание подключения...")
        try:
            if LANGUAGE == "en":
                speak("Please connect a microphone.")
            else:
                speak("Пожалуйста, подключите микрофон.")
        except:
            if LANGUAGE == "en":
                print("Failed to output voice message")
            else:
                print("Не удалось вывести голосовое сообщение")
        time.sleep(5)


# Создаем один экземпляр распознавателя для повторного использования
_recognizer = sr.Recognizer()
_recognizer.energy_threshold = SPEECH_ENERGY_THRESHOLD  # Настраиваем чувствительность
_recognizer.pause_threshold = SPEECH_PAUSE_THRESHOLD  # Уменьшаем время паузы для более быстрой реакции
_recognizer.dynamic_energy_threshold = True  # Включаем динамическую настройку порога энергии


def handle_speech_recognition():
    """Выполняет попытку распознавания речи с обработкой ошибок и оптимизированной скоростью."""
    global _recognizer
    
    try:
        with sr.Microphone() as source:
            if LANGUAGE == "en":
                print("Speak...")
            else:
                print("Говорите...")

            try:
                # Используем предварительную настройку для шумоподавления
                # только при первом вызове для ускорения работы
                if not hasattr(handle_speech_recognition, 'adjusted'):
                    _recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    handle_speech_recognition.adjusted = True

                # Уменьшенное время ожидания для более быстрой реакции
                audio = _recognizer.listen(source, timeout=SPEECH_RECOGNITION_TIMEOUT)

                # Выбираем язык распознавания в зависимости от настроек
                lang = "en-US" if LANGUAGE == "en" else "ru-RU"

                # Добавляем показатель уверенности для более точных результатов
                command = _recognizer.recognize_google(
                    audio,
                    language=lang,
                    show_all=False  # Для более быстрой обработки
                ).lower()

                if LANGUAGE == "en":
                    print(f"You said: {command}")
                else:
                    print(f"Вы сказали: {command}")
                    
                return command
            except sr.WaitTimeoutError:
                if LANGUAGE == "en":
                    print("No sound detected, continuing to wait.")
                else:
                    print("Микрофон не обнаружил звук, жду дальше.")
                return None
            except sr.UnknownValueError:
                if LANGUAGE == "en":
                    print("Can't recognize, please try again.")
                else:
                    print("Не могу распознать, попробуйте снова.")
                return None
            except RequestError:
                if LANGUAGE == "en":
                    print("Network error. Check your internet connection and try again.")
                else:
                    print("Ошибка сети. Проверьте интернет и попробуйте снова.")
                return None
            except Exception as e:
                if LANGUAGE == "en":
                    print(f"Recognition error: {e}")
                else:
                    print(f"Произошла ошибка при распознавании: {e}")
                return None
    except (ValueError, OSError, IOError) as e:
        if LANGUAGE == "en":
            print(f"Microphone access error: {e}")
        else:
            print(f"Ошибка при доступе к микрофону: {e}")
        return None
