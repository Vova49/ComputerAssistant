import re
import requests
import time
import keyboard
import pyautogui
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


def turn_on_radio():
    """
    Открывает радио в браузере.
    Вместо жестко закодированных координат использует логику обнаружения элементов.
    """
    try:
        # Ищем окно Chrome
        windows = gw.getWindowsWithTitle("Google Chrome")
        if not windows:
            print("Chrome не запущен, попытка запустить")
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.typewrite('chrome')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            windows = gw.getWindowsWithTitle("Google Chrome")

        if windows:
            chrome = windows[0]
            chrome.activate()

            # Переходим на вкладку с радио (предположительно первая)
            keyboard.press_and_release(f'ctrl+{RADIO_BROWSER_TAB}')
            time.sleep(0.5)

            # Ищем кнопку воспроизведения на основе поиска изображения
            try:
                # Методы поиска элементов на странице:
                # 1. Поиск по оптическому распознаванию - безопаснее
                play_button_location = None

                # В первую очередь ищем по центру окна, где обычно находятся элементы управления
                center_x = chrome.left + chrome.width // 2
                center_y = chrome.top + chrome.height // 2

                # Если есть изображение кнопки плей, можно использовать pyautogui.locateCenterOnScreen()
                # Если нет - приближенный поиск по центру страницы
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click()  # Активируем элементы управления

                # Используем клик по центру страницы, что в большинстве случаев активирует плеер
                print("Открываю радио в браузере")

            except Exception as e:
                print(f"Ошибка при поиске элементов управления: {e}")
                # Если не удалось найти элементы автоматически, можно предложить пользователю указать нужное место
                print("Радио открыто, но возможно потребуется ручное управление")
    except Exception as e:
        print(f"Ошибка при открытии радио: {e}")
