import re
import pyautogui
import requests
import time
import keyboard
import pygetwindow as gw
from config import RADIO_BROWSER_TAB


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
    """
    Переключает состояние радио в браузере (включает/выключает).
    Кликает по кнопке плеера, учитывая текущее разрешение экрана.
    """
    try:
        # Ищем окно Chrome
        windows = gw.getWindowsWithTitle("Chrome")
        if not windows:
            print("Chrome не запущен, попытка запустить")
            keyboard.press_and_release('win')
            time.sleep(0.2)
            keyboard.write('chrome')
            time.sleep(0.2)
            keyboard.press_and_release('enter')
            time.sleep(1)
            windows = gw.getWindowsWithTitle("Chrome")  

        if windows:
            # Переходим на окно Chrome
            chrome_window = windows[0]
            chrome_window.activate()
            time.sleep(0.5)  # Ждём, чтобы окно активировалось

            # Нажимаем Ctrl+1 для перехода на первую вкладку
            pyautogui.hotkey('ctrl', '1')
            time.sleep(0.3)

            # Получаем размер экрана
            screen_width, screen_height = pyautogui.size()

            # Рассчитываем координаты в зависимости от разрешения экрана
            # Исходные координаты (821, 177) для экрана 1920x1080
            rel_x = 821 / 1920  # Примерно 0.427
            rel_y = 177 / 1080  # Примерно 0.164

            # Вычисляем абсолютные координаты для текущего разрешения
            click_x = int(screen_width * rel_x)
            click_y = int(screen_height * rel_y)

            # Кликаем по рассчитанным координатам
            pyautogui.click(click_x, click_y)

            print(f"Переключение состояния радио выполнено по координатам {click_x}, {click_y}")
    except Exception as e:
        print(f"Ошибка при управлении радио: {e}")
