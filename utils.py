import re
import time

import keyboard
import pyautogui
import pygetwindow as gw
import requests


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
    try:
        time_parts = re.findall(r"(\d+)\s*(час[а-я]*|минут[а-я]*|секунд[а-я]*)?", command)
        total_seconds = 0

        for value, unit in time_parts:
            value = int(value)
            if not unit or unit.strip() == "":
                total_seconds += value * 60
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


def toggle_radio():
    windows = gw.getWindowsWithTitle("Chrome")  # Ищем окна с "Chrome" в заголовке
    if windows:
        win = windows[0]  # Берем первое найденное окно
        win.activate()  # Переключаемся на него
        time.sleep(0.5)  # Задержка для корректного переключения
        pyautogui.hotkey("ctrl", "1")  # Нажимаем Ctrl+1

        time.sleep(0.5)  # Ждем после переключения вкладки

        # Определяем текущее разрешение экрана
        screen_width, screen_height = pyautogui.size()

        # Вычисляем координаты кнопки в зависимости от разрешения
        # Используем относительные координаты (примерно 43.5% ширины и 15.6% высоты)
        x_rel, y_rel = 0.435, 0.156

        # Вычисляем абсолютные координаты для текущего разрешения
        x_pos = int(screen_width * x_rel)
        y_pos = int(screen_height * y_rel)

        # Выполняем клик
        pyautogui.click(x_pos, y_pos)
        print(f"Выполнен клик по координатам ({x_pos}, {y_pos}) на экране {screen_width}x{screen_height}")
    else:
        print("Chrome не найден. Запускаем Chrome...")
        keyboard.press_and_release('win')
        time.sleep(0.2)
        keyboard.write('chrome')
        time.sleep(0.2)
        keyboard.press_and_release('enter')
        time.sleep(2)  # Ждем запуска Chrome

        # Повторно пробуем найти окно и кликнуть
        windows = gw.getWindowsWithTitle("Chrome")
        if windows:
            win = windows[0]
            win.activate()
            time.sleep(0.5)
            pyautogui.hotkey("ctrl", "1")
            time.sleep(0.5)

            # Определяем текущее разрешение экрана
            screen_width, screen_height = pyautogui.size()

            # Вычисляем координаты кнопки в зависимости от разрешения
            x_rel, y_rel = 0.435, 0.156
            x_pos = int(screen_width * x_rel)
            y_pos = int(screen_height * y_rel)

            pyautogui.click(x_pos, y_pos)
            print(f"Выполнен клик по координатам ({x_pos}, {y_pos}) на экране {screen_width}x{screen_height}")
        else:
            print("Не удалось найти Chrome даже после попытки запуска")
