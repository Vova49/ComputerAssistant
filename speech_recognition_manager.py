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
        print(f"Ошибка при инициализации микрофона: {e}")
        return False


def wait_for_microphone():
    """Ожидает появления микрофона в системе."""
    while not check_microphone():
        print("Микрофон не обнаружен. Ожидание подключения...")
        try:
            if LANGUAGE == "en":
                speak("Please connect a microphone.")
            else:
                speak("Пожалуйста, подключите микрофон.")
        except:
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
    except (ValueError, OSError, IOError) as e:
        print(f"Ошибка при доступе к микрофону: {e}")
        return None
