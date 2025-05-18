import os
import subprocess
from datetime import datetime

from audio_manager import speak, set_volume, play_music, stop_music
from config import DEFAULT_VOLUME, MUSIC_FOLDER, LANGUAGE, RADIO_VOLUME
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
    """
    Обрабатывает команды по управлению радио.
    
    Args:
        command (str): Команда для обработки
        radio_on_commands (list): Список команд для включения радио
        radio_off_commands (list): Список команд для выключения радио
    """
    from utils import is_command_match

    # Для выключения радио мы ищем и закрываем вкладку с радио
    if is_command_match(command, radio_off_commands):
        if LANGUAGE == "en":
            speak("Turning off radio")
        else:
            speak("Выключаю радио")

        try:
            import keyboard
            import time
            import pygetwindow as gw
            from config import RADIO_TITLE

            # Ищем окно Chrome
            chrome_windows = gw.getWindowsWithTitle("Chrome")
            if chrome_windows:
                # Активируем окно Chrome
                target_window = None
                for window in chrome_windows:
                    if not window.isMinimized:
                        target_window = window
                        break

                # Если все окна свернуты, восстанавливаем первое
                if not target_window and chrome_windows:
                    target_window = chrome_windows[0]
                    if target_window.isMinimized:
                        target_window.restore()
                        time.sleep(1)

                if target_window:
                    # Активируем окно Chrome
                    target_window.activate()
                    time.sleep(1)  # Увеличенная задержка

                    # Проверяем, действительно ли активировалось окно Chrome
                    active_win = gw.getActiveWindow()
                    if not active_win or "Chrome" not in active_win.title:
                        # Альтернативный метод: Alt+Tab
                        keyboard.press('alt')
                        time.sleep(0.5)
                        keyboard.press('tab')
                        time.sleep(0.5)
                        keyboard.release('tab')
                        time.sleep(0.3)
                        keyboard.release('alt')
                        time.sleep(1)

                # Теперь Chrome активен, ищем вкладку с радио
                print("Открываю меню поиска вкладок...")
                keyboard.press('ctrl')
                time.sleep(0.3)
                keyboard.press('shift')
                time.sleep(0.3)
                keyboard.press('a')
                time.sleep(0.3)
                keyboard.release('a')
                time.sleep(0.2)
                keyboard.release('shift')
                time.sleep(0.2)
                keyboard.release('ctrl')

                # Даем больше времени на открытие меню поиска
                time.sleep(1.5)

                # Вводим заголовок радио для поиска
                for char in RADIO_TITLE:
                    keyboard.write(char)
                    time.sleep(0.1)

                # Увеличиваем время ожидания результатов поиска
                time.sleep(2)

                # Нажимаем Enter для выбора найденной вкладки
                keyboard.press_and_release('enter')
                time.sleep(1.5)

                # Закрываем найденную вкладку
                keyboard.press('ctrl')
                time.sleep(0.3)
                keyboard.press('w')
                time.sleep(0.3)
                keyboard.release('w')
                time.sleep(0.2)
                keyboard.release('ctrl')

                print(f"Закрыта вкладка с радио {RADIO_TITLE}")
                return True
            else:
                print("Chrome не найден, не удалось закрыть радио")
                return False

        except Exception as e:
            print(f"Ошибка при закрытии вкладки радио: {e}")
            # Запасной вариант - просто пытаемся закрыть текущую вкладку
            try:
                import keyboard
                keyboard.press('ctrl')
                time.sleep(0.3)
                keyboard.press('w')
                time.sleep(0.3)
                keyboard.release('w')
                time.sleep(0.2)
                keyboard.release('ctrl')
                return True
            except Exception as e2:
                print(f"Ошибка при запасном закрытии вкладки: {e2}")
                return False

    # Для включения радио устанавливаем громкость и открываем поиск
    elif is_command_match(command, radio_on_commands):
        set_volume(RADIO_VOLUME)
        if LANGUAGE == "en":
            speak("Turning on radio")
        else:
            speak("Включаю радио")
        return toggle_radio()


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
