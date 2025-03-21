import time
import speech_recognition as sr
from speech_recognition.exceptions import RequestError

from audio_manager import speak


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
            speak("Микрофон не обнаружен. Пожалуйста, подключите микрофон.")
        except:
            print("Не удалось вывести голосовое сообщение")
        time.sleep(5)

    try:
        speak("Микрофон обнаружен.")
    except:
        pass


def handle_speech_recognition():
    """Выполняет попытку распознавания речи с обработкой ошибок."""
    recognizer = sr.Recognizer()
    try:
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
    except (ValueError, OSError, IOError) as e:
        print(f"Ошибка при доступе к микрофону: {e}")
        return None
