import os
import re
import sys
import time

import keyboard
import pyautogui
import pygetwindow as gw
import requests

# Глобальная переменная для отслеживания первого запуска радио в текущей сессии
_is_first_radio_launch = True

def get_application_path():
    """
    Возвращает путь к папке, в которой находится приложение.
    Работает как для запуска из .py файла, так и для скомпилированного .exe
    
    Returns:
        str: Абсолютный путь к папке приложения
    """
    if getattr(sys, 'frozen', False):
        # Если приложение скомпилировано (exe)
        application_path = os.path.dirname(sys.executable)
    else:
        # Если приложение запущено как скрипт
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path


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


def parse_time(command):
    """
    Анализирует команду и извлекает значение времени.
    
    Args:
        command (str): Команда для анализа
        
    Returns:
        int: Общее количество секунд или None, если не удалось распознать
    """
    try:
        # Импортируем LANGUAGE здесь, чтобы избежать круговой импортации
        from config import LANGUAGE
        
        if LANGUAGE == "en":
            # Шаблон для английского языка
            time_parts = re.findall(r"(\d+)\s*(hour[s]?|minute[s]?|second[s]?)?", command)
            total_seconds = 0

            for value, unit in time_parts:
                value = int(value)
                if not unit or unit.strip() == "":
                    total_seconds += value * 60  # По умолчанию считаем минуты
                elif "hour" in unit:
                    total_seconds += value * 3600
                elif "minute" in unit:
                    total_seconds += value * 60
                elif "second" in unit:
                    total_seconds += value
        else:
            # Шаблон для русского языка
            time_parts = re.findall(r"(\d+)\s*(час[а-я]*|минут[а-я]*|секунд[а-я]*)?", command)
            total_seconds = 0

            for value, unit in time_parts:
                value = int(value)
                if not unit or unit.strip() == "":
                    total_seconds += value * 60  # По умолчанию считаем минуты
                elif "час" in unit:
                    total_seconds += value * 3600
                elif "минут" in unit or "минута" in unit:
                    total_seconds += value * 60
                elif "секунд" in unit or "секунда" in unit:
                    total_seconds += value

        return total_seconds if total_seconds > 0 else None
    except ValueError:
        return None


def check_internet():
    """ Проверяет наличие интернета, делая запрос к Google. """
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False


def try_click_radio():
    try:
        # Определяем текущее разрешение экрана
        screen_width, screen_height = pyautogui.size()

        # Вычисляем координаты кнопки в зависимости от разрешения
        x_rel, y_rel = 0.435, 0.156
        x_pos = int(screen_width * x_rel)
        y_pos = int(screen_height * y_rel)

        # Даем время на полную загрузку страницы
        time.sleep(1)

        # Выполняем клик
        pyautogui.click(x_pos, y_pos)
        print(f"Выполнен клик по координатам ({x_pos}, {y_pos}) на экране {screen_width}x{screen_height}")
        return True
    except Exception as e:
        print(f"Ошибка при попытке клика: {e}")
        return False


