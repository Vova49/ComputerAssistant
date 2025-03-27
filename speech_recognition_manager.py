import time

import speech_recognition as sr
from speech_recognition.exceptions import RequestError

from audio_manager import speak
from config import LANGUAGE


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


def handle_speech_recognition():
    """Выполняет попытку распознавания речи с обработкой ошибок."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            if LANGUAGE == "en":
                print("Speak...")
            else:
                print("Говорите...")
            try:
                audio = recognizer.listen(source, timeout=5)

                # Выбираем язык распознавания в зависимости от настроек
                lang = "en-US" if LANGUAGE == "en" else "ru-RU"

                command = recognizer.recognize_google(audio, language=lang).lower()

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