def toggle_radio():
    """
    Улучшенная функция для управления радио.
    Находит вкладку с радио по заголовку и переключается на неё.
    """
    # Импортируем настройки радио и языка
    from config import RADIO_TITLE
    global _is_first_radio_launch

    print(f"Начинаем процесс управления радио...")
    
    # Проверка, запущен ли Chrome
    chrome_running = False
    chrome_windows = []
    try:
        chrome_windows = gw.getWindowsWithTitle("Chrome")
        chrome_running = len(chrome_windows) > 0
    except Exception as e:
        print(f"Ошибка при проверке запущенного Chrome: {e}")

    # Если Chrome не запущен, сообщаем об ошибке
    if not chrome_running:
        print("Chrome не запущен. Пожалуйста, запустите Chrome и откройте вкладку с радио.")
        return False

    # Chrome запущен, активируем и обрабатываем окно
    try:
        print("Попытка активации Chrome...")

        # Сначала пробуем переключиться через Alt+Tab
        print("Использую Alt+Tab для переключения на Chrome...")
        keyboard.press('alt')
        time.sleep(0.3)  # Увеличенная задержка
        keyboard.press('tab')
        time.sleep(0.3)  # Увеличенная задержка
        keyboard.release('tab')
        time.sleep(0.3)
        keyboard.release('alt')
        time.sleep(0.5)  # Увеличенная задержка для завершения анимации

        # Проверяем, переключились ли мы на Chrome
        active_window = gw.getActiveWindow()
        if not active_window or "Chrome" not in active_window.title:
            print("Первая попытка переключения не удалась, пробуем еще раз...")

            # Находим подходящее окно Chrome
            target_window = None
            for window in chrome_windows:
                if not window.isMinimized:
                    target_window = window
                    break

            # Если все окна свернуты, восстанавливаем первое
            if not target_window and chrome_windows:
                target_window = chrome_windows[0]
                print(f"Восстанавливаем свернутое окно Chrome...")
                try:
                    target_window.restore()
                    time.sleep(0.5)  # Увеличенная задержка
                except Exception as e:
                    print(f"Ошибка при восстановлении окна: {e}")
                    return False

            if target_window:
                # Пробуем активировать окно
                try:
                    target_window.activate()
                    time.sleep(0.5)  # Увеличенная задержка

                    # Еще раз пробуем Alt+Tab если активация не сработала
                    active_win = gw.getActiveWindow()
                    if not active_win or "Chrome" not in active_win.title:
                        keyboard.press('alt')
                        time.sleep(0.3)
                        keyboard.press('tab')
                        time.sleep(0.3)
                        keyboard.release('tab')
                        time.sleep(0.3)
                        keyboard.release('alt')
                        time.sleep(0.3)
                except Exception as e:
                    print(f"Ошибка при активации окна: {e}")
                    return False

        # Финальная проверка активации Chrome
        active_window = gw.getActiveWindow()
        if not active_window or "Chrome" not in active_window.title:
            print("Не удалось активировать Chrome после всех попыток")
            return False

        print(f"Chrome успешно активирован: {active_window.title}")

        # Даем дополнительное время на полную активацию Chrome
        time.sleep(1)

        # Ищем вкладку с радио
        try:
            print("Открываю меню поиска вкладок (Ctrl+Shift+A)...")

            # Используем более надежный метод нажатия клавиш через keyboard
            keyboard.press('ctrl')
            time.sleep(0.3)  # Увеличенные задержки
            keyboard.press('shift')
            time.sleep(0.3)
            keyboard.press('a')
            time.sleep(0.3)
            keyboard.release('a')
            time.sleep(0.3)
            keyboard.release('shift')
            time.sleep(0.3)
            keyboard.release('ctrl')

            # Увеличенное время на открытие меню поиска вкладок
            time.sleep(1)

            print(f"Ввожу текст для поиска: {RADIO_TITLE}")
            # Печатаем текст с задержкой для надежности
            for char in RADIO_TITLE:
                keyboard.write(char)
                time.sleep(0.1)  # Увеличенная задержка между символами

            # Увеличенное время ожидания результатов поиска
            time.sleep(0.3)

            print("Нажимаю Enter для выбора найденной вкладки...")
            keyboard.press_and_release('enter')
            time.sleep(0.5)  # Даем время на переключение вкладки

            # Проверяем, первый ли это запуск радио в текущей сессии
            if not _is_first_radio_launch:
                # Пытаемся кликнуть по кнопке воспроизведения только если это не первый запуск
                try_click_radio()
            else:
                print("Первый запуск радио в этой сессии, пропускаем автоматический клик")
                _is_first_radio_launch = False

            return True
            
        except Exception as e:
            print(f"Ошибка при работе с вкладками Chrome: {e}")
            return False

    except Exception as e:
        print(f"Общая ошибка при управлении радио: {e}")
        return False
